"""Composition root / dependency-injection container.

Holds process-wide singletons (settings, database, providers). Per-request objects
(sessions, repositories, services) are built in ``app.api.deps`` from these.
"""

from __future__ import annotations

from app.adapters.factory import build_llm_provider, build_stt_provider, build_tts_provider
from app.core.config import Settings, get_settings
from app.db.session import Database
from app.domain.ports.providers import LLMProvider, STTProvider, TTSProvider


class Container:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings: Settings = settings or get_settings()
        self.db: Database = Database(self.settings)
        self.llm: LLMProvider = build_llm_provider(self.settings)
        self.stt: STTProvider = build_stt_provider(self.settings)
        self.tts: TTSProvider = build_tts_provider(self.settings)

    async def startup(self) -> None:
        await self.db.create_all()

    async def shutdown(self) -> None:
        await self.db.dispose()
