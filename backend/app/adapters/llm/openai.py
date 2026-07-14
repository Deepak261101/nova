"""OpenAI chat-completions LLM adapter (used when NOVA_LLM_PROVIDER=openai).

Implemented with httpx directly to avoid pinning a heavy SDK. Streaming uses the
SSE ``chat/completions`` API.
"""

from __future__ import annotations

import json
import os
from collections.abc import AsyncIterator

import httpx

from app.domain.models.chat import ChatMessage, MessageRole
from app.domain.ports.providers import LLMProvider, ToolSpec

_API = "https://api.openai.com/v1/chat/completions"


class OpenAILLMProvider(LLMProvider):
    def __init__(self, *, model: str, api_key: str | None = None) -> None:
        self._model = model
        self._api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        if not self._api_key:
            raise ValueError("OPENAI_API_KEY is required for the OpenAI LLM provider")

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}

    @staticmethod
    def _dump(messages: list[ChatMessage]) -> list[dict]:
        return [{"role": m.role.value, "content": m.content} for m in messages]

    async def complete(
        self,
        messages: list[ChatMessage],
        *,
        tools: list[ToolSpec] | None = None,
        temperature: float = 0.7,
    ) -> ChatMessage:
        payload = {
            "model": self._model,
            "messages": self._dump(messages),
            "temperature": temperature,
        }
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(_API, headers=self._headers(), json=payload)
            resp.raise_for_status()
            data = resp.json()
        content = data["choices"][0]["message"]["content"]
        return ChatMessage(role=MessageRole.ASSISTANT, content=content)

    async def stream(
        self,
        messages: list[ChatMessage],
        *,
        tools: list[ToolSpec] | None = None,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        payload = {
            "model": self._model,
            "messages": self._dump(messages),
            "temperature": temperature,
            "stream": True,
        }
        async with (
            httpx.AsyncClient(timeout=None) as client,
            client.stream("POST", _API, headers=self._headers(), json=payload) as resp,
        ):
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line or not line.startswith("data: "):
                    continue
                chunk = line.removeprefix("data: ").strip()
                if chunk == "[DONE]":
                    break
                try:
                    delta = json.loads(chunk)["choices"][0]["delta"].get("content")
                except (KeyError, IndexError, json.JSONDecodeError):
                    continue
                if delta:
                    yield delta
