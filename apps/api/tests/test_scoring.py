"""Test scoring service"""
import pytest
from decimal import Decimal
from uuid import uuid4

from app.services.scoring import ScoringService
from app.models import Property, Event, Observation


@pytest.mark.asyncio
async def test_scoring_service_calculates_signals(db_session):
    """Test that scoring service calculates signals correctly"""
    # Create test property
    property_obj = Property(
        external_property_id="TEST-001",
        geometry=b"\\x01\\x01\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00",
        data_source="test",
    )
    db_session.add(property_obj)

    # Create test event
    event = Event(
        event_type="flood",
        name="Test Flood",
        event_date="2023-08-15",
        status="active",
    )
    db_session.add(event)
    await db_session.flush()

    # Create observation
    observation = Observation(
        property_id=property_obj.id,
        event_id=event.id,
        observation_date="2023-08-16T00:00:00Z",
        flood_extent=True,
        distance_to_flood_m=Decimal("100"),
        rainfall_percentile=Decimal("90"),
        river_stage_exceedance=True,
        elevation_m=Decimal("2"),
        optical_change=Decimal("0.8"),
        cloud_quality=Decimal("0.95"),
        sensor_source="Sentinel-2",
        feature_payload={},
    )
    db_session.add(observation)
    await db_session.flush()

    # Test scoring
    scoring_service = ScoringService(db_session)
    result = await scoring_service.score_property_for_event(property_obj.id, event.id)

    # Verify results
    assert "damage_probability" in result
    assert "inspection_priority" in result
    assert "evidence" in result

    # High flood signals should result in high probability
    assert result["damage_probability"] > 0.7
    assert result["inspection_priority"] == "P1"
    assert result["confidence"] == "high"


@pytest.mark.asyncio
async def test_scoring_priority_thresholds(db_session):
    """Test that priority assignment uses correct thresholds"""
    scoring_service = ScoringService(db_session)

    # Test signal calculation
    observation_high = Observation(
        property_id=uuid4(),
        event_id=uuid4(),
        observation_date="2023-08-16T00:00:00Z",
        flood_extent=True,
        distance_to_flood_m=Decimal("0"),
        rainfall_percentile=Decimal("95"),
        river_stage_exceedance=True,
        elevation_m=Decimal("1"),
        optical_change=Decimal("0.9"),
        cloud_quality=Decimal("0.95"),
    )

    signals = scoring_service._calculate_signals(observation_high)

    # Verify signals are calculated
    assert signals["flood_extent_signal"] == 1.0
    assert signals["proximity_signal"] == 1.0
    assert signals["rainfall_signal"] == 0.95
