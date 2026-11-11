"""Triage and scoring endpoints"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models import AuditEvent, Event, Property, Score
from app.models.user import User
from app.schemas.score import TriageItem
from io import StringIO
import csv

router = APIRouter(tags=["triage"])


@router.get("/events/{event_id}/triage", response_model=list[TriageItem])
async def get_triage_queue(
    event_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    priority: str | None = Query(None, description="Filter by priority (P1, P2, P3)"),
    min_probability: float | None = Query(None, ge=0, le=1),
    skip: int = 0,
    limit: int = 100,
) -> list[TriageItem]:
    """Get triage queue for an event with filtering and sorting"""
    # Verify event exists
    result = await session.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    # Build query
    query = (
        select(Score, Property)
        .join(Property, Score.property_id == Property.id)
        .where(Score.event_id == event_id)
    )

    if priority:
        query = query.where(Score.inspection_priority == priority)

    if min_probability is not None:
        query = query.where(Score.damage_probability >= min_probability)

    # Order by priority then probability
    query = query.order_by(
        Score.inspection_priority.asc(), Score.damage_probability.desc()
    ).offset(skip).limit(limit)

    result = await session.execute(query)
    rows = result.all()

    triage_items = []
    for score, prop in rows:
        triage_items.append(
            TriageItem(
                property_id=prop.id,
                external_property_id=prop.external_property_id,
                geometry={},  # Simplified for MVP
                exposure_value=prop.exposure_value,
                damage_probability=score.damage_probability,
                inspection_priority=score.inspection_priority,
                recommended_action=score.recommended_action,
                created_at=score.created_at,
            )
        )

    return triage_items


@router.get("/events/{event_id}/properties/{property_id}/evidence", response_model=dict)
async def get_property_evidence(
    event_id: UUID,
    property_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    """Get detailed evidence for a property's score"""
    result = await session.execute(
        select(Score, Property)
        .join(Property, Score.property_id == Property.id)
        .where(Score.event_id == event_id, Score.property_id == property_id)
        .order_by(Score.created_at.desc())
        .limit(1)
    )
    row = result.first()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Score not found for this property"
        )

    score, prop = row

    return {
        "property_id": prop.id,
        "external_property_id": prop.external_property_id,
        "score": {
            "id": score.id,
            "damage_probability": float(score.damage_probability),
            "inspection_priority": score.inspection_priority,
            "recommended_action": score.recommended_action,
            "damage_confidence": score.damage_confidence,
            "model_version": score.model_version,
            "created_at": score.created_at,
        },
        "evidence": score.evidence,
        "property_details": {
            "building_type": prop.building_type,
            "exposure_value": float(prop.exposure_value) if prop.exposure_value else None,
            "region": prop.region,
        },
    }


@router.post("/scores/{score_id}/review", response_model=dict)
async def review_score(
    score_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    action: str = Query(..., description="accept or override"),
    reason: str | None = Query(None, description="Reason for override"),
    new_priority: str | None = Query(None, description="New priority if overriding (P1, P2, P3)"),
) -> dict:
    """Review and optionally override a score"""
    if current_user.role not in ["admin", "analyst", "reviewer"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to review scores",
        )

    # Get score
    result = await session.execute(select(Score).where(Score.id == score_id))
    score = result.scalar_one_or_none()

    if not score:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Score not found")

    before_value = {
        "inspection_priority": score.inspection_priority,
        "recommended_action": score.recommended_action,
    }

    after_value = before_value.copy()

    if action == "override" and new_priority:
        # Validate new priority
        if new_priority not in ["P1", "P2", "P3"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid priority value"
            )

        # Update score
        score.inspection_priority = new_priority

        # Update recommended action based on new priority
        if new_priority == "P1":
            score.recommended_action = "Field inspection (Human override)"
        elif new_priority == "P2":
            score.recommended_action = "Desk review (Human override)"
        else:
            score.recommended_action = "No action (Human override)"

        after_value = {
            "inspection_priority": score.inspection_priority,
            "recommended_action": score.recommended_action,
        }

    # Create audit event
    audit_event = AuditEvent(
        user_id=current_user.id,
        property_id=score.property_id,
        event_id=score.event_id,
        score_id=score.id,
        action=action,
        before_value=before_value,
        after_value=after_value,
        reason=reason,
    )

    session.add(audit_event)
    await session.commit()
    await session.refresh(score)

    return {
        "score_id": score.id,
        "action": action,
        "updated_priority": score.inspection_priority,
        "audit_event_id": audit_event.id,
    }


@router.get("/events/{event_id}/export.csv")
async def export_triage_csv(
    event_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> StreamingResponse:
    """Export triage queue as CSV"""
    # Verify event exists
    result = await session.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    # Get all scores for event
    query = (
        select(Score, Property)
        .join(Property, Score.property_id == Property.id)
        .where(Score.event_id == event_id)
        .order_by(Score.inspection_priority.asc(), Score.damage_probability.desc())
    )

    result = await session.execute(query)
    rows = result.all()

    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        "property_id",
        "external_property_id",
        "damage_probability",
        "inspection_priority",
        "recommended_action",
        "exposure_value",
        "building_type",
        "region",
        "confidence",
        "model_version",
    ])

    # Write data
    for score, prop in rows:
        writer.writerow([
            str(prop.id),
            prop.external_property_id,
            float(score.damage_probability),
            score.inspection_priority,
            score.recommended_action,
            float(prop.exposure_value) if prop.exposure_value else "",
            prop.building_type or "",
            prop.region or "",
            score.damage_confidence,
            score.model_version,
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=triage-export-{event.name}.csv"},
    )
