"""
AI-Powered Code Review Agent

Orchestrates the code review process:
1. Fetch PR details and files
2. Run static analysis
3. Call Claude for AI review
4. Format and post comments
5. Track costs and confidence
"""
import json
import time
import logging
from typing import Dict, Any, List, Optional
import anthropic

from .config import get_settings
from .github_client import GitHubClient
from .code_analyzer import CodeAnalyzer, Finding
from .prompts import SYSTEM_PROMPT, create_review_prompt, format_review_comment

logger = logging.getLogger(__name__)


class ReviewAgent:
    """
    AI-powered code review agent.

    Orchestrates the review process from PR fetch to comment posting.
    """

    def __init__(
        self,
        github_client: GitHubClient,
        anthropic_api_key: str,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize review agent.

        Args:
            github_client: GitHub API client
            anthropic_api_key: Anthropic API key
            config: Optional configuration overrides
        """
        self.github = github_client
        self.anthropic = anthropic.Anthropic(api_key=anthropic_api_key)
        self.analyzer = CodeAnalyzer()
        self.settings = get_settings()

        # Override settings with config if provided
        if config:
            for key, value in config.items():
                if hasattr(self.settings, key):
                    setattr(self.settings, key, value)

        self.total_cost = 0.0
        self.reviews_completed = 0

    def review_pull_request(
        self,
        owner: str,
        repo: str,
        pr_number: int
    ) -> Dict[str, Any]:
        """
        Perform complete review of a pull request.

        Args:
            owner: Repository owner
            repo: Repository name
            pr_number: Pull request number

        Returns:
            Review result with status, cost, and comment URL
        """
        start_time = time.time()

        try:
            logger.info(f"Starting review for {owner}/{repo}#{pr_number}")

            # 1. Fetch PR details
            pr_data = self.github.get_pull_request(owner, repo, pr_number)
            pr_title = pr_data.get("title", "")
            pr_description = pr_data.get("body", "")
            commit_id = pr_data.get("head", {}).get("sha", "")

            logger.info(f"PR Title: {pr_title}")

            # 2. Fetch changed files
            files = self.github.get_pull_request_files(
                owner, repo, pr_number,
                max_files=self.settings.max_files_per_pr
            )

            if not files:
                logger.warning("No files to review")
                return {
                    "status": "skipped",
                    "reason": "No files to review",
                    "cost": 0.0
                }

            logger.info(f"Reviewing {len(files)} files")

            # 3. Run static analysis
            logger.info("Running static analysis...")
            static_analysis = self.analyzer.analyze_pr(files)

            # 4. Prepare context for AI review
            review_context = self._prepare_review_context(
                pr_title, pr_description, files, static_analysis
            )

            # 5. Call Claude for AI review
            logger.info("Calling Claude for AI review...")
            ai_review = self._get_ai_review(review_context)

            # 6. Merge static analysis with AI review
            merged_review = self._merge_reviews(static_analysis, ai_review)

            # 7. Calculate confidence score
            confidence = self._calculate_confidence(merged_review, files)
            merged_review["confidence_score"] = confidence

            # 8. Format comment
            comment = format_review_comment(merged_review)

            # 9. Post comment (if enabled)
            comment_url = None
            if self.settings.auto_comment:
                logger.info("Posting review comment...")
                result = self.github.post_review_comment(
                    owner, repo, pr_number, comment
                )
                comment_url = result.get("html_url")
                logger.info(f"Comment posted: {comment_url}")

            # 10. Track metrics
            elapsed = time.time() - start_time
            self.reviews_completed += 1

            review_result = {
                "status": "completed",
                "pr_number": pr_number,
                "cost": ai_review.get("cost", 0.0),
                "confidence": confidence,
                "issues_found": static_analysis["summary"]["total_issues"],
                "high_severity_count": static_analysis["summary"]["high_severity"],
                "comment_url": comment_url,
                "elapsed_seconds": elapsed,
                "files_reviewed": len(files)
            }

            logger.info(
                f"Review completed in {elapsed:.1f}s. "
                f"Cost: ${ai_review.get('cost', 0):.4f}, "
                f"Issues: {review_result['issues_found']}"
            )

            return review_result

        except Exception as e:
            logger.error(f"Review failed: {str(e)}", exc_info=True)
            return {
                "status": "failed",
                "error": str(e),
                "cost": 0.0,
                "elapsed_seconds": time.time() - start_time
            }

    def _prepare_review_context(
        self,
        pr_title: str,
        pr_description: str,
        files: List[Dict[str, Any]],
        static_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare context for AI review."""
        return {
            "pr_title": pr_title,
            "pr_description": pr_description,
            "files": files,
            "static_analysis": static_analysis
        }

    def _get_ai_review(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get AI-powered review from Claude.

        Args:
            context: Review context with PR and analysis data

        Returns:
            Parsed review data with cost tracking
        """
        # Create prompt
        prompt = create_review_prompt(
            pr_title=context["pr_title"],
            pr_description=context["pr_description"],
            files_changed=context["files"]
        )

        # Add static analysis summary to prompt
        static_summary = context["static_analysis"]["summary"]
        prompt += f"\n\n## Static Analysis Results\n"
        prompt += f"- Total issues: {static_summary['total_issues']}\n"
        prompt += f"- High severity: {static_summary['high_severity']}\n"
        prompt += f"- Medium severity: {static_summary['medium_severity']}\n"
        prompt += f"- Low severity: {static_summary['low_severity']}\n"

        try:
            # Call Claude
            response = self.anthropic.messages.create(
                model=self.settings.model_name,
                max_tokens=self.settings.max_tokens,
                temperature=self.settings.temperature,
                system=SYSTEM_PROMPT,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Extract response
            response_text = response.content[0].text

            # Parse JSON response
            try:
                # Try to extract JSON from markdown code blocks
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    response_text = response_text[json_start:json_end].strip()
                elif "```" in response_text:
                    json_start = response_text.find("```") + 3
                    json_end = response_text.find("```", json_start)
                    response_text = response_text[json_start:json_end].strip()

                review_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON response: {e}")
                # Fallback to basic structure
                review_data = {
                    "summary": response_text[:500],
                    "security_issues": [],
                    "quality_issues": [],
                    "best_practices": [],
                    "positive_feedback": [],
                    "overall_assessment": response_text[:200],
                    "confidence_score": 0.5
                }

            # Calculate cost
            cost = self._calculate_cost(response.usage)
            review_data["cost"] = cost
            self.total_cost += cost

            # Check cost limit
            if cost > self.settings.max_cost_per_review:
                logger.warning(
                    f"Review cost ${cost:.4f} exceeds limit "
                    f"${self.settings.max_cost_per_review:.4f}"
                )

            return review_data

        except anthropic.APIError as e:
            logger.error(f"Anthropic API error: {str(e)}")
            raise

    def _merge_reviews(
        self,
        static_analysis: Dict[str, Any],
        ai_review: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge static analysis findings with AI review.

        Args:
            static_analysis: Static analysis results
            ai_review: AI review results

        Returns:
            Merged review data
        """
        merged = ai_review.copy()

        # Add static analysis findings
        static_findings = static_analysis["findings"]

        # Convert static findings to review format
        for finding in static_findings.get("security", []):
            merged.setdefault("security_issues", []).append({
                "severity": finding.severity.value,
                "file": finding.file,
                "line": finding.line,
                "issue": finding.issue,
                "recommendation": finding.recommendation,
                "source": "static_analysis"
            })

        for finding in static_findings.get("quality", []):
            merged.setdefault("quality_issues", []).append({
                "severity": finding.severity.value,
                "file": finding.file,
                "line": finding.line,
                "issue": finding.issue,
                "recommendation": finding.recommendation,
                "source": "static_analysis"
            })

        for finding in static_findings.get("best_practices", []):
            merged.setdefault("best_practices", []).append({
                "file": finding.file,
                "line": finding.line,
                "suggestion": f"{finding.issue} - {finding.recommendation}",
                "source": "static_analysis"
            })

        # Deduplicate issues (prefer AI review over static)
        merged["security_issues"] = self._deduplicate_issues(
            merged.get("security_issues", [])
        )
        merged["quality_issues"] = self._deduplicate_issues(
            merged.get("quality_issues", [])
        )

        return merged

    def _deduplicate_issues(self, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate issues based on file and line."""
        seen = set()
        unique_issues = []

        for issue in issues:
            key = (issue.get("file"), issue.get("line"), issue.get("issue", "")[:50])
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)

        return unique_issues

    def _calculate_confidence(
        self,
        review: Dict[str, Any],
        files: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate confidence score for the review.

        Based on:
        - Number of files reviewed
        - Completeness of analysis
        - AI's self-reported confidence
        """
        # Start with AI's confidence
        confidence = review.get("confidence_score", 0.7)

        # Adjust based on file count (more files = less confident)
        file_count = len(files)
        if file_count > 15:
            confidence *= 0.8
        elif file_count > 10:
            confidence *= 0.9

        # Check completeness
        has_security = len(review.get("security_issues", [])) > 0
        has_quality = len(review.get("quality_issues", [])) > 0
        has_assessment = bool(review.get("overall_assessment"))

        completeness = sum([has_security, has_quality, has_assessment]) / 3
        confidence = (confidence + completeness) / 2

        return round(min(confidence, 1.0), 2)

    def _calculate_cost(self, usage) -> float:
        """
        Calculate cost based on token usage.

        Args:
            usage: Usage object from Anthropic response

        Returns:
            Cost in USD
        """
        # Claude 3.5 Sonnet pricing (as of 2024)
        input_cost_per_mtok = 3.0
        output_cost_per_mtok = 15.0

        input_cost = (usage.input_tokens / 1_000_000) * input_cost_per_mtok
        output_cost = (usage.output_tokens / 1_000_000) * output_cost_per_mtok

        return input_cost + output_cost

    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        return {
            "reviews_completed": self.reviews_completed,
            "total_cost": round(self.total_cost, 4),
            "average_cost": round(
                self.total_cost / self.reviews_completed if self.reviews_completed > 0 else 0,
                4
            )
        }
