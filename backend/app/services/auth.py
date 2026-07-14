"""Authentication use-cases: registration, login, token issue/refresh."""

from __future__ import annotations

from dataclasses import dataclass

import jwt

from app.core.config import Settings
from app.core.exceptions import AuthenticationError, ConflictError, NotFoundError
from app.core.security import create_token, decode_token, hash_password, verify_password
from app.domain.models.user import AuthProvider, User
from app.domain.ports.repositories import UserRepository


@dataclass(slots=True)
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthService:
    def __init__(self, users: UserRepository, settings: Settings) -> None:
        self._users = users
        self._settings = settings

    def _issue(self, user: User) -> TokenPair:
        claims = {"email": str(user.email), "role": user.role.value}
        return TokenPair(
            access_token=create_token(self._settings, user.id, "access", claims),
            refresh_token=create_token(self._settings, user.id, "refresh"),
        )

    async def register(
        self, email: str, password: str, display_name: str
    ) -> tuple[User, TokenPair]:
        existing = await self._users.get_by_email(email)
        if existing is not None:
            raise ConflictError("An account with that email already exists")
        user = await self._users.create(
            email=email,
            display_name=display_name or email.split("@")[0],
            auth_provider=AuthProvider.PASSWORD,
            password_hash=hash_password(password),
        )
        return user, self._issue(user)

    async def authenticate(self, email: str, password: str) -> tuple[User, TokenPair]:
        user = await self._users.get_by_email(email)
        if user is None:
            raise AuthenticationError()
        password_hash = await self._users.get_password_hash(user.id)
        if not password_hash or not verify_password(password, password_hash):
            raise AuthenticationError()
        if not user.is_active:
            raise AuthenticationError("Account is disabled")
        return user, self._issue(user)

    async def refresh(self, refresh_token: str) -> TokenPair:
        try:
            payload = decode_token(self._settings, refresh_token)
        except jwt.PyJWTError as exc:
            raise AuthenticationError("Invalid refresh token") from exc
        if payload.get("type") != "refresh":
            raise AuthenticationError("Not a refresh token")
        user = await self._users.get_by_id(payload["sub"])
        if user is None:
            raise AuthenticationError("Unknown user")
        return self._issue(user)

    async def user_from_access_token(self, token: str) -> User:
        try:
            payload = decode_token(self._settings, token)
        except jwt.PyJWTError as exc:
            raise AuthenticationError("Invalid access token") from exc
        if payload.get("type") != "access":
            raise AuthenticationError("Not an access token")
        user = await self._users.get_by_id(payload["sub"])
        if user is None:
            raise NotFoundError("User not found")
        return user

    async def upsert_oauth_user(
        self,
        *,
        email: str,
        display_name: str,
        provider: AuthProvider,
        avatar_url: str | None = None,
    ) -> tuple[User, TokenPair]:
        user = await self._users.get_by_email(email)
        if user is None:
            user = await self._users.create(
                email=email,
                display_name=display_name,
                auth_provider=provider,
                avatar_url=avatar_url,
            )
        return user, self._issue(user)
