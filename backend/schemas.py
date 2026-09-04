"""SatQuery API Schemas - Request/Response Models

Defines Pydantic models for structured data exchange.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class ImageModality(str, Enum):
    """Supported image modalities."""
    OPTICAL = "optical"
    MULTISPECTRAL = "multispectral"
    SAR = "sar"
    THERMAL = "thermal"
    PANCHROMATIC = "panchromatic"
    HYPERSPECTRAL = "hyperspectral"
    UNKNOWN = "unknown"


class TaskType(str, Enum):
    """Supported task types."""
    SINGLE_IMAGE_ANALYSIS = "single_image_analysis"
    BITEMPORAL_ANALYSIS = "bitemporal_analysis"
    OPTICAL_SAR_ANALYSIS = "optical_sar_analysis"
    MULTI_TEMPORAL_ANALYSIS = "multi_temporal_analysis"
    VQA = "visual_question_answering"
    SCENE_DESCRIPTION = "scene_description"
    CHANGE_DETECTION = "change_detection"
    GROUNDING = "grounding"
    UNKNOWN = "unknown"


class ConfidenceLevel(str, Enum):
    """Confidence assessment levels."""
    OBSERVED = "observed"
    SUPPORTED_INFERENCE = "supported_inference"
    UNCERTAIN = "uncertain"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ============================================================================
# Request Models
# ============================================================================


class ImageMetadata(BaseModel):
    """Image metadata for validation and analysis."""
    filepath: str = Field(..., description="Path to image file")
    modality: ImageModality = Field(default=ImageModality.UNKNOWN, description="Image modality")
    bands: Optional[List[str]] = Field(default=None, description="Band names (e.g., ['B2', 'B3', 'B4'])")
    crs: Optional[str] = Field(default=None, description="Coordinate reference system (e.g., 'EPSG:4326')")
    resolution: Optional[float] = Field(default=None, description="Spatial resolution in meters")
    extent: Optional[Dict[str, float]] = Field(
        default=None,
        description="Geographic extent {'north', 'south', 'east', 'west'}"
    )
    acquisition_date: Optional[str] = Field(default=None, description="ISO 8601 acquisition date")
    sensor_name: Optional[str] = Field(default=None, description="Sensor name (e.g., 'Sentinel-2')")

    class Config:
        json_schema_extra = {
            "example": {
                "filepath": "/data/s2_2024_01_15.tif",
                "modality": "multispectral",
                "bands": ["B2", "B3", "B4", "B5", "B6", "B7", "B8"],
                "crs": "EPSG:32633",
                "resolution": 10.0,
                "acquisition_date": "2024-01-15",
                "sensor_name": "Sentinel-2A"
            }
        }


class QueryRequest(BaseModel):
    """Main query request to SatQuery agent."""
    query: str = Field(
        ...,
        description="Natural language query about satellite imagery",
        example="Find newly constructed buildings between 2024 and 2026"
    )
    images: List[ImageMetadata] = Field(
        ...,
        description="List of satellite images to analyze",
        min_items=1
    )
    optional_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional context (AOI polygon, temporal constraints, etc.)"
    )
    trace_execution: bool = Field(
        default=True,
        description="Return full execution trace with intermediate results"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is the extent of urban expansion from 2020 to 2024?",
                "images": [
                    {
                        "filepath": "/data/urban_2020.tif",
                        "modality": "multispectral",
                        "acquisition_date": "2020-06-15"
                    },
                    {
                        "filepath": "/data/urban_2024.tif",
                        "modality": "multispectral",
                        "acquisition_date": "2024-06-15"
                    }
                ],
                "trace_execution": True
            }
        }


# ============================================================================
# Validation Models
# ============================================================================


class ValidationReport(BaseModel):
    """Data validation report."""
    is_valid: bool = Field(..., description="Whether inputs are valid")
    num_images: int = Field(..., description="Number of images provided")
    image_modalities: List[ImageModality] = Field(..., description="Detected modalities")
    detected_task_type: TaskType = Field(..., description="Inferred task type")
    errors: List[str] = Field(default=[], description="Validation errors")
    warnings: List[str] = Field(default=[], description="Validation warnings")
    metadata_summary: Dict[str, Any] = Field(default={}, description="Summary of image metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "is_valid": True,
                "num_images": 2,
                "image_modalities": ["multispectral", "multispectral"],
                "detected_task_type": "bitemporal_analysis",
                "errors": [],
                "warnings": ["Spatial resolution differs: 10m vs 20m"],
                "metadata_summary": {
                    "crss": ["EPSG:32633", "EPSG:32633"],
                    "bands": ["B2,B3,B4,B5,B6,B7,B8"] * 2
                }
            }
        }


# ============================================================================
# Evidence and Verification Models
# ============================================================================


class Evidence(BaseModel):
    """Single piece of evidence supporting a finding."""
    source: str = Field(..., description="Source of evidence (image, tool, model)")
    tool_name: str = Field(..., description="Tool that generated evidence")
    model_name: Optional[str] = Field(default=None, description="Model used (if applicable)")
    input_data: Dict[str, Any] = Field(..., description="Input to the tool")
    output_data: Dict[str, Any] = Field(..., description="Output from the tool")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "source": "image_2024.tif",
                "tool_name": "ObjectDetector",
                "model_name": "YOLOv8-buildings",
                "input_data": {"image": "path/to/image.tif"},
                "output_data": {"detections": [{"bbox": [100, 200, 150, 250], "class": "building"}]},
                "confidence": 0.85,
                "timestamp": "2024-09-04T10:00:00Z"
            }
        }


class ConfidenceEstimate(BaseModel):
    """Confidence assessment with justification."""
    level: ConfidenceLevel = Field(..., description="Overall confidence level")
    score: float = Field(..., ge=0.0, le=1.0, description="Numerical confidence (0-1)")
    justification: str = Field(..., description="Explanation of confidence level")
    evidence_count: int = Field(..., description="Number of supporting evidence pieces")
    model_agreement: Optional[float] = Field(default=None, description="Agreement between models (0-1)")


# ============================================================================
# Response Models
# ============================================================================


class ToolExecution(BaseModel):
    """Record of a tool execution step."""
    tool_name: str = Field(..., description="Name of executed tool")
    status: str = Field(..., description="Execution status (success, failed, skipped)")
    parameters: Dict[str, Any] = Field(..., description="Tool parameters")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Tool result")
    error_message: Optional[str] = Field(default=None, description="Error if failed")
    duration_ms: float = Field(..., description="Execution time in milliseconds")


class ExecutionTrace(BaseModel):
    """Complete trace of agent execution."""
    query: str = Field(..., description="Original query")
    task_type: TaskType = Field(..., description="Detected task type")
    validation: ValidationReport = Field(..., description="Input validation report")
    plan: List[str] = Field(..., description="Execution plan (tool names)")
    executions: List[ToolExecution] = Field(..., description="Executed tools and results")
    total_duration_ms: float = Field(..., description="Total execution time")
    errors: List[str] = Field(default=[], description="Errors during execution")


class QueryResponse(BaseModel):
    """Final response to a query."""
    query: str = Field(..., description="Original query")
    answer: str = Field(..., description="Final answer in natural language")
    confidence: ConfidenceEstimate = Field(..., description="Confidence in the answer")
    evidence: List[Evidence] = Field(..., description="Supporting evidence")
    findings: Dict[str, Any] = Field(..., description="Structured findings")
    execution_trace: Optional[ExecutionTrace] = Field(
        default=None,
        description="Execution trace (if requested)"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Find newly constructed buildings between 2024 and 2026",
                "answer": "Detected 47 new buildings in the study area. 34 were newly constructed, with an average size of 250 m². Highest concentration in the northeastern district.",
                "confidence": {
                    "level": "high",
                    "score": 0.87,
                    "justification": "Supported by bi-temporal change detection with SAR verification",
                    "evidence_count": 5,
                    "model_agreement": 0.92
                },
                "evidence": [],
                "findings": {
                    "new_buildings_count": 34,
                    "buildings_modified": 13,
                    "average_size_m2": 250,
                    "highest_concentration": "northeastern_district"
                }
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Environment (dev/prod)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
