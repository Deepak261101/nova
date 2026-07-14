from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.models.chat import MessageRole


class Message(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    conversation_id: str
    role: MessageRole
    content: str
    # Optional structured payload (tool calls, citations, audio refs...)
    meta: dict = Field(default_factory=dict)
    created_at: datetime | None = None


class Conversation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str = "New conversation"
    created_at: datetime | None = None
    updated_at: datetime | None = None
    messages: list[Message] = Field(default_factory=list)
