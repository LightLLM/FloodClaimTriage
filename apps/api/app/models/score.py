"""Score model"""
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Score(Base):
    """Score model representing damage probability and inspection priority"""

    __tablename__ = "scores"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    property_id: Mapped[UUID] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_id: Mapped[UUID] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True
    )
    model_version: Mapped[str] = mapped_column(Text, nullable=False)
    damage_probability: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    damage_confidence: Mapped[str] = mapped_column(Text, nullable=False)
    inspection_priority: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    recommended_action: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
