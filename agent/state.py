"""Agent State Management

Manages the complete state of an agent execution.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime
import uuid

from backend.schemas import (
    QueryRequest, TaskType, ImageModality,
    ValidationReport, ToolExecution, ExecutionTrace
)


class AgentPhase(str, Enum):
    """Agent execution phases."""
    INITIALIZED = "initialized"
    VALIDATING = "validating"
    PLANNING = "planning"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    FUSING = "fusing"
    EXPLAINING = "explaining"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentState(BaseModel):
    """
    Complete state of a SatQuery agent execution.

    Tracks all information from query reception through final answer generation.
    """
    # Execution ID
    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # User Input
    user_query: str = Field(..., description="Original user query")
    input_images: List[Dict[str, Any]] = Field(..., description="Provided images")
    optional_metadata: Optional[Dict[str, Any]] = Field(default=None)

    # Detection & Planning
    task_type: Optional[TaskType] = Field(default=None, description="Inferred task type")
    image_modalities: List[ImageModality] = Field(default=[], description="Detected modalities")
    required_tools: List[str] = Field(default=[], description="Tools needed")

    # Validation
    validation_report: Optional[ValidationReport] = Field(default=None)
    is_valid: bool = Field(default=False)

    # Planning
    plan: List[str] = Field(default=[], description="Ordered list of tool names to execute")
    plan_reasoning: str = Field(default="", description="Why this plan was chosen")

    # Execution
    phase: AgentPhase = Field(default=AgentPhase.INITIALIZED)
    executed_tools: List[ToolExecution] = Field(default=[], description="Completed tool executions")
    current_tool: Optional[str] = Field(default=None)
    tool_results: Dict[str, Any] = Field(default={}, description="Results from each tool")

    # Verification
    verification_results: Dict[str, Any] = Field(default={})
    verified: bool = Field(default=False)

    # Evidence Collection
    evidence_items: List[Dict[str, Any]] = Field(default=[], description="Collected evidence")

    # Confidence Estimation
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    confidence_justification: str = Field(default="")

    # Final Answer
    final_answer: Optional[str] = Field(default=None)
    structured_findings: Dict[str, Any] = Field(default={})

    # Error Tracking
    errors: List[str] = Field(default=[])

    # Execution Trace
    execution_trace: Optional[ExecutionTrace] = Field(default=None)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def add_error(self, error_message: str) -> None:
        """Log an error."""
        self.errors.append(f"[{datetime.utcnow().isoformat()}] {error_message}")

    def set_phase(self, phase: AgentPhase) -> None:
        """Transition to a new phase."""
        self.phase = phase

    def add_tool_execution(self, execution: ToolExecution) -> None:
        """Record a tool execution."""
        self.executed_tools.append(execution)
        self.tool_results[execution.tool_name] = execution.result

    def add_evidence(self, evidence: Dict[str, Any]) -> None:
        """Add evidence item."""
        self.evidence_items.append(evidence)

    def is_ready_to_execute(self) -> bool:
        """Check if state is ready for tool execution."""
        return self.is_valid and len(self.plan) > 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump()


class AgentStateManager:
    """Manages agent state lifecycle."""

    def __init__(self):
        """Initialize state manager."""
        self.states: Dict[str, AgentState] = {}

    def create(self, query_request: QueryRequest) -> AgentState:
        """Create a new agent state for a query."""
        state = AgentState(
            user_query=query_request.query,
            input_images=[img.model_dump() for img in query_request.images],
            optional_metadata=query_request.optional_metadata,
        )
        self.states[state.execution_id] = state
        return state

    def get(self, execution_id: str) -> Optional[AgentState]:
        """Retrieve an agent state."""
        return self.states.get(execution_id)

    def delete(self, execution_id: str) -> bool:
        """Delete an agent state."""
        if execution_id in self.states:
            del self.states[execution_id]
            return True
        return False

    def list_active(self) -> List[str]:
        """List all active execution IDs."""
        return list(self.states.keys())


# Global state manager instance
state_manager = AgentStateManager()
