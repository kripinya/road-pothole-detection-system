"""Data validation schemas for the ML service API."""

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Coordinates for a detected object bounding box."""
    x_min: float
    y_min: float
    x_max: float
    y_max: float


class DetectionResult(BaseModel):
    """A single detected pothole or road damage instance."""
    class_id: int
    class_name: str
    confidence: float
    bbox: BoundingBox


class InferenceResponse(BaseModel):
    """The full response from running YOLOv8 on an image."""
    image_width: int
    image_height: int
    detections: list[DetectionResult]
    inference_time_ms: float = Field(..., description="Time taken for model inference in milliseconds")


# Schemas for the Agentic AI Pipeline

class SeverityAssessment(BaseModel):
    """Output from the Severity Agent."""
    score: float = Field(..., ge=0, le=100)
    classification: str = Field(..., pattern="^(low|medium|high|critical)$")
    reasoning: str


class AIAnalysisResponse(BaseModel):
    """The final output from the Orchestrator combining all agent reports."""
    detection_count: int
    overall_severity: SeverityAssessment
    recommended_action: str
    agent_logs: list[str] = Field(default_factory=list)
