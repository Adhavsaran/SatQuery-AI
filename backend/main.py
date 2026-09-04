"""SatQuery FastAPI Backend

Main application serving the autonomous remote-sensing agent.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime

from backend.config import settings
from backend.schemas import (
    QueryRequest, QueryResponse, ValidationReport, HealthResponse,
    ToolExecution, ExecutionTrace, Evidence, ConfidenceEstimate,
    ConfidenceLevel, TaskType
)

# Setup logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# ============================================================================
# Lifespan Events
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    # Startup
    logger.info("SatQuery AI backend starting...")
    settings.validate()
    logger.info(f"LLM Provider: {settings.llm_provider}")
    logger.info(f"VLM Provider: {settings.vlm_provider}")

    yield

    # Shutdown
    logger.info("SatQuery AI backend shutting down...")


# ============================================================================
# Create FastAPI App
# ============================================================================


app = FastAPI(
    title="SatQuery AI",
    description="Autonomous Vision-Language Assistant for Multimodal Remote Sensing",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Health & Status Endpoints
# ============================================================================


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check if backend is running."""
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        environment=settings.environment,
    )


@app.get("/config")
async def get_config():
    """Get current configuration (non-sensitive)."""
    return {
        "llm_provider": settings.llm_provider,
        "vlm_provider": settings.vlm_provider,
        "environment": settings.environment,
        "enable_cache": settings.enable_cache,
        "enable_execution_trace": settings.enable_execution_trace,
    }


# ============================================================================
# Query Endpoint
# ============================================================================


@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a natural language query about satellite imagery.

    This is the main entry point for the SatQuery agent.

    Args:
        request: QueryRequest containing query text and images

    Returns:
        QueryResponse with answer, evidence, and optional execution trace
    """
    logger.info(f"Received query: {request.query}")
    logger.info(f"Images: {len(request.images)} file(s)")

    try:
        # TODO: Phase 1 - Implement full agent orchestration
        # For now, return placeholder response

        # Step 1: Validate inputs (will be implemented in Phase 1)
        validation = ValidationReport(
            is_valid=True,
            num_images=len(request.images),
            image_modalities=[],  # Will be populated by validator
            detected_task_type=TaskType.SINGLE_IMAGE_ANALYSIS,
            errors=[],
            warnings=["Phase 1: Using placeholder response. Full agent not yet implemented."],
            metadata_summary={}
        )

        if not validation.is_valid:
            logger.error(f"Validation failed: {validation.errors}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"errors": validation.errors}
            )

        # Step 2: Placeholder agent execution (Phase 1)
        # In Phase 2+, this will call the real agent
        execution_trace = ExecutionTrace(
            query=request.query,
            task_type=TaskType.SINGLE_IMAGE_ANALYSIS,
            validation=validation,
            plan=["validate_inputs", "extract_metadata", "analyze_images"],
            executions=[],
            total_duration_ms=100.0,
            errors=[]
        ) if request.trace_execution else None

        # Step 3: Create placeholder response
        response = QueryResponse(
            query=request.query,
            answer="SatQuery AI backend is running. Phase 1 agent implementation in progress.",
            confidence=ConfidenceEstimate(
                level=ConfidenceLevel.UNCERTAIN,
                score=0.0,
                justification="Phase 1: Placeholder response. Full agent not implemented.",
                evidence_count=0,
            ),
            evidence=[],
            findings={
                "status": "development",
                "phase": "Phase 1 - Backend & Infrastructure",
                "next_phase": "Phase 2 - Vision-Language Models"
            },
            execution_trace=execution_trace,
        )

        logger.info(f"Query processed successfully")
        return response

    except Exception as e:
        logger.exception(f"Error processing query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================================================
# Validation Endpoint
# ============================================================================


@app.post("/api/validate", response_model=ValidationReport)
async def validate_inputs(request: QueryRequest):
    """
    Validate query inputs without executing the full agent.

    Returns a validation report indicating whether the query can be processed.
    """
    logger.info(f"Validating query: {request.query}")

    try:
        # TODO: Phase 1 - Implement real validator
        # For now, return placeholder

        validation = ValidationReport(
            is_valid=True,
            num_images=len(request.images),
            image_modalities=[],
            detected_task_type=TaskType.SINGLE_IMAGE_ANALYSIS,
            errors=[],
            warnings=["Phase 1: Validator not yet implemented"],
            metadata_summary={}
        )

        return validation

    except Exception as e:
        logger.exception(f"Error validating inputs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================================================
# Agent Status Endpoint
# ============================================================================


@app.get("/api/agent/status")
async def agent_status():
    """Get current agent status and capabilities."""
    return {
        "status": "development",
        "phase": "Phase 1 - Backend Infrastructure",
        "capabilities": {
            "single_image_analysis": False,
            "bitemporal_analysis": False,
            "optical_sar_fusion": False,
            "vqa": False,
            "grounding": False,
            "change_detection": False,
        },
        "tools_available": 0,
        "models_loaded": 0,
    }


# ============================================================================
# Error Handlers
# ============================================================================


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.exception(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error"}
    )


# ============================================================================
# Root Endpoint
# ============================================================================


@app.get("/")
async def root():
    """Root endpoint with API documentation link."""
    return {
        "name": "SatQuery AI",
        "description": "Autonomous Vision-Language Assistant for Remote Sensing",
        "version": "0.1.0",
        "phase": "Phase 1 - Backend Infrastructure",
        "docs": "/docs",
        "health": "/health",
        "query": "/api/query",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.backend_host,
        port=settings.backend_port,
        log_level=settings.log_level.lower(),
    )
