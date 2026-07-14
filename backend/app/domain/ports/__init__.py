"""Port interfaces — the boundaries the core depends on.

Adapters in ``app.adapters`` implement these so infrastructure/providers are
swappable and the domain stays framework-free.
"""

from app.domain.ports.providers import (
    LLMProvider,
    STTProvider,
    ToolSpec,
    TTSProvider,
)
from app.domain.ports.repositories import (
    ConversationRepository,
    MemoryRepository,
    UserRepository,
)

__all__ = [
    "ConversationRepository",
    "LLMProvider",
    "MemoryRepository",
    "STTProvider",
    "TTSProvider",
    "ToolSpec",
    "UserRepository",
]
