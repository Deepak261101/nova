"""Factories that select provider adapters based on configuration.

Unknown/unset providers fall back to the mock implementations so the app always
runs. This keeps provider selection in one place (open/closed for new providers).
"""

from __future__ import annotations

from app.core.config import Settings
from app.core.logging import get_logger
from app.domain.ports.providers import LLMProvider, STTProvider, TTSProvider

log = get_logger(__name__)


def build_llm_provider(settings: Settings) -> LLMProvider:
    provider = settings.llm_provider.lower()
    if provider == "openai":
        try:
            from app.adapters.llm.openai import OpenAILLMProvider

            return OpenAILLMProvider(model=settings.llm_model)
        except Exception as exc:  # missing key / import error -> safe fallback
            log.warning("llm_provider_fallback", requested=provider, error=str(exc))
    from app.adapters.llm.mock import MockLLMProvider

    return MockLLMProvider()


def build_stt_provider(settings: Settings) -> STTProvider:
    # Only the mock provider ships in Phase 1; real providers plug in here.
    from app.adapters.stt.mock import MockSTTProvider

    return MockSTTProvider()


def build_tts_provider(settings: Settings) -> TTSProvider:
    from app.adapters.tts.mock import MockTTSProvider

    return MockTTSProvider()
