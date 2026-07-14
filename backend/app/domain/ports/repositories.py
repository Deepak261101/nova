"""Repository ports for persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.models.conversation import Conversation, Message, MessageRole
from app.domain.models.memory import MemoryItem
from app.domain.models.user import AuthProvider, User


class UserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: str) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def get_password_hash(self, user_id: str) -> str | None: ...

    @abstractmethod
    async def create(
        self,
        *,
        email: str,
        display_name: str,
        auth_provider: AuthProvider,
        password_hash: str | None = None,
        avatar_url: str | None = None,
    ) -> User: ...

    @abstractmethod
    async def update_settings(self, user_id: str, settings: dict) -> User: ...

    @abstractmethod
    async def update_profile(
        self, user_id: str, *, display_name: str | None = None, avatar_url: str | None = None
    ) -> User: ...


class ConversationRepository(ABC):
    @abstractmethod
    async def create(self, user_id: str, title: str = "New conversation") -> Conversation: ...

    @abstractmethod
    async def get(self, conversation_id: str, user_id: str) -> Conversation | None: ...

    @abstractmethod
    async def list_for_user(self, user_id: str, limit: int = 50) -> list[Conversation]: ...

    @abstractmethod
    async def add_message(
        self,
        conversation_id: str,
        role: MessageRole,
        content: str,
        meta: dict | None = None,
    ) -> Message: ...

    @abstractmethod
    async def rename(self, conversation_id: str, user_id: str, title: str) -> None: ...

    @abstractmethod
    async def delete(self, conversation_id: str, user_id: str) -> None: ...


class MemoryRepository(ABC):
    @abstractmethod
    async def upsert(
        self, user_id: str, key: str, value: str, importance: int = 1
    ) -> MemoryItem: ...

    @abstractmethod
    async def list_for_user(self, user_id: str, limit: int = 100) -> list[MemoryItem]: ...

    @abstractmethod
    async def delete(self, user_id: str, key: str) -> None: ...
