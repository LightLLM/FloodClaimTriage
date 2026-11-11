"""Property schemas"""
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from geojson_pydantic import Point
from pydantic import BaseModel, ConfigDict


class PropertyCreate(BaseModel):
    """Schema for creating a new property"""

    external_property_id: str
    geometry: Point
    address_hash: str | None = None
    building_type: str | None = None
    exposure_value: Decimal | None = None
    region: str | None = None
    data_source: str


class Property(BaseModel):
    """Schema for property response"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    external_property_id: str
    geometry: dict[str, Any]
    address_hash: str | None = None
    building_type: str | None = None
    exposure_value: Decimal | None = None
    region: str | None = None
    data_source: str
    created_at: datetime
    updated_at: datetime


class PropertyResponse(Property):
    """Schema for detailed property response with scores"""

    latest_score: dict[str, Any] | None = None
