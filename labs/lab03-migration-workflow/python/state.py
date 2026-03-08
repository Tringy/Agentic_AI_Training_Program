"""Migration Workflow Agent - State Management."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


@dataclass
class Snapshot:
    """Lightweight snapshot of migrated_files taken before a step executes."""

    step_index: int
    step_description: str
    timestamp: str  # ISO-8601
    migrated_files: Dict[str, str]  # deep copy at time of snapshot


@dataclass
class RollbackRecord:
    """Audit entry for a rollback action."""

    timestamp: str  # ISO-8601
    from_step: int
    to_step: int
    reason: str  # "automatic" | "manual"


class Phase(Enum):
    """Migration phases."""

    ANALYSIS = "analysis"
    PLANNING = "planning"
    AWAITING_APPROVAL = "awaiting_approval"
    EXECUTION = "execution"
    VERIFICATION = "verification"
    COMPLETE = "complete"


@dataclass
class MigrationStep:
    """Represents a single migration step."""

    id: int
    description: str
    status: str = "pending"  # pending, in_progress, completed, failed
    input_files: List[str] = field(default_factory=list)
    output_files: List[str] = field(default_factory=list)
    result: Optional[str] = None
    dependencies: List[int] = field(default_factory=list)  # step IDs that must finish first
    wave_index: int = 0  # assigned during execution planning


@dataclass
class MigrationState:
    """State for the migration workflow."""

    source_framework: str
    target_framework: str
    source_files: Dict[str, str]  # filename -> content
    phase: Phase = Phase.ANALYSIS
    analysis: Optional[Dict[str, Any]] = None
    plan: List[MigrationStep] = field(default_factory=list)
    current_step: int = 0
    migrated_files: Dict[str, str] = field(default_factory=dict)
    verification_result: Optional[Dict] = None
    errors: List[str] = field(default_factory=list)
    # Parallel execution
    execution_mode: str = "parallel"  # "parallel" | "sequential"
    waves: List[List[int]] = field(default_factory=list)  # [[step_ids], ...] per wave
    # Human-approval tracking
    job_id: Optional[str] = None
    approved_at: Optional[str] = None  # ISO-8601
    rejected_at: Optional[str] = None  # ISO-8601
    timed_out: bool = False
    # Rollback support
    snapshots: List[Snapshot] = field(default_factory=list)
    rollback_history: List[RollbackRecord] = field(default_factory=list)
