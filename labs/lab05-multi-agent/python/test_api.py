"""Tests for the Multi-Agent System API."""

import asyncio
import os
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

# Point memory DB at a temp dir for all tests
_TMP_DIR = tempfile.mkdtemp()
os.environ.setdefault("DATABASE_PATH", _TMP_DIR)

from fastapi.testclient import TestClient

# Patch LLM init before importing app so no real API key is needed
with patch("llm_client.get_llm_client") as _mock_get_llm:
    _mock_get_llm.return_value = MagicMock()
    import memory_store
    from job_store import Job, job_store
    from main import app

# Initialise the test DB schema
memory_store.init_db()

from agent_registry import AgentDefinition, init_agents_table
from agent_registry import registry as _agent_registry
from agents import RESEARCHER_PROMPT, REVIEWER_PROMPT, WRITER_PROMPT

# Create the agents table so persist=True calls succeed in tests
init_agents_table()

client = TestClient(app)


def _ensure_builtins() -> None:
    """Register built-in agents if they are missing (lifespan doesn't run in TestClient)."""
    builtins = [
        AgentDefinition("Researcher", RESEARCHER_PROMPT, "Finds and summarizes information on a topic", builtin=True),
        AgentDefinition("Writer", WRITER_PROMPT, "Creates polished content from research", builtin=True),
        AgentDefinition("Reviewer", REVIEWER_PROMPT, "Reviews content for quality and accuracy", builtin=True),
    ]
    for defn in builtins:
        if _agent_registry.get(defn.name) is None:
            _agent_registry.register(defn)


def _make_job(**kwargs) -> Job:
    """Create a Job and register it in the in-memory store."""
    job = Job(**kwargs)
    job_store[job.job_id] = job
    return job


