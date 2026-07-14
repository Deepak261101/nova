"""Long-term memory use-cases."""

from __future__ import annotations

from app.domain.models.memory import MemoryItem
from app.domain.ports.repositories import MemoryRepository


class MemoryService:
    def __init__(self, memories: MemoryRepository) -> None:
        self._memories = memories

    async def remember(self, user_id: str, key: str, value: str, importance: int = 1) -> MemoryItem:
        return await self._memories.upsert(user_id, key, value, importance)

    async def recall(self, user_id: str, limit: int = 100) -> list[MemoryItem]:
        return await self._memories.list_for_user(user_id, limit)

    async def forget(self, user_id: str, key: str) -> None:
        await self._memories.delete(user_id, key)

    async def as_prompt_context(self, user_id: str, limit: int = 20) -> str:
        """Render the user's memories as a compact system-prompt fragment."""
        items = await self._memories.list_for_user(user_id, limit)
        if not items:
            return ""
        lines = "\n".join(f"- {m.key}: {m.value}" for m in items)
        return f"Known facts about the user:\n{lines}"
