"""Property endpoints"""
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.base import get_db
from app.models import Property
from app.models.user import User
from app.schemas.property import Property as PropertySchema
from app.schemas.property import PropertyResponse

router = APIRouter(prefix="/properties", tags=["properties"])


@router.get("", response_model=list[PropertySchema])
async def list_properties(
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = 0,
    limit: int = 100,
) -> list[PropertySchema]:
    """List all properties"""
    result = await session.execute(select(Property).offset(skip).limit(limit))
    properties = result.scalars().all()

    return [PropertySchema.model_validate(prop) for prop in properties]


@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(
    property_id: UUID,
    session: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PropertyResponse:
    """Get property details"""
    result = await session.execute(select(Property).where(Property.id == property_id))
    prop = result.scalar_one_or_none()

    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")

    return PropertyResponse.model_validate(prop)
