from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class MessageRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ChatMessage(BaseModel):
    """A single message in an LLM prompt/completion exchange."""

    role: MessageRole
    content: str
    name: str | None = None
    tool_calls: list[dict] = Field(default_factory=list)