# ---------------------------------------------------------------------------
# Core tests
# ---------------------------------------------------------------------------


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_run_task_success():
    mock_agent = MagicMock()
    mock_agent.run_async = AsyncMock(return_value="RAG systems combine retrieval with generation.")
    mock_agent.results = {"Researcher_0": "...", "Writer_1": "..."}

    with patch("main.SupervisorAgent", return_value=mock_agent):
        response = client.post(
            "/run",
            json={"task": "Explain RAG systems", "max_iterations": 3},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["result"] == "RAG systems combine retrieval with generation."
    assert data["steps_taken"] == 2


def test_run_task_empty_task():
    response = client.post("/run", json={"task": "", "max_iterations": 3})
    assert response.status_code == 422


def test_run_task_iterations_below_minimum():
    response = client.post("/run", json={"task": "Explain RAG", "max_iterations": 0})
    assert response.status_code == 422


def test_run_task_iterations_above_maximum():
    response = client.post("/run", json={"task": "Explain RAG", "max_iterations": 11})
    assert response.status_code == 422


def test_run_task_missing_task_field():
    response = client.post("/run", json={"max_iterations": 3})
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Human Approval tests
# ---------------------------------------------------------------------------


def test_run_with_approval_returns_202():
    """GIVEN require_approval=True WHEN POST /run-with-approval THEN 202 + awaiting_approval."""

    async def fake_run(job, agent, task, max_iterations, mem_entries=None):
        job.status = "awaiting_approval"
        job.intermediate = {"Researcher": "Some research findings"}
        await asyncio.Event().wait()  # block until cancelled by reject/timeout

    mock_agent = MagicMock()
    mock_agent.run_async = AsyncMock()

    with patch("main.SupervisorAgent", return_value=mock_agent), patch("main._run_with_timeout", new=fake_run):
        response = client.post(
            "/run-with-approval",
            json={"task": "Write about SOLID principles", "max_iterations": 5},
        )

    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "awaiting_approval"
    assert isinstance(data["intermediate"], dict)


def test_get_job_status():
    """GIVEN a job in job_store WHEN GET /jobs/{id} THEN 200 with all required fields."""
    job = _make_job(status="awaiting_approval", intermediate={"Researcher": "findings"})

    response = client.get(f"/jobs/{job.job_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == job.job_id
    assert data["status"] == "awaiting_approval"
    assert "intermediate" in data
    assert "steps_taken" in data


def test_get_job_not_found():
    """GIVEN unknown job_id WHEN GET /jobs/{id} THEN 404."""
    response = client.get("/jobs/definitely-does-not-exist")
    assert response.status_code == 404


def test_approve_job_without_override():
    """GIVEN awaiting_approval job WHEN POST /approve (no body) THEN 200 + executing."""
    job = _make_job(status="awaiting_approval")

    response = client.post(f"/jobs/{job.job_id}/approve", json={})

    assert response.status_code == 200
    assert response.json()["status"] == "executing"
    assert job.resume_event.is_set()
    assert job.approved_override is None


def test_approve_job_with_override():
    """GIVEN awaiting_approval job WHEN POST /approve with override_task THEN task stored."""
    job = _make_job(status="awaiting_approval")
    override = "Focus only on Python-specific aspects"

    response = client.post(
        f"/jobs/{job.job_id}/approve",
        json={"override_task": override},
    )

    assert response.status_code == 200
    assert job.approved_override == override
    assert job.resume_event.is_set()


def test_reject_job():
    """GIVEN awaiting_approval job WHEN POST /reject THEN 200 + rejected."""
    job = _make_job(status="awaiting_approval")

    response = client.post(f"/jobs/{job.job_id}/reject")

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"
    assert job.status == "rejected"


def test_approve_unknown_job_returns_404():
    """GIVEN unknown job_id WHEN POST /approve THEN 404."""
    response = client.post("/jobs/no-such-job/approve", json={})
    assert response.status_code == 404


def test_reject_unknown_job_returns_404():
    """GIVEN unknown job_id WHEN POST /reject THEN 404."""
    response = client.post("/jobs/no-such-job/reject")
    assert response.status_code == 404


def test_approve_wrong_state_returns_409():
    """GIVEN job already executing WHEN POST /approve THEN 409 conflict."""
    job = _make_job(status="executing")

    response = client.post(f"/jobs/{job.job_id}/approve", json={})
    assert response.status_code == 409


def test_reject_wrong_state_returns_409():
    """GIVEN completed job WHEN POST /reject THEN 409 conflict."""
    job = _make_job(status="completed")

    response = client.post(f"/jobs/{job.job_id}/reject")
    assert response.status_code == 409


# ---------------------------------------------------------------------------
# Memory acceptance criteria tests
# ---------------------------------------------------------------------------


def _clear_memory():
    """Helper: wipe memory table between tests."""
    memory_store.delete_all_memory()


def test_run_no_prior_memory_returns_memory_context_used_false():
    """GIVEN no previous tasks exist WHEN POST /run THEN memory_context_used is false."""
    _clear_memory()

    mock_agent = MagicMock()
    mock_agent.run_async = AsyncMock(return_value="Some result")
    mock_agent.results = {"Researcher_0": "r", "Writer_1": "w"}

    with patch("main.SupervisorAgent", return_value=mock_agent), patch("main._summarise_and_save"):
        response = client.post("/run", json={"task": "Explain ML", "max_iterations": 3})

    assert response.status_code == 200
    assert response.json()["memory_context_used"] is False


def test_run_with_prior_memory_returns_memory_context_used_true():
    """GIVEN one completed task exists WHEN POST /run THEN memory_context_used is true."""
    _clear_memory()
    memory_store.save_memory("Prior task", "A useful summary of prior work.")

    mock_agent = MagicMock()
    mock_agent.run_async = AsyncMock(return_value="New result")
    mock_agent.results = {"Researcher_0": "r", "Writer_1": "w"}

    with patch("main.SupervisorAgent", return_value=mock_agent), patch("main._summarise_and_save"):
        response = client.post("/run", json={"task": "Follow-up task", "max_iterations": 3})

    assert response.status_code == 200
    assert response.json()["memory_context_used"] is True


def test_run_injects_memory_context_into_supervisor():
    """GIVEN prior memory exists WHEN POST /run THEN supervisor receives MEMORY CONTEXT block."""
    _clear_memory()
    memory_store.save_memory("Prior task", "Summary of prior work.")

    captured_kwargs = {}

    async def capture_run(task, max_iterations, memory_entries=None):
        captured_kwargs["memory_entries"] = memory_entries
        return "result"

    mock_agent = MagicMock()
    mock_agent.run_async = capture_run
    mock_agent.results = {}

    with patch("main.SupervisorAgent", return_value=mock_agent), patch("main._summarise_and_save"):
        client.post("/run", json={"task": "New task", "max_iterations": 3})

    assert captured_kwargs.get("memory_entries")
    assert captured_kwargs["memory_entries"][0]["summary"] == "Summary of prior work."


def test_memory_top_k_limits_entries_injected(monkeypatch):
    """GIVEN MEMORY_TOP_K=2 and 5 entries WHEN POST /run THEN only 2 entries injected."""
    _clear_memory()
    for i in range(5):
        memory_store.save_memory(f"Task {i}", f"Summary {i}")

    monkeypatch.setattr("main.MEMORY_TOP_K", 2)

    captured_kwargs = {}

    async def capture_run(task, max_iterations, memory_entries=None):
        captured_kwargs["memory_entries"] = memory_entries
        return "result"

    mock_agent = MagicMock()
    mock_agent.run_async = capture_run
    mock_agent.results = {}

    with patch("main.SupervisorAgent", return_value=mock_agent), patch("main._summarise_and_save"):
        client.post("/run", json={"task": "New task", "max_iterations": 3})

    assert len(captured_kwargs.get("memory_entries", [])) == 2


def test_memory_max_entries_prunes_oldest(monkeypatch):
    """GIVEN MEMORY_MAX_ENTRIES=3 and 3 entries WHEN new task completes THEN still 3 rows."""
    _clear_memory()
    monkeypatch.setattr("memory_store.MEMORY_MAX_ENTRIES", 3)
    for i in range(3):
        memory_store.save_memory(f"Old task {i}", f"Old summary {i}")

    memory_store.save_memory("New task", "New summary")

    entries = memory_store.list_memory()
    assert len(entries) == 3
    tasks = [e["task"] for e in entries]
    assert "New task" in tasks
    assert "Old task 0" not in tasks  # oldest was pruned


def test_get_memory_returns_entries_most_recent_first():
    """GIVEN entries exist WHEN GET /memory THEN ordered by most recent first with required fields."""
    _clear_memory()
    memory_store.save_memory("First task", "First summary")
    memory_store.save_memory("Second task", "Second summary")

    response = client.get("/memory")

    assert response.status_code == 200
    data = response.json()
    assert "entries" in data
    assert "total" in data
    assert data["total"] == 2
    first = data["entries"][0]
    assert first["task"] == "Second task"
    for field in ("id", "task", "summary", "created_at"):
        assert field in first


def test_delete_memory_clears_all_entries():
    """GIVEN entries exist WHEN DELETE /memory THEN GET /memory returns empty."""
    _clear_memory()
    memory_store.save_memory("A task", "A summary")

    del_response = client.delete("/memory")
    assert del_response.status_code == 200
    assert del_response.json()["deleted"] >= 1

    get_response = client.get("/memory")
    data = get_response.json()
    assert data["entries"] == []
    assert data["total"] == 0


def test_summariser_json_decode_error_stores_raw_truncated():
    """GIVEN summariser returns malformed JSON WHEN task completes THEN raw result stored."""
    _clear_memory()

    from main import _summarise_and_save

    with patch("main.llm") as mock_llm:
        mock_llm.chat.return_value = "NOT VALID JSON !!!"
        _summarise_and_save("Test task", "A" * 600)

    entries = memory_store.list_memory()
    assert len(entries) == 1
    # Summary should be the raw result truncated to 500 chars
    assert entries[0]["summary"] == "A" * 500


def test_summariser_failure_does_not_break_post_run():
    """GIVEN summariser raises an exception WHEN POST /run THEN 200 still returned."""
    _clear_memory()

    mock_agent = MagicMock()
    mock_agent.run_async = AsyncMock(return_value="Good result")
    mock_agent.results = {"Researcher_0": "r", "Writer_1": "w"}

    def boom(*_args, **_kwargs):
        raise RuntimeError("LLM down")

    with patch("main.SupervisorAgent", return_value=mock_agent), patch("main.llm") as mock_llm:
        mock_llm.chat.side_effect = boom
        response = client.post("/run", json={"task": "Some task", "max_iterations": 3})

    assert response.status_code == 200
    assert response.json()["result"] == "Good result"


# ---------------------------------------------------------------------------
# Agent Registry tests
# ---------------------------------------------------------------------------


def _reset_registry():
    """Remove any custom agents added during tests, keep/restore builtins."""
    for defn in list(_agent_registry.list()):
        if not defn.builtin:
            try:
                _agent_registry.delete(defn.name)
            except Exception:
                pass
    _ensure_builtins()


def test_get_agents_returns_builtins():
    """GIVEN server starts WHEN GET /agents THEN Researcher, Writer, Reviewer listed as builtin."""
    _reset_registry()
    response = client.get("/agents")
    assert response.status_code == 200
    data = response.json()
    names = {a["name"] for a in data["agents"]}
    assert {"Researcher", "Writer", "Reviewer"}.issubset(names)
    for agent in data["agents"]:
        if agent["name"] in ("Researcher", "Writer", "Reviewer"):
            assert agent["builtin"] is True


def test_post_agents_creates_custom_agent():
    """GIVEN valid POST /agents THEN 201, GET /agents includes new agent."""
    _reset_registry()
    payload = {
        "name": "Editor",
        "system_prompt": "You are an expert editor.",
        "description": "Polishes prose for grammar and clarity",
    }
    response = client.post("/agents", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Editor"
    assert data["builtin"] is False

    list_resp = client.get("/agents")
    names = {a["name"] for a in list_resp.json()["agents"]}
    assert "Editor" in names
    _reset_registry()


def test_post_agents_duplicate_returns_409():
    """GIVEN POST /agents with existing name THEN 409."""
    _reset_registry()
    payload = {"name": "Dupl", "system_prompt": "x", "description": "d"}
    client.post("/agents", json=payload)
    response = client.post("/agents", json=payload)
    assert response.status_code == 409
    _reset_registry()


def test_post_agents_name_with_spaces_returns_422():
    """GIVEN name with spaces WHEN POST /agents THEN 422."""
    response = client.post(
        "/agents",
        json={
            "name": "Bad Name",
            "system_prompt": "x",
            "description": "d",
        },
    )
    assert response.status_code == 422


def test_delete_custom_agent():
    """GIVEN custom agent exists WHEN DELETE /agents/{name} THEN 200 + deleted=true, not in list."""
    _reset_registry()
    client.post("/agents", json={"name": "TempAgent", "system_prompt": "x", "description": "d"})

    response = client.delete("/agents/TempAgent")
    assert response.status_code == 200
    assert response.json()["deleted"] is True

    names = {a["name"] for a in client.get("/agents").json()["agents"]}
    assert "TempAgent" not in names


def test_delete_builtin_agent_returns_403():
    """GIVEN DELETE /agents/Researcher THEN 403."""
    response = client.delete("/agents/Researcher")
    assert response.status_code == 403


def test_delete_unknown_agent_returns_404():
    """GIVEN DELETE /agents/NoSuchAgent THEN 404."""
    response = client.delete("/agents/NoSuchAgent")
    assert response.status_code == 404


def test_supervisor_skips_unknown_agent():
    """GIVEN supervisor delegates to unregistered 'Translator' THEN iteration skipped, run continues."""
    _reset_registry()

    captured_messages = []

    async def fake_run_async(task, max_iterations, job=None, require_approval=False, memory_entries=None):
        # Simulate LLM returning DELEGATE to unknown agent once, then fallback FINAL
        return "final result"

    from agent_registry import registry as _reg
    from supervisor import SupervisorAgent as _Sup

    sup = _Sup.__new__(_Sup)
    sup.llm = MagicMock()
    sup.registry = _reg
    sup.results = {}
    sup.agent_trace = []
    sup._parallel_group = 0

    # LLM returns unknown agent first, then FINAL on second call
    call_count = [0]

    def fake_chat(msgs):
        call_count[0] += 1
        if call_count[0] == 1:
            return "DELEGATE: Translator\nTASK: Translate to French"
        return "FINAL: done"

    sup.llm.chat = fake_chat

    import asyncio as _asyncio

    result = _asyncio.run(sup.run_async("test task", max_iterations=5))
    # run should complete without crashing
    assert result is not None


def test_custom_agent_can_be_delegated_to():
    """GIVEN custom 'Editor' registered WHEN POST /run delegates to it THEN output counted in steps."""
    _reset_registry()
    client.post(
        "/agents",
        json={
            "name": "Editor",
            "system_prompt": "You are an editor.",
            "description": "Edits content",
        },
    )

    mock_agent = MagicMock()
    mock_agent.run_async = AsyncMock(return_value="Edited result")
    mock_agent.results = {"Researcher_0": "r", "Writer_1": "w", "Editor_2": "e"}

    with patch("main.SupervisorAgent", return_value=mock_agent), patch("main._summarise_and_save"):
        response = client.post("/run", json={"task": "Write and edit something", "max_iterations": 5})

    assert response.status_code == 200
    assert response.json()["steps_taken"] == 3
    _reset_registry()
