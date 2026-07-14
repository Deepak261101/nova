"""Provider ports: LLM, STT, TTS."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field

from app.domain.models.chat import ChatMessage


@dataclass(slots=True)
class ToolSpec:
    """A JSON-schema tool definition offered to the LLM for function calling."""

    name: str
    description: str
    parameters: dict = field(default_factory=dict)


class LLMProvider(ABC):
    """Large-language-model provider abstraction."""

    @abstractmethod
    async def complete(
        self,
        messages: list[ChatMessage],
        *,
        tools: list[ToolSpec] | None = None,
        temperature: float = 0.7,
    ) -> ChatMessage:
        """Return a single completion for the given messages."""

    @abstractmethod
    def stream(
        self,
        messages: list[ChatMessage],
        *,
        tools: list[ToolSpec] | None = None,
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Yield completion token deltas as they are produced."""


class STTProvider(ABC):
    """Speech-to-text provider abstraction."""

    @abstractmethod
    async def transcribe(self, audio: bytes, *, sample_rate: int = 16000) -> str:
        """Transcribe a complete audio buffer to text."""


class TTSProvider(ABC):
    """Text-to-speech provider abstraction."""

    @abstractmethod
    async def synthesize(self, text: str, *, voice: str = "nova") -> bytes:
        """Synthesize text to an audio buffer (e.g. WAV/PCM bytes)."""
