"""Unit tests for scoring signal logic (no database required)."""
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from app.services.scoring import ScoringService


def _make_observation(**overrides):
    defaults = {
        "property_id": uuid4(),
        "event_id": uuid4(),
        "observation_date": "2023-08-16T00:00:00Z",
        "flood_extent": True,
        "distance_to_flood_m": Decimal("0"),
        "rainfall_percentile": Decimal("95"),
        "river_stage_exceedance": True,
        "elevation_m": Decimal("1"),
        "optical_change": Decimal("0.9"),
        "cloud_quality": Decimal("0.95"),
        "sensor_source": "Sentinel-2",
        "feature_payload": {"stac_item_id": "sentinel2-test"},
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def test_calculate_signals_high_risk():
    service = ScoringService(session=None)  # type: ignore[arg-type]
    observation = _make_observation()
    signals = service._calculate_signals(observation)

    assert signals["flood_extent_signal"] == 1.0
    assert signals["proximity_signal"] == 1.0
    assert signals["rainfall_signal"] == 0.95
    assert signals["river_stage_signal"] == 1.0
    assert signals["optical_change_signal"] == 0.9
    assert signals["elevation_signal"] == 0.9


def test_calculate_signals_no_observation():
    service = ScoringService(session=None)  # type: ignore[arg-type]
    signals = service._calculate_signals(None)

    assert signals == {
        "flood_extent_signal": 0.0,
        "proximity_signal": 0.0,
        "rainfall_signal": 0.0,
        "river_stage_signal": 0.0,
        "optical_change_signal": 0.0,
        "elevation_signal": 0.0,
    }


def test_priority_thresholds_from_formula():
    service = ScoringService(session=None)  # type: ignore[arg-type]
    observation = _make_observation()
    signals = service._calculate_signals(observation)

    damage_probability = (
        0.45 * signals["flood_extent_signal"]
        + 0.20 * signals["proximity_signal"]
        + 0.15 * signals["rainfall_signal"]
        + 0.10 * signals["river_stage_signal"]
        + 0.10 * signals["optical_change_signal"]
        - 0.10 * signals["elevation_signal"]
    )
    damage_probability = max(0.01, min(0.99, damage_probability))

    assert damage_probability >= 0.75

    if damage_probability >= 0.75:
        priority = "P1"
        action = "Field inspection"
    elif damage_probability >= 0.45:
        priority = "P2"
        action = "Desk review"
    else:
        priority = "P3"
        action = "No action"

    assert priority == "P1"
    assert action == "Field inspection"


def test_confidence_high_with_complete_data():
    service = ScoringService(session=None)  # type: ignore[arg-type]
    observation = _make_observation()
    signals = service._calculate_signals(observation)
    confidence = service._calculate_confidence(observation, signals)
    assert confidence == "high"


def test_confidence_low_without_observation():
    service = ScoringService(session=None)  # type: ignore[arg-type]
    confidence = service._calculate_confidence(None, {})
    assert confidence == "low"


def test_low_priority_when_far_from_flood():
    service = ScoringService(session=None)  # type: ignore[arg-type]
    observation = _make_observation(
        flood_extent=False,
        distance_to_flood_m=Decimal("5000"),
        rainfall_percentile=Decimal("10"),
        river_stage_exceedance=False,
        elevation_m=Decimal("20"),
        optical_change=Decimal("0.05"),
        cloud_quality=Decimal("0.9"),
    )
    signals = service._calculate_signals(observation)
    damage_probability = (
        0.45 * signals["flood_extent_signal"]
        + 0.20 * signals["proximity_signal"]
        + 0.15 * signals["rainfall_signal"]
        + 0.10 * signals["river_stage_signal"]
        + 0.10 * signals["optical_change_signal"]
        - 0.10 * signals["elevation_signal"]
    )
    damage_probability = max(0.01, min(0.99, damage_probability))
    assert damage_probability < 0.45
