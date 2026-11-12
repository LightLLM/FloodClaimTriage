"""Event endpoints"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models import Event, Property, Score
from app.models.user import User
from app.schemas.event import Event as EventSchema
from app.schemas.event import EventCreate, EventResponse
from app.services.scoring import ScoringService

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[EventResponse])
async def list_events(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100,
) -> list[EventResponse]:
    """List all events with summary statistics"""
    result = await session.execute(select(Event).offset(skip).limit(limit).order_by(Event.event_date.desc()))
    events = result.scalars().all()

    response = []
    for event in events:
        # Get property count
        prop_count_result = await session.execute(
            select(func.count(Property.id))
        )
        property_count = prop_count_result.scalar_one()

        # Get scored count
        score_count_result = await session.execute(
            select(func.count(Score.id)).where(Score.event_id == event.id)
        )
        scored_count = score_count_result.scalar_one()

        response.append(
            EventResponse(
                id=event.id,
                event_type=event.event_type,
                name=event.name,
                event_date=event.event_date,
                geometry=None,  # Simplified for MVP
                stac_collection_id=event.stac_collection_id,
                status=event.status,
                created_at=event.created_at,
                property_count=property_count,
                scored_count=scored_count,
            )
        )

    return response


@router.post("", response_model=EventSchema, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: EventCreate,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> EventSchema:
    """Create a new flood event"""
    if current_user.role not in ["admin", "analyst"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create events",
        )

    event = Event(
        event_type=event_data.event_type,
        name=event_data.name,
        event_date=event_data.event_date,
        stac_collection_id=event_data.stac_collection_id,
        status="draft",
    )

    session.add(event)
    await session.commit()
    await session.refresh(event)

    return EventSchema.model_validate(event)


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> EventResponse:
    """Get event details"""
    result = await session.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    # Get counts
    prop_count_result = await session.execute(select(func.count(Property.id)))
    property_count = prop_count_result.scalar_one()

    score_count_result = await session.execute(
        select(func.count(Score.id)).where(Score.event_id == event.id)
    )
    scored_count = score_count_result.scalar_one()

    return EventResponse(
        id=event.id,
        event_type=event.event_type,
        name=event.name,
        event_date=event.event_date,
        geometry=None,
        stac_collection_id=event.stac_collection_id,
        status=event.status,
        created_at=event.created_at,
        property_count=property_count,
        scored_count=scored_count,
    )


@router.post("/{event_id}/score", response_model=dict)
async def score_event(
    event_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    force_rescore: bool = False,
) -> dict:
    """Score all properties for a given event"""
    if current_user.role not in ["admin", "analyst"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to score events",
        )

    # Verify event exists
    result = await session.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

    # Run scoring
    scoring_service = ScoringService(session)
    result_data = await scoring_service.score_event(event_id, force_rescore=force_rescore)

    return result_data
