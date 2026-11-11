"""Property schemas"""
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from geojson_pydantic import Point
from pydantic import BaseModel, Field


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

    id: UUID
    external_property_id: str
    geometry: dict
    address_hash: str | None = None
    building_type: str | None = None
    exposure_value: Decimal | None = None
    region: str | None = None
    data_source: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PropertyResponse(Property):
    """Schema for detailed property response with scores"""

    latest_score: dict | None = None
