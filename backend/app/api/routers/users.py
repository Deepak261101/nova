"""User profile & settings endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.repositories import SqlUserRepository
from app.api.deps import CurrentUser, get_session
from app.api.schemas import UpdateProfileRequest, UpdateSettingsRequest, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(user.model_dump())


@router.patch("/me", response_model=UserResponse)
async def update_profile(
    body: UpdateProfileRequest,
    user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserResponse:
    repo = SqlUserRepository(session)
    updated = await repo.update_profile(
        user.id, display_name=body.display_name, avatar_url=body.avatar_url
    )
    return UserResponse.model_validate(updated.model_dump())


@router.put("/me/settings", response_model=UserResponse)
async def update_settings(
    body: UpdateSettingsRequest,
    user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserResponse:
    repo = SqlUserRepository(session)
    updated = await repo.update_settings(user.id, body.settings)
    return UserResponse.model_validate(updated.model_dump())
