"""Event schemas"""
from datetime import date, datetime
from typing import Any
from uuid import UUID

from geojson_pydantic import Polygon
from pydantic import BaseModel, ConfigDict, Field


class EventCreate(BaseModel):
    """Schema for creating a new event"""

    event_type: str = Field(..., description="Type of event (e.g., flood, hurricane)")
    name: str = Field(..., description="Human-readable name of the event")
    event_date: date = Field(..., description="Date of the event")
    geometry: Polygon | None = Field(None, description="Geographic extent of the event")
    stac_collection_id: str | None = Field(None, description="STAC collection ID")


class Event(BaseModel):
    """Schema for event response"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    event_type: str
    name: str
    event_date: date
    geometry: dict[str, Any] | None = None
    stac_collection_id: str | None = None
    status: str
    created_at: datetime


class EventResponse(BaseModel):
    """Schema for detailed event response"""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    event_type: str
    name: str
    event_date: date
    geometry: dict[str, Any] | None = None
    stac_collection_id: str | None = None
    status: str
    created_at: datetime
    property_count: int = 0
    scored_count: int = 0
