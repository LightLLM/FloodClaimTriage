"""Scoring service implementing rule-based damage probability model"""
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import Event, Observation, Property, Score
from app.schemas.score import Evidence


class ScoringService:
    """Service for calculating damage probability and inspection priority"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def score_property_for_event(
        self, property_id: UUID, event_id: UUID
    ) -> dict[str, Any]:
        """
        Score a single property for a specific event.

        Implements the MVP v0.1 rule-based model:
        damage_probability =
          0.45 * flood_extent_signal
        + 0.20 * proximity_signal
        + 0.15 * rainfall_signal
        + 0.10 * river_stage_signal
        + 0.10 * optical_change_signal
        - 0.10 * elevation_signal

        Returns the score with evidence payload.
        """
        # Get latest observation for this property and event
        result = await self.session.execute(
            select(Observation)
            .where(
                Observation.property_id == property_id,
                Observation.event_id == event_id,
            )
            .order_by(Observation.observation_date.desc())
            .limit(1)
        )
        observation = result.scalar_one_or_none()

        # Calculate signals from observation data
        signals = self._calculate_signals(observation)

        # Calculate damage probability using weighted formula
        damage_probability = (
            0.45 * signals["flood_extent_signal"]
            + 0.20 * signals["proximity_signal"]
            + 0.15 * signals["rainfall_signal"]
            + 0.10 * signals["river_stage_signal"]
            + 0.10 * signals["optical_change_signal"]
            - 0.10 * signals["elevation_signal"]
        )

        # Clamp between 0.01 and 0.99
        damage_probability = max(0.01, min(0.99, damage_probability))

        # Determine inspection priority
        if damage_probability >= 0.75:
            priority = "P1"
            recommended_action = "Field inspection"
        elif damage_probability >= 0.45:
            priority = "P2"
            recommended_action = "Desk review"
        else:
            priority = "P3"
            recommended_action = "No action"

        # Determine confidence
        confidence = self._calculate_confidence(observation, signals)

        # Build evidence payload
        evidence = Evidence(
            flood_extent_signal=signals["flood_extent_signal"],
            proximity_signal=signals["proximity_signal"],
            rainfall_signal=signals["rainfall_signal"],
            river_stage_signal=signals["river_stage_signal"],
            optical_change_signal=signals["optical_change_signal"],
            elevation_signal=signals["elevation_signal"],
            data_sources=self._get_data_sources(observation),
            confidence_factors=self._get_confidence_factors(observation),
        )

        # Create or update score
        existing_score = await self.session.execute(
            select(Score).where(
                Score.property_id == property_id,
                Score.event_id == event_id,
                Score.model_version == settings.MODEL_VERSION,
            )
        )
        score = existing_score.scalar_one_or_none()

        if score:
            score.damage_probability = Decimal(str(round(damage_probability, 4)))
            score.damage_confidence = confidence
            score.inspection_priority = priority
            score.recommended_action = recommended_action
            score.evidence = evidence.model_dump()
        else:
            score = Score(
                property_id=property_id,
                event_id=event_id,
                model_version=settings.MODEL_VERSION,
                damage_probability=Decimal(str(round(damage_probability, 4))),
                damage_confidence=confidence,
                inspection_priority=priority,
                recommended_action=recommended_action,
                evidence=evidence.model_dump(),
            )
            self.session.add(score)

        await self.session.flush()

        return {
            "score_id": score.id,
            "damage_probability": float(score.damage_probability),
            "inspection_priority": priority,
            "recommended_action": recommended_action,
            "confidence": confidence,
            "evidence": evidence.model_dump(),
        }

    def _calculate_signals(self, observation: Observation | None) -> dict[str, float]:
        """Calculate normalized signals from observation data"""
        if not observation:
            # No observation data - return low confidence neutral signals
            return {
                "flood_extent_signal": 0.0,
                "proximity_signal": 0.0,
                "rainfall_signal": 0.0,
                "river_stage_signal": 0.0,
                "optical_change_signal": 0.0,
                "elevation_signal": 0.0,
            }

        # Flood extent signal (binary)
        flood_extent_signal = 1.0 if observation.flood_extent else 0.0

        # Proximity signal (inverse distance, normalized)
        proximity_signal = 0.0
        if observation.distance_to_flood_m is not None:
            distance = float(observation.distance_to_flood_m)
            if distance == 0:
                proximity_signal = 1.0
            elif distance < 1000:  # Within 1km
                proximity_signal = 1.0 - (distance / 1000.0)

        # Rainfall signal (percentile)
        rainfall_signal = 0.0
        if observation.rainfall_percentile is not None:
            rainfall_signal = float(observation.rainfall_percentile) / 100.0

        # River stage signal (binary exceedance)
        river_stage_signal = 1.0 if observation.river_stage_exceedance else 0.0

        # Optical change signal
        optical_change_signal = 0.0
        if observation.optical_change is not None:
            optical_change_signal = min(1.0, max(0.0, float(observation.optical_change)))

        # Elevation signal (protective factor - higher is better)
        elevation_signal = 0.0
        if observation.elevation_m is not None:
            elevation = float(observation.elevation_m)
            # Normalize: 0m = 1.0 (worst), 10m+ = 0.0 (best)
            if elevation < 10:
                elevation_signal = 1.0 - (elevation / 10.0)

        return {
            "flood_extent_signal": flood_extent_signal,
            "proximity_signal": proximity_signal,
            "rainfall_signal": rainfall_signal,
            "river_stage_signal": river_stage_signal,
            "optical_change_signal": optical_change_signal,
            "elevation_signal": elevation_signal,
        }

    def _calculate_confidence(
        self, observation: Observation | None, signals: dict[str, float]
    ) -> str:
        """Determine confidence level based on data availability and quality"""
        if not observation:
            return "low"

        # Count available data points
        data_points = 0
        if observation.flood_extent is not None:
            data_points += 1
        if observation.distance_to_flood_m is not None:
            data_points += 1
        if observation.rainfall_percentile is not None:
            data_points += 1
        if observation.river_stage_exceedance is not None:
            data_points += 1
        if observation.optical_change is not None:
            data_points += 1
        if observation.elevation_m is not None:
            data_points += 1

        # Check cloud quality
        low_cloud_quality = (
            observation.cloud_quality is not None and float(observation.cloud_quality) < 0.5
        )

        if data_points >= 5 and not low_cloud_quality:
            return "high"
        elif data_points >= 3:
            return "medium"
        else:
            return "low"

    def _get_data_sources(self, observation: Observation | None) -> dict[str, str]:
        """Extract data source references from observation"""
        if not observation:
            return {"status": "no observation data"}

        sources: dict[str, str] = {}
        if observation.sensor_source:
            sources["sensor"] = observation.sensor_source
        if observation.feature_payload:
            if "stac_item_id" in observation.feature_payload:
                sources["stac_item"] = observation.feature_payload["stac_item_id"]
            if "weather_source" in observation.feature_payload:
                sources["weather"] = observation.feature_payload["weather_source"]
            if "elevation_source" in observation.feature_payload:
                sources["elevation"] = observation.feature_payload["elevation_source"]

        return sources

    def _get_confidence_factors(self, observation: Observation | None) -> dict[str, str]:
        """Extract factors affecting confidence"""
        if not observation:
            return {"warning": "No observation data available"}

        factors: dict[str, str] = {}

        if observation.cloud_quality is not None:
            cloud_quality = float(observation.cloud_quality)
            if cloud_quality < 0.5:
                factors["cloud_cover"] = f"High cloud cover (quality: {cloud_quality:.2f})"
            else:
                factors["cloud_cover"] = f"Clear imagery (quality: {cloud_quality:.2f})"

        data_count = sum(
            [
                observation.flood_extent is not None,
                observation.distance_to_flood_m is not None,
                observation.rainfall_percentile is not None,
                observation.river_stage_exceedance is not None,
                observation.optical_change is not None,
                observation.elevation_m is not None,
            ]
        )
        factors["data_completeness"] = f"{data_count}/6 data sources available"

        return factors

    async def score_event(self, event_id: UUID, force_rescore: bool = False) -> dict[str, Any]:
        """Score all properties for a given event"""
        # Get all properties (simplified - in production would filter by event extent)
        result = await self.session.execute(select(Property))
        properties = result.scalars().all()

        scored_count = 0
        skipped_count = 0

        for prop in properties:
            # Check if already scored
            if not force_rescore:
                existing = await self.session.execute(
                    select(Score).where(
                        Score.property_id == prop.id,
                        Score.event_id == event_id,
                        Score.model_version == settings.MODEL_VERSION,
                    )
                )
                if existing.scalar_one_or_none():
                    skipped_count += 1
                    continue

            await self.score_property_for_event(prop.id, event_id)
            scored_count += 1

        await self.session.commit()

        return {
            "event_id": event_id,
            "scored_count": scored_count,
            "skipped_count": skipped_count,
            "total_properties": len(properties),
        }
