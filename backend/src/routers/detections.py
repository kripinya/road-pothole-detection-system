"""Detection CRUD routes -- create, read, update, soft-delete."""

import os
import uuid
import logging
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_db
from src.models.user import User
from src.models.detection import Detection
from src.models.repair_priority import RepairPriority
from src.schemas.detection import (
    DetectionResponse,
    DetectionUpdate,
    DetectionListResponse,
)
from src.middleware.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/detections", tags=["Detections"])


@router.post("/", response_model=DetectionResponse, status_code=status.HTTP_201_CREATED)
async def create_detection(
    file: UploadFile = File(...),
    latitude: float | None = Form(None),
    longitude: float | None = Form(None),
    source_type: str = Form("upload"),
    description: str | None = Form(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload an image, run ML detection, and store results."""
    # Save uploaded file
    file_id = str(uuid.uuid4())
    file_ext = os.path.splitext(file.filename or "image.jpg")[1]
    file_path = f"uploads/{file_id}{file_ext}"
    os.makedirs("uploads", exist_ok=True)

    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    # Call ML service for detection + analysis
    ml_result = None
    analysis_result = None

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.ml_service_url}/analyze",
                files={"file": (file.filename, contents, file.content_type)},
            )
            if response.status_code == 200:
                data = response.json()
                ml_result = data.get("detection")
                analysis_result = data.get("analysis")
    except Exception as e:
        logger.warning(f"ML service unavailable: {e}")

    # Extract severity from analysis
    severity = "low"
    confidence = 0.0
    if analysis_result and analysis_result.get("severity"):
        severity = analysis_result["severity"].get("classification", "low")
    if ml_result and ml_result.get("detections"):
        confidences = [d["confidence"] for d in ml_result["detections"]]
        confidence = max(confidences) if confidences else 0.0

    # Create detection record
    detection = Detection(
        user_id=user.id,
        image_path=file_path,
        source_type=source_type,
        latitude=latitude,
        longitude=longitude,
        severity=severity,
        confidence_score=confidence,
        bbox_data=ml_result,
        ai_analysis=analysis_result,
        status="detected",
        description=description,
    )
    db.add(detection)
    await db.commit()
    await db.refresh(detection)

    # Store repair priority if analysis succeeded
    if analysis_result and analysis_result.get("priority"):
        priority_data = analysis_result["priority"]
        repair = RepairPriority(
            detection_id=detection.id,
            priority_score=priority_data.get("priority_score", 0),
            estimated_cost=priority_data.get("estimated_cost_inr"),
            recommended_action=priority_data.get("recommended_action"),
            repair_timeline=priority_data.get("repair_timeline", "next_maintenance_cycle"),
            agent_outputs=analysis_result,
        )
        db.add(repair)
        await db.commit()

    return detection


@router.get("/", response_model=DetectionListResponse)
async def list_detections(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    severity: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List detections with pagination and optional filters."""
    query = select(Detection).where(Detection.deleted_at.is_(None))

    if severity:
        query = query.where(Detection.severity == severity)
    if status_filter:
        query = query.where(Detection.status == status_filter)

    # Count total matching rows
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Paginate
    query = query.order_by(Detection.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    items = result.scalars().all()

    return DetectionListResponse(
        items=items, total=total, page=page, page_size=page_size
    )


@router.get("/{detection_id}", response_model=DetectionResponse)
async def get_detection(
    detection_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single detection by ID."""
    result = await db.execute(
        select(Detection).where(
            Detection.id == detection_id,
            Detection.deleted_at.is_(None),
        )
    )
    detection = result.scalar_one_or_none()

    if detection is None:
        raise HTTPException(status_code=404, detail="Detection not found")

    return detection


@router.patch("/{detection_id}", response_model=DetectionResponse)
async def update_detection(
    detection_id: uuid.UUID,
    data: DetectionUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Partially update a detection (status, severity, description)."""
    result = await db.execute(
        select(Detection).where(
            Detection.id == detection_id,
            Detection.deleted_at.is_(None),
        )
    )
    detection = result.scalar_one_or_none()

    if detection is None:
        raise HTTPException(status_code=404, detail="Detection not found")

    # Only update fields that were provided
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(detection, field, value)

    await db.commit()
    await db.refresh(detection)
    return detection


@router.delete("/{detection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_detection(
    detection_id: uuid.UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a detection (sets deleted_at timestamp)."""
    result = await db.execute(
        select(Detection).where(
            Detection.id == detection_id,
            Detection.deleted_at.is_(None),
        )
    )
    detection = result.scalar_one_or_none()

    if detection is None:
        raise HTTPException(status_code=404, detail="Detection not found")

    detection.deleted_at = datetime.now(timezone.utc)
    await db.commit()
