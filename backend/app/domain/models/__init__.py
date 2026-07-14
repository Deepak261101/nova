"""Domain entities (framework-agnostic)."""

from app.domain.models.chat import ChatMessage, MessageRole
from app.domain.models.conversation import Conversation, Message  # noqa: F401 (re-export)
from app.domain.models.memory import MemoryItem
from app.domain.models.user import AuthProvider, User, UserRole

__all__ = [
    "AuthProvider",
    "ChatMessage",
    "Conversation",
    "MemoryItem",
    "Message",
    "MessageRole",
    "User",
    "UserRole",
]
