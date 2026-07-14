"""FastAPI dependency providers wiring the DI container to requests."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.db.repositories import (
    SqlConversationRepository,
    SqlMemoryRepository,
    SqlUserRepository,
)
from app.core.container import Container
from app.core.exceptions import AuthenticationError
from app.domain.models.user import User
from app.services.auth import AuthService
from app.services.conversation import ConversationService
from app.services.memory import MemoryService
from app.services.voice import VoiceService

_bearer = HTTPBearer(auto_error=False)


def get_container(request: Request) -> Container:
    return request.app.state.container


async def get_session(
    container: Annotated[Container, Depends(get_container)],
) -> AsyncIterator[AsyncSession]:
    async for session in container.db.session():
        yield session


def get_auth_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    container: Annotated[Container, Depends(get_container)],
) -> AuthService:
    return AuthService(SqlUserRepository(session), container.settings)


def get_memory_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MemoryService:
    return MemoryService(SqlMemoryRepository(session))


def get_conversation_service(
    session: Annotated[AsyncSession, Depends(get_session)],
    container: Annotated[Container, Depends(get_container)],
    memory: Annotated[MemoryService, Depends(get_memory_service)],
) -> ConversationService:
    return ConversationService(SqlConversationRepository(session), container.llm, memory)


def get_voice_service(
    container: Annotated[Container, Depends(get_container)],
    conversations: Annotated[ConversationService, Depends(get_conversation_service)],
) -> VoiceService:
    return VoiceService(container.stt, container.tts, conversations)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    auth: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    if credentials is None:
        raise AuthenticationError("Missing bearer token")
    return await auth.user_from_access_token(credentials.credentials)


CurrentUser = Annotated[User, Depends(get_current_user)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
ConversationServiceDep = Annotated[ConversationService, Depends(get_conversation_service)]
MemoryServiceDep = Annotated[MemoryService, Depends(get_memory_service)]
VoiceServiceDep = Annotated[VoiceService, Depends(get_voice_service)]
