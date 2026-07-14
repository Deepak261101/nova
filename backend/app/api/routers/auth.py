"""Authentication endpoints: register, login, refresh, me."""

from __future__ import annotations

from fastapi import APIRouter, status

from app.api.deps import AuthServiceDep, CurrentUser
from app.api.schemas import (
    AuthResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, auth: AuthServiceDep) -> AuthResponse:
    user, tokens = await auth.register(body.email, body.password, body.display_name)
    return AuthResponse(
        user=UserResponse.model_validate(user.model_dump()),
        tokens=TokenResponse(access_token=tokens.access_token, refresh_token=tokens.refresh_token),
    )


@router.post("/login", response_model=AuthResponse)
async def login(body: LoginRequest, auth: AuthServiceDep) -> AuthResponse:
    user, tokens = await auth.authenticate(body.email, body.password)
    return AuthResponse(
        user=UserResponse.model_validate(user.model_dump()),
        tokens=TokenResponse(access_token=tokens.access_token, refresh_token=tokens.refresh_token),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, auth: AuthServiceDep) -> TokenResponse:
    tokens = await auth.refresh(body.refresh_token)
    return TokenResponse(access_token=tokens.access_token, refresh_token=tokens.refresh_token)


@router.get("/me", response_model=UserResponse)
async def me(user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(user.model_dump())
