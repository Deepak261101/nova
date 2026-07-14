"""SQLAlchemy ORM models (persistence representation)."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base import Base, TimestampMixin, UUIDMixin


class UserORM(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="user")
    auth_provider: Mapped[str] = mapped_column(String(20), default="password")
    avatar_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    settings: Mapped[dict] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(default=True)

    conversations: Mapped[list[ConversationORM]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    memories: Mapped[list[MemoryORM]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class ConversationORM(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "conversations"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200), default="New conversation")

    user: Mapped[UserORM] = relationship(back_populates="conversations")
    messages: Mapped[list[MessageORM]] = relationship(
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="MessageORM.created_at",
    )


class MessageORM(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "messages"

    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), index=True
    )
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(Text)
    meta: Mapped[dict] = mapped_column(JSON, default=dict)

    conversation: Mapped[ConversationORM] = relationship(back_populates="messages")


class MemoryORM(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "memories"
    __table_args__ = (UniqueConstraint("user_id", "key", name="uq_memory_user_key"),)

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    key: Mapped[str] = mapped_column(String(200))
    value: Mapped[str] = mapped_column(Text)
    importance: Mapped[int] = mapped_column(Integer, default=1)
    meta: Mapped[dict] = mapped_column(JSON, default=dict)

    user: Mapped[UserORM] = relationship(back_populates="memories")
