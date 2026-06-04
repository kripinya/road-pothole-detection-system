"""Repair Priority ORM model -- stores agentic AI recommendations."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Float, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class RepairPriority(Base):
    """Repair priorities table -- agentic AI generated repair plans."""

    __tablename__ = "repair_priorities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    detection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("detections.id", ondelete="CASCADE"),
        unique=True, nullable=False
    )

    # Priority data
    priority_score: Mapped[float] = mapped_column(Float, nullable=False)
    estimated_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    recommended_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    repair_timeline: Mapped[str] = mapped_column(
        String(50), nullable=False, default="next_maintenance_cycle"
    )

    # Full agent pipeline output
    agent_outputs: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    generated_by: Mapped[str] = mapped_column(
        String(100), nullable=False, default="agentic_ai_v1"
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
