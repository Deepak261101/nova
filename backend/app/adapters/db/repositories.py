"""SQLAlchemy implementations of the repository ports."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import ConversationORM, MemoryORM, MessageORM, UserORM
from app.domain.models.conversation import Conversation, Message, MessageRole
from app.domain.models.memory import MemoryItem
from app.domain.models.user import AuthProvider, User
from app.domain.ports.repositories import (
    ConversationRepository,
    MemoryRepository,
    UserRepository,
)


def _to_user(orm: UserORM) -> User:
    return User.model_validate(orm)


def _to_message(orm: MessageORM) -> Message:
    return Message(
        id=orm.id,
        conversation_id=orm.conversation_id,
        role=MessageRole(orm.role),
        content=orm.content,
        meta=orm.meta or {},
        created_at=orm.created_at,
    )


def _to_conversation(orm: ConversationORM, *, with_messages: bool = False) -> Conversation:
    return Conversation(
        id=orm.id,
        user_id=orm.user_id,
        title=orm.title,
        created_at=orm.created_at,
        updated_at=orm.updated_at,
        messages=[_to_message(m) for m in orm.messages] if with_messages else [],
    )


class SqlUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: str) -> User | None:
        orm = await self._session.get(UserORM, user_id)
        return _to_user(orm) if orm else None

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(select(UserORM).where(UserORM.email == email))
        orm = result.scalar_one_or_none()
        return _to_user(orm) if orm else None

    async def get_password_hash(self, user_id: str) -> str | None:
        orm = await self._session.get(UserORM, user_id)
        return orm.password_hash if orm else None

    async def create(
        self,
        *,
        email: str,
        display_name: str,
        auth_provider: AuthProvider,
        password_hash: str | None = None,
        avatar_url: str | None = None,
    ) -> User:
        orm = UserORM(
            email=email,
            display_name=display_name,
            auth_provider=auth_provider.value,
            password_hash=password_hash,
            avatar_url=avatar_url,
            settings={},
        )
        self._session.add(orm)
        await self._session.commit()
        await self._session.refresh(orm)
        return _to_user(orm)

    async def update_settings(self, user_id: str, settings: dict) -> User:
        orm = await self._session.get(UserORM, user_id)
        if orm is None:
            raise ValueError("user not found")
        merged = {**(orm.settings or {}), **settings}
        orm.settings = merged
        await self._session.commit()
        await self._session.refresh(orm)
        return _to_user(orm)

    async def update_profile(
        self, user_id: str, *, display_name: str | None = None, avatar_url: str | None = None
    ) -> User:
        orm = await self._session.get(UserORM, user_id)
        if orm is None:
            raise ValueError("user not found")
        if display_name is not None:
            orm.display_name = display_name
        if avatar_url is not None:
            orm.avatar_url = avatar_url
        await self._session.commit()
        await self._session.refresh(orm)
        return _to_user(orm)


class SqlConversationRepository(ConversationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, user_id: str, title: str = "New conversation") -> Conversation:
        orm = ConversationORM(user_id=user_id, title=title)
        self._session.add(orm)
        await self._session.commit()
        await self._session.refresh(orm)
        # A freshly-created conversation has no messages; avoid a lazy relationship load.
        return _to_conversation(orm, with_messages=False)

    async def get(self, conversation_id: str, user_id: str) -> Conversation | None:
        result = await self._session.execute(
            select(ConversationORM)
            .where(ConversationORM.id == conversation_id, ConversationORM.user_id == user_id)
            .options(selectinload(ConversationORM.messages))
        )
        orm = result.scalar_one_or_none()
        return _to_conversation(orm, with_messages=True) if orm else None

    async def list_for_user(self, user_id: str, limit: int = 50) -> list[Conversation]:
        result = await self._session.execute(
            select(ConversationORM)
            .where(ConversationORM.user_id == user_id)
            .order_by(ConversationORM.updated_at.desc())
            .limit(limit)
        )
        return [_to_conversation(o) for o in result.scalars().all()]

    async def add_message(
        self,
        conversation_id: str,
        role: MessageRole,
        content: str,
        meta: dict | None = None,
    ) -> Message:
        orm = MessageORM(
            conversation_id=conversation_id,
            role=role.value,
            content=content,
            meta=meta or {},
        )
        self._session.add(orm)
        await self._session.commit()
        await self._session.refresh(orm)
        return _to_message(orm)

    async def rename(self, conversation_id: str, user_id: str, title: str) -> None:
        result = await self._session.execute(
            select(ConversationORM).where(
                ConversationORM.id == conversation_id, ConversationORM.user_id == user_id
            )
        )
        orm = result.scalar_one_or_none()
        if orm is not None:
            orm.title = title
            await self._session.commit()

    async def delete(self, conversation_id: str, user_id: str) -> None:
        result = await self._session.execute(
            select(ConversationORM).where(
                ConversationORM.id == conversation_id, ConversationORM.user_id == user_id
            )
        )
        orm = result.scalar_one_or_none()
        if orm is not None:
            await self._session.delete(orm)
            await self._session.commit()


class SqlMemoryRepository(MemoryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert(self, user_id: str, key: str, value: str, importance: int = 1) -> MemoryItem:
        result = await self._session.execute(
            select(MemoryORM).where(MemoryORM.user_id == user_id, MemoryORM.key == key)
        )
        orm = result.scalar_one_or_none()
        if orm is None:
            orm = MemoryORM(user_id=user_id, key=key, value=value, importance=importance)
            self._session.add(orm)
        else:
            orm.value = value
            orm.importance = importance
        await self._session.commit()
        await self._session.refresh(orm)
        return MemoryItem.model_validate(orm)

    async def list_for_user(self, user_id: str, limit: int = 100) -> list[MemoryItem]:
        result = await self._session.execute(
            select(MemoryORM)
            .where(MemoryORM.user_id == user_id)
            .order_by(MemoryORM.importance.desc(), MemoryORM.updated_at.desc())
            .limit(limit)
        )
        return [MemoryItem.model_validate(o) for o in result.scalars().all()]

    async def delete(self, user_id: str, key: str) -> None:
        result = await self._session.execute(
            select(MemoryORM).where(MemoryORM.user_id == user_id, MemoryORM.key == key)
        )
        orm = result.scalar_one_or_none()
        if orm is not None:
            await self._session.delete(orm)
            await self._session.commit()
