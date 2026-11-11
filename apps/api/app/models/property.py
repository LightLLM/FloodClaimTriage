"""Property model"""
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Property(Base):
    """Property model representing insured properties"""

    __tablename__ = "properties"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    external_property_id: Mapped[str] = mapped_column(
        Text, unique=True, nullable=False, index=True
    )
    geometry: Mapped[bytes] = mapped_column(
        Geometry("POINT", srid=4326), nullable=False, index=True
    )
    address_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    building_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    exposure_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    region: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_source: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
