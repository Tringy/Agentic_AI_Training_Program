"""Supervisor agent that coordinates specialist agents."""

import asyncio
import json
import time
from typing import Callable, Dict, List, Optional

from agents import AssistantCoachAgent, CoachAgent, FanAgent, JournalistAgent
from prompts import SYNTHESIS_PROMPT


class SupervisorAgent:
    """Orchestrates specialist agents to analyze football matches."""

    def __init__(self, llm_client):
        self.llm = llm_client
        self.journalist = JournalistAgent(llm_client)
        self.coach = CoachAgent(llm_client)
        self.assistant_coach = AssistantCoachAgent(llm_client)
        self.fan = FanAgent(llm_client)

        self.results: Dict[str, str] = {}
        self.trace: List[Dict] = []

    def _build_game_context(
        self,
        game_date: str,
        home_team: str,
        away_team: str,
        home_score: int,
        away_score: int,
        final_score: str,
        review_question: str,
        context: Optional[str] = None,
    ) -> str:
        """Build game context for agents."""
        lines = [
            f"Game Date: {game_date}",
            f"Match: {home_team} vs {away_team}",
            f"Final Score: {final_score} ({home_team} {home_score}-{away_score} {away_team})",
            f"Question: {review_question}",
        ]
        if context:
            lines.append(f"Additional Context: {context}")
        return "\n".join(lines)

    async def orchestrate(
        self,
        game_context: str,
        agent_tokens: int = 256,
        synthesis_tokens: int = 512,
        synthesis_prompt: Optional[str] = None,
        depth: str = "standard",
        report_format: str = "standard",
        max_iterations: int = 4,
        agent_timeout_seconds: int = 60,
        synthesis_timeout_seconds: int = 60,
        focus_question: Optional[str] = None,
        stream_callback: Optional[Callable] = None,
    ) -> str:
        """Sequential iterative orchestration for game review with context building.

        Workflow: Journalist → Coach (sees journalist) → AssistantCoach (sees both) → Fan (sees all three) → Synthesis
        Used for new endpoint-based architecture where game details are pre-provided.
        Returns JSON string with review structure.
        """
        start_time = time.time()
        self.trace = []
        self.results = {}
        agents_used: List[str] = []
        specialist_sequence = [
            ("Journalist", self.journalist, "journalist", "Journalist Perspective"),
            ("Coach", self.coach, "coach", "Coach Perspective"),
            ("AssistantCoach", self.assistant_coach, "assistant_coach", "Assistant Coach Perspective"),
            ("Fan", self.fan, "fan", "Fan Perspective"),
        ]
        effective_iterations = max(1, min(max_iterations, len(specialist_sequence)))
        planned_agents = [agent_name for agent_name, _, _, _ in specialist_sequence[:effective_iterations]]
        planned_steps = planned_agents + ["Synthesis"]

        self.trace.append(
            {
                "iteration": 0,
                "agent": "Supervisor",
                "action": "DELEGATE",
                "content": f"Starting sequential iterative workflow: {' → '.join(planned_steps)}",
                "duration_ms": 0,
            }
        )

        depth_task_map = {
            "brief": "Provide a concise response in 2 short sentences.",
            "standard": "Provide a balanced response in 3-4 sentences.",
            "detailed": "Provide a detailed response in 5-7 sentences with specific match facts and numbers.",
        }
        if focus_question:
            specialist_task = (
                f"Answer this specific question about the match: {focus_question}\n"
                f"Use only the provided match context and prior agent outputs. "
                f"{depth_task_map.get(depth, depth_task_map['standard'])}"
            )
        else:
            specialist_task = depth_task_map.get(depth, depth_task_map["standard"])

        context_sections: List[tuple[str, str]] = []
        agent_metrics: Dict[str, dict] = {}

        for iteration, (agent_name, agent, result_key, section_title) in enumerate(
            specialist_sequence[:effective_iterations],
            start=1,
        ):
            # Emit thinking event
            if stream_callback:
                await stream_callback(
                    {
                        "state": "agent_thinking",
                        "message": f"{agent_name} is analyzing the match...",
                    }
                )

            agent_context = game_context
            if context_sections:
                prior_sections = "\n\n".join(f"{title}:\n{content}" for title, content in context_sections)
                agent_context = f"{game_context}\n\n{prior_sections}"

            try:
                step_start = time.time()
                result, prompt_tokens, completion_tokens = await asyncio.wait_for(
                    asyncio.to_thread(agent.execute_with_tokens, specialist_task, agent_context, agent_tokens),
                    timeout=agent_timeout_seconds,
                )
                duration_ms = round((time.time() - step_start) * 1000)
                agents_used.append(agent_name)
                self.results[result_key] = result
                context_sections.append((section_title, result))

                # Track agent metrics
                agent_metrics[agent_name] = {
                    "duration_ms": duration_ms,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                }

                self.trace.append(
                    {
                        "iteration": iteration,
                        "agent": agent_name,
                        "action": "RESULT",
                        "content": result,
                        "duration_ms": duration_ms,
                    }
                )

                # Emit stream callback for real-time progress
                if stream_callback:
                    await stream_callback(
                        {
                            "state": "agent_working",
                            "agent": agent_name,
                            "message": f"{agent_name} completed analysis",
                        }
                    )
            except asyncio.TimeoutError as exc:
                self.trace.append(
                    {
                        "iteration": iteration,
                        "agent": agent_name,
                        "action": "ERROR",
                        "content": f"{agent_name} timed out after {agent_timeout_seconds} seconds",
                        "duration_ms": 0,
                    }
                )
                raise ValueError(f"AGENT_TIMEOUT: {agent_name}") from exc

        synthesis_sections = "\n\n".join(f"{title}:\n{content}" for title, content in context_sections)
        synthesis_context = (
            game_context
            if not synthesis_sections
            else f"""
{game_context}

Specialist Analyses:

{synthesis_sections}
"""
        )

        if focus_question:
            synthesis_task = (
                f"Answer this specific follow-up question about the match: {focus_question}. "
                f"Use the specialist analyses to produce a {report_format} response at {depth} depth. "
                "Make every field directly relevant to the question. "
                "Set summary to the direct answer, key_moments to relevant evidence, tactical_analysis to the tactical reasoning if relevant, "
                "performance_insights to player/team evidence if relevant, fan_perspective to an emotional angle if relevant, and final_verdict to a concise conclusion."
            )
        else:
            synthesis_task = (
                f"Synthesize these specialist analyses into a {report_format} review format "
                f"at {depth} depth with fields: summary, key_moments, tactical_analysis, "
                "performance_insights, fan_perspective, and final_verdict."
            )

        selected_synthesis_prompt = synthesis_prompt or SYNTHESIS_PROMPT

        try:
            synthesis_start = time.time()
            synthesis_response, synthesis_prompt_tokens, synthesis_completion_tokens = await asyncio.wait_for(
                asyncio.to_thread(
                    self.llm.chat_json_with_tokens,
                    selected_synthesis_prompt,
                    synthesis_context + "\n\nTask: " + synthesis_task,
                    synthesis_tokens,
                ),
                timeout=synthesis_timeout_seconds,
            )
            synthesis_duration_ms = round((time.time() - synthesis_start) * 1000)

            # Track synthesis metrics
            agent_metrics["Synthesis"] = {
                "duration_ms": synthesis_duration_ms,
                "prompt_tokens": synthesis_prompt_tokens,
                "completion_tokens": synthesis_completion_tokens,
                "total_tokens": synthesis_prompt_tokens + synthesis_completion_tokens,
            }
        except asyncio.TimeoutError as exc:
            self.trace.append(
                {
                    "iteration": 5,
                    "agent": "Supervisor",
                    "action": "ERROR",
                    "content": f"Synthesis timed out after {synthesis_timeout_seconds} seconds",
                    "duration_ms": 0,
                }
            )
            raise ValueError("AGENT_TIMEOUT: Synthesis") from exc
        except (json.JSONDecodeError, ValueError):
            synthesis_response = {
                "summary": "Game analysis completed",
                "key_moments": ["Analysis complete"],
                "tactical_analysis": self.results.get("coach", "")[:200],
                "performance_insights": self.results.get("assistant_coach", "")[:200],
                "fan_perspective": self.results.get("fan", "")[:200],
                "final_verdict": "Review finished",
            }
            synthesis_duration_ms = 1

            # Track synthesis metrics even on partial failure
            agent_metrics["Synthesis"] = {
                "duration_ms": synthesis_duration_ms,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            }

        duration = round(time.time() - start_time, 2)

        self.trace.append(
            {
                "iteration": effective_iterations + 1,
                "agent": "Supervisor",
                "action": "SYNTHESIS",
                "content": "Final review synthesized from all specialist perspectives.",
                "duration_ms": synthesis_duration_ms,
            }
        )

        # Emit stream callback for synthesis completion
        if stream_callback:
            await stream_callback(
                {
                    "state": "agent_working",
                    "agent": "Synthesis",
                    "message": "Synthesizing all specialist perspectives...",
                }
            )

        agent_timings: Dict[str, int] = {}
        for entry in self.trace:
            if entry["action"] == "RESULT":
                agent_timings[entry["agent"]] = entry["duration_ms"]
            elif entry["action"] == "SYNTHESIS":
                agent_timings["Synthesis"] = entry["duration_ms"]

        # Compute aggregate token totals
        total_prompt_tokens = sum(m.get("prompt_tokens", 0) for m in agent_metrics.values())
        total_completion_tokens = sum(m.get("completion_tokens", 0) for m in agent_metrics.values())
        total_tokens = sum(m.get("total_tokens", 0) for m in agent_metrics.values())

        progress = {
            "status": "complete",
            "total_steps": len(planned_steps),
            "completed_steps": len(planned_steps),
            "percent_complete": 100,
            "current_step": "complete",
            "planned_steps": planned_steps,
            "completed_steps_labels": planned_steps,
            "max_iterations": effective_iterations,
        }

        return json.dumps(
            {
                **synthesis_response,
                "specialist_perspectives": {key: value for key, value in self.results.items()},
                "iterations": len(agents_used),
                "max_iterations": effective_iterations,
                "agents_used": agents_used,
                "duration_seconds": duration,
                "agent_timings": agent_timings,
                "agent_metrics": agent_metrics,
                "total_prompt_tokens": total_prompt_tokens,
                "total_completion_tokens": total_completion_tokens,
                "total_tokens": total_tokens,
                "conversation_history": self.trace,
                "progress": progress,
            }
        )

    async def run(
        self,
        game_date: str,
        home_team: str,
        away_team: str,
        home_score: int,
        away_score: int,
        final_score: str,
        review_question: str,
        context: Optional[str] = None,
    ) -> Dict:
        """Orchestrate agents to produce comprehensive game review."""
        start_time = time.time()

        game_context = self._build_game_context(
            game_date,
            home_team,
            away_team,
            home_score,
            away_score,
            final_score,
            review_question,
            context,
        )

        # Add supervisor trace
        self.trace.append(
            {
                "iteration": 0,
                "agent": "Supervisor",
                "action": "DELEGATE",
                "content": f"Analyzing {home_team} vs {away_team} match...",
            }
        )

        # Delegate to all specialist agents in parallel
        try:
            journalist_task = asyncio.create_task(asyncio.to_thread(self.journalist.execute, review_question, game_context))
            coach_task = asyncio.create_task(asyncio.to_thread(self.coach.execute, review_question, game_context))
            assistant_task = asyncio.create_task(asyncio.to_thread(self.assistant_coach.execute, review_question, game_context))
            fan_task = asyncio.create_task(asyncio.to_thread(self.fan.execute, review_question, game_context))

            journalist_result = await asyncio.wait_for(journalist_task, timeout=60)
            coach_result = await asyncio.wait_for(coach_task, timeout=60)
            assistant_result = await asyncio.wait_for(assistant_task, timeout=60)
            fan_result = await asyncio.wait_for(fan_task, timeout=60)
        except asyncio.TimeoutError as exc:
            raise ValueError("Agent execution timed out after 60 seconds") from exc

        # Store results
        self.results = {
            "journalist": journalist_result,
            "coach": coach_result,
            "assistant_coach": assistant_result,
            "fan": fan_result,
        }

        # Add agent traces
        for agent_name in ["Journalist", "Coach", "AssistantCoach", "Fan"]:
            self.trace.append(
                {
                    "iteration": 0,
                    "agent": agent_name,
                    "action": "RESULT",
                    "content": self.results[agent_name.lower()].replace("_", "")[:100] + "...",
                }
            )

        # Synthesize results
        synthesis_context = f"""
Game: {home_team} vs {away_team} ({final_score})
Question: {review_question}

Journalist Perspective:
{journalist_result}

Coach Perspective:
{coach_result}

Assistant Coach Perspective:
{assistant_result}

Fan Perspective:
{fan_result}
"""

        synthesis_task = "Synthesize these four specialist analyses into a comprehensive game review."

        try:
            synthesis_response = await asyncio.to_thread(
                self.llm.chat_json,
                SYNTHESIS_PROMPT,
                synthesis_context + "\n\nTask: " + synthesis_task,
            )
        except (json.JSONDecodeError, ValueError):
            # Fallback if JSON parsing fails
            synthesis_response = {
                "summary": f"{home_team} vs {away_team} - Final Score: {final_score}",
                "key_moments": ["Game analysis in progress"],
                "tactical_analysis": coach_result[:200],
                "performance_insights": assistant_result[:200],
                "fan_perspective": fan_result[:200],
                "final_verdict": "Match completed successfully",
            }

        # Add synthesis trace
        self.trace.append(
            {
                "iteration": 1,
                "agent": "Supervisor",
                "action": "SYNTHESIS",
                "content": "Game review synthesized from all specialist perspectives",
            }
        )

        duration = time.time() - start_time

        return {
            "game_review": synthesis_response,
            "specialist_perspectives": {
                "journalist": journalist_result,
                "coach": coach_result,
                "assistant_coach": assistant_result,
                "fan": fan_result,
            },
            "conversation_history": self.trace,
            "metadata": {
                "iterations": len(set(t["iteration"] for t in self.trace)),
                "agents_used": ["Journalist", "Coach", "AssistantCoach", "Fan"],
                "game_info": [home_team, away_team, final_score],
                "duration_seconds": round(duration, 2),
            },
        }
