"""Detection schemas for CRUD and analysis endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class DetectionCreate(BaseModel):
    """Data sent alongside an image upload."""
    latitude: float | None = None
    longitude: float | None = None
    source_type: str = Field(default="upload", pattern="^(upload|video|satellite)$")
    description: str | None = None


class DetectionUpdate(BaseModel):
    """PATCH /detections/{id} -- partial update."""
    severity: str | None = Field(default=None, pattern="^(low|medium|high|critical)$")
    status: str | None = Field(
        default=None,
        pattern="^(detected|verified|repair_scheduled|resolved)$"
    )
    description: str | None = None


class DetectionResponse(BaseModel):
    """Single detection returned to the client."""
    id: uuid.UUID
    user_id: uuid.UUID
    image_path: str
    source_type: str
    latitude: float | None
    longitude: float | None
    severity: str
    confidence_score: float
    bbox_data: dict | None
    ai_analysis: dict | None
    status: str
    description: str | None
    detected_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class DetectionListResponse(BaseModel):
    """Paginated list of detections."""
    items: list[DetectionResponse]
    total: int
    page: int
    page_size: int
