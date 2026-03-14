"""In-memory job store for human approval workflow."""

import asyncio
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Job:
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "awaiting_approval"  # awaiting_approval | executing | completed | rejected | timed_out
    intermediate: Dict[str, str] = field(default_factory=dict)
    result: Optional[str] = None
    steps_taken: int = 0
    workers_used: list = field(default_factory=list)
    agent_trace: List[Any] = field(default_factory=list)
    resume_event: asyncio.Event = field(default_factory=asyncio.Event)
    approved_override: Optional[str] = None
    _supervisor_task: Optional[asyncio.Task] = field(default=None, repr=False)


# Module-level store — ephemeral (cleared on restart)
job_store: Dict[str, Job] = {}
