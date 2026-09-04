"""SatQuery Agent Orchestrator

Coordinates the multi-phase autonomous agent execution:
Understand → Validate → Plan → Execute → Verify → Fuse → Explain
"""

import logging
from typing import Optional
from datetime import datetime

from agent.state import AgentState, AgentPhase, state_manager
from agent.tool_registry import tool_registry, init_phase1_tools
from backend.schemas import QueryRequest, QueryResponse, ValidationReport

logger = logging.getLogger(__name__)


class SatQueryAgent:
    """
    Autonomous agent for satellite image analysis.

    Orchestrates the complete pipeline from query to answer.
    """

    def __init__(self):
        """Initialize agent."""
        self.name = "SatQuery Agent"
        self.version = "0.1.0"
        self.phase = "Phase 1"

        # Initialize tools
        init_phase1_tools()
        logger.info(f"Agent initialized: {self.name} v{self.version} ({self.phase})")

    async def process_query(self, request: QueryRequest) -> QueryResponse:
        """
        Process a user query end-to-end.

        Args:
            request: QueryRequest with query text and images

        Returns:
            QueryResponse with answer and evidence

        Phases:
            1. UNDERSTAND: Parse query and detect task type
            2. VALIDATE: Check inputs are valid
            3. PLAN: Create execution plan
            4. EXECUTE: Run tools
            5. VERIFY: Check results
            6. FUSE: Combine evidence
            7. EXPLAIN: Generate natural language answer
        """
        # Create execution state
        state = state_manager.create(request)
        logger.info(f"[{state.execution_id}] Starting query processing")

        try:
            # Phase 1: UNDERSTAND
            await self._phase_understand(state)

            # Phase 2: VALIDATE
            await self._phase_validate(state)
            if not state.is_valid:
                return self._create_error_response(request, state)

            # Phase 3: PLAN
            await self._phase_plan(state)

            # Phase 4: EXECUTE
            await self._phase_execute(state)

            # Phase 5: VERIFY
            await self._phase_verify(state)

            # Phase 6: FUSE
            await self._phase_fuse(state)

            # Phase 7: EXPLAIN
            await self._phase_explain(state)

            # Finalize
            state.set_phase(AgentPhase.COMPLETED)
            logger.info(f"[{state.execution_id}] Query processing completed")

            return self._create_response(request, state)

        except Exception as e:
            logger.exception(f"[{state.execution_id}] Agent error: {str(e)}")
            state.add_error(str(e))
            state.set_phase(AgentPhase.FAILED)
            return self._create_error_response(request, state)

    async def _phase_understand(self, state: AgentState) -> None:
        """Phase 1: Understand the query and detect task type."""
        logger.info(f"[{state.execution_id}] PHASE: UNDERSTAND")
        state.set_phase(AgentPhase.VALIDATING)  # Using VALIDATING as placeholder

        # TODO: Phase 2 - Implement LLM-based query understanding
        # For Phase 1: Placeholder implementation
        from backend.schemas import TaskType, ImageModality

        if len(state.input_images) == 1:
            state.task_type = TaskType.SINGLE_IMAGE_ANALYSIS
            state.image_modalities = [ImageModality.UNKNOWN]
        elif len(state.input_images) == 2:
            state.task_type = TaskType.BITEMPORAL_ANALYSIS
            state.image_modalities = [ImageModality.UNKNOWN, ImageModality.UNKNOWN]
        else:
            state.task_type = TaskType.MULTI_TEMPORAL_ANALYSIS
            state.image_modalities = [ImageModality.UNKNOWN] * len(state.input_images)

        logger.info(f"[{state.execution_id}] Detected task: {state.task_type}")

    async def _phase_validate(self, state: AgentState) -> None:
        """Phase 2: Validate inputs."""
        logger.info(f"[{state.execution_id}] PHASE: VALIDATE")
        state.set_phase(AgentPhase.VALIDATING)

        # TODO: Phase 1 - Implement real validator
        # For now: placeholder validation

        state.validation_report = ValidationReport(
            is_valid=True,
            num_images=len(state.input_images),
            image_modalities=state.image_modalities,
            detected_task_type=state.task_type,
            errors=[],
            warnings=["Phase 1: Validation is placeholder"],
            metadata_summary={}
        )

        state.is_valid = state.validation_report.is_valid
        logger.info(f"[{state.execution_id}] Validation result: {state.is_valid}")

    async def _phase_plan(self, state: AgentState) -> None:
        """Phase 3: Create execution plan."""
        logger.info(f"[{state.execution_id}] PHASE: PLAN")
        state.set_phase(AgentPhase.PLANNING)

        # TODO: Phase 1 - Implement dynamic planning
        # For now: Basic plan based on task type

        if state.task_type and state.is_valid:
            state.plan = [
                "ImageValidator",
                "MetadataExtractor",
            ]
            state.plan_reasoning = "Phase 1: Basic placeholder plan"
            logger.info(f"[{state.execution_id}] Plan: {state.plan}")

    async def _phase_execute(self, state: AgentState) -> None:
        """Phase 4: Execute tools."""
        logger.info(f"[{state.execution_id}] PHASE: EXECUTE")
        state.set_phase(AgentPhase.EXECUTING)

        # TODO: Phase 1 - Execute planned tools

        logger.info(f"[{state.execution_id}] Execution completed")

    async def _phase_verify(self, state: AgentState) -> None:
        """Phase 5: Verify results."""
        logger.info(f"[{state.execution_id}] PHASE: VERIFY")
        state.set_phase(AgentPhase.VERIFYING)

        # TODO: Phase 2+ - Implement verification logic

        state.verified = True
        logger.info(f"[{state.execution_id}] Verification: {state.verified}")

    async def _phase_fuse(self, state: AgentState) -> None:
        """Phase 6: Fuse evidence."""
        logger.info(f"[{state.execution_id}] PHASE: FUSE")
        state.set_phase(AgentPhase.FUSING)

        # TODO: Phase 3+ - Implement evidence fusion

        logger.info(f"[{state.execution_id}] Evidence fusion completed")

    async def _phase_explain(self, state: AgentState) -> None:
        """Phase 7: Generate explanation."""
        logger.info(f"[{state.execution_id}] PHASE: EXPLAIN")
        state.set_phase(AgentPhase.EXPLAINING)

        # TODO: Phase 2 - Use LLM to generate explanation

        state.final_answer = (
            f"Processing completed for: {state.user_query[:50]}... "
            f"Phase 1: Backend infrastructure ready. "
            f"Awaiting agent implementation."
        )

        # Placeholder confidence
        state.confidence_score = 0.0
        state.confidence_justification = "Phase 1: Placeholder response. Full agent not implemented."

        logger.info(f"[{state.execution_id}] Explanation generated")

    def _create_response(self, request: QueryRequest, state: AgentState) -> QueryResponse:
        """Create successful response from state."""
        from backend.schemas import (
            QueryResponse, ConfidenceEstimate, ConfidenceLevel, Evidence
        )

        return QueryResponse(
            query=request.query,
            answer=state.final_answer or "Processing completed.",
            confidence=ConfidenceEstimate(
                level=ConfidenceLevel.UNCERTAIN,
                score=state.confidence_score or 0.0,
                justification=state.confidence_justification,
                evidence_count=len(state.evidence_items),
            ),
            evidence=[],  # TODO: Convert state.evidence_items to Evidence objects
            findings=state.structured_findings,
            execution_trace=state.execution_trace,
        )

    def _create_error_response(self, request: QueryRequest, state: AgentState) -> QueryResponse:
        """Create error response from state."""
        from backend.schemas import QueryResponse, ConfidenceEstimate, ConfidenceLevel

        error_msg = "\n".join(state.errors) if state.errors else "Unknown error"

        return QueryResponse(
            query=request.query,
            answer=f"Error processing query: {error_msg}",
            confidence=ConfidenceEstimate(
                level=ConfidenceLevel.UNCERTAIN,
                score=0.0,
                justification="Query processing failed",
                evidence_count=0,
            ),
            evidence=[],
            findings={"errors": state.errors},
        )

    def get_status(self) -> dict:
        """Get agent status."""
        return {
            "name": self.name,
            "version": self.version,
            "phase": self.phase,
            "status": "development",
            "tools_registered": len(tool_registry.tools),
            "execution_phases": [p.value for p in AgentPhase],
        }


# Global agent instance
agent = SatQueryAgent()
