"""Migration Workflow Agent - State Management."""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


class Phase(Enum):
    """Migration phases."""
    ANALYSIS = "analysis"
    PLANNING = "planning"
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
