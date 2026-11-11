"""Score schemas"""
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class Evidence(BaseModel):
    """Evidence payload for score explanation"""

    flood_extent_signal: float = Field(..., description="0-1 signal from flood extent")
    proximity_signal: float = Field(..., description="0-1 signal from distance to flood")
    rainfall_signal: float = Field(..., description="0-1 signal from rainfall data")
    river_stage_signal: float = Field(..., description="0-1 signal from river stage")
    optical_change_signal: float = Field(..., description="0-1 signal from optical change")
    elevation_signal: float = Field(..., description="0-1 signal from elevation")
    data_sources: dict[str, str] = Field(..., description="References to input data")
    confidence_factors: dict[str, str] = Field(..., description="Factors affecting confidence")


class ScoreCreate(BaseModel):
    """Schema for creating a score (internal use)"""

    property_id: UUID
    event_id: UUID
    model_version: str
    damage_probability: Decimal
    damage_confidence: str
    inspection_priority: str
    recommended_action: str
    evidence: Evidence


class Score(BaseModel):
    """Schema for score response"""

    id: UUID
    property_id: UUID
    event_id: UUID
    model_version: str
    damage_probability: Decimal
    damage_confidence: str
    inspection_priority: str
    recommended_action: str
    evidence: dict
    created_at: datetime

    class Config:
        from_attributes = True


class ScoreResponse(Score):
    """Schema for detailed score response with property info"""

    property: dict | None = None


class TriageItem(BaseModel):
    """Schema for triage queue item"""

    property_id: UUID
    external_property_id: str
    geometry: dict
    exposure_value: Decimal | None
    damage_probability: Decimal
    inspection_priority: str
    recommended_action: str
    created_at: datetime


class ScoreRequest(BaseModel):
    """Schema for requesting scoring for an event"""

    force_rescore: bool = Field(default=False, description="Force rescoring of existing scores")
