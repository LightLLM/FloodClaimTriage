"""Observation model"""
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Observation(Base):
    """Observation model representing property-level observations during an event"""

    __tablename__ = "observations"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    property_id: Mapped[UUID] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_id: Mapped[UUID] = mapped_column(
        ForeignKey("events.id", ondelete="CASCADE"), nullable=False, index=True
    )
    observation_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    flood_extent: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    distance_to_flood_m: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    rainfall_percentile: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    river_stage_exceedance: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    elevation_m: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    optical_change: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    cloud_quality: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    sensor_source: Mapped[str | None] = mapped_column(Text, nullable=True)
    feature_payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
