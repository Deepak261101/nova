"""A deterministic mock LLM provider.

Lets the whole app run (and be tested) with zero API keys. It echoes context and
produces a friendly, streaming-capable response so the voice/chat loop is fully
exercisable end-to-end.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

from app.domain.models.chat import ChatMessage, MessageRole
from app.domain.ports.providers import LLMProvider, ToolSpec


class MockLLMProvider(LLMProvider):
    def __init__(self, *, delay: float = 0.02) -> None:
        self._delay = delay

    def _reply_text(self, messages: list[ChatMessage]) -> str:
        last_user = next(
            (m.content for m in reversed(messages) if m.role == MessageRole.USER),
            "",
        )
        if not last_user.strip():
            return "Hi, I'm Nova. How can I help you today?"
        return (
            f"You said: \u201c{last_user.strip()}\u201d. "
            "I'm Nova running in mock mode \u2014 wire up a real LLM provider "
            "(set NOVA_LLM_PROVIDER and an API key) for full responses."
        )

    async def complete(
        self,
        messages: list[ChatMessage],
        *,
        tools: list[ToolSpec] | None = None,
        temperature: float = 0.7,
    ) -> ChatMessage:
        return ChatMessage(role=MessageRole.ASSISTANT, content=self._reply_text(messages))

    async def stream(
        self,
        messages: list[ChatMessage],
        *,
        tools: list[ToolSpec] | None = None,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        for token in self._reply_text(messages).split(" "):
            await asyncio.sleep(self._delay)
            yield token + " "
