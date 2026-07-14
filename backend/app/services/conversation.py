"""Conversation use-cases: history, streaming chat, titling."""

from __future__ import annotations

from collections.abc import AsyncIterator

from app.core.exceptions import NotFoundError
from app.domain.models.chat import ChatMessage, MessageRole
from app.domain.models.conversation import Conversation, Message
from app.domain.ports.providers import LLMProvider
from app.domain.ports.repositories import ConversationRepository
from app.services.memory import MemoryService

SYSTEM_PROMPT = (
    "You are Nova, a helpful, concise, and friendly AI voice assistant. "
    "Answer clearly. When the user asks you to perform an action that is destructive, "
    "financial, or otherwise risky, always ask for explicit confirmation first."
)


class ConversationService:
    def __init__(
        self,
        conversations: ConversationRepository,
        llm: LLMProvider,
        memory: MemoryService,
    ) -> None:
        self._conversations = conversations
        self._llm = llm
        self._memory = memory

    async def create(self, user_id: str, title: str = "New conversation") -> Conversation:
        return await self._conversations.create(user_id, title)

    async def list_all(self, user_id: str) -> list[Conversation]:
        return await self._conversations.list_for_user(user_id)

    async def get(self, conversation_id: str, user_id: str) -> Conversation:
        convo = await self._conversations.get(conversation_id, user_id)
        if convo is None:
            raise NotFoundError("Conversation not found")
        return convo

    async def rename(self, conversation_id: str, user_id: str, title: str) -> None:
        await self._conversations.rename(conversation_id, user_id, title)

    async def delete(self, conversation_id: str, user_id: str) -> None:
        await self._conversations.delete(conversation_id, user_id)

    async def _build_prompt(self, convo: Conversation, user_id: str) -> list[ChatMessage]:
        system = SYSTEM_PROMPT
        mem = await self._memory.as_prompt_context(user_id)
        if mem:
            system = f"{system}\n\n{mem}"
        prompt: list[ChatMessage] = [ChatMessage(role=MessageRole.SYSTEM, content=system)]
        for m in convo.messages:
            if m.role in (MessageRole.USER, MessageRole.ASSISTANT):
                prompt.append(ChatMessage(role=m.role, content=m.content))
        return prompt

    async def stream_reply(
        self, conversation_id: str, user_id: str, user_text: str
    ) -> AsyncIterator[str]:
        """Persist the user turn, stream the assistant reply, then persist it."""
        convo = await self.get(conversation_id, user_id)
        await self._conversations.add_message(conversation_id, MessageRole.USER, user_text)
        # Re-fetch so the new user message is part of the prompt.
        convo = await self.get(conversation_id, user_id)
        prompt = await self._build_prompt(convo, user_id)

        chunks: list[str] = []
        async for delta in self._llm.stream(prompt):
            chunks.append(delta)
            yield delta

        full = "".join(chunks).strip()
        await self._conversations.add_message(conversation_id, MessageRole.ASSISTANT, full)

        # Auto-title on the first exchange.
        if convo.title == "New conversation":
            title = user_text.strip()[:60] or "New conversation"
            await self._conversations.rename(conversation_id, user_id, title)

    async def reply(self, conversation_id: str, user_id: str, user_text: str) -> Message:
        """Non-streaming variant used by the voice loop and tests."""
        convo = await self.get(conversation_id, user_id)
        await self._conversations.add_message(conversation_id, MessageRole.USER, user_text)
        convo = await self.get(conversation_id, user_id)
        prompt = await self._build_prompt(convo, user_id)
        completion = await self._llm.complete(prompt)
        message = await self._conversations.add_message(
            conversation_id, MessageRole.ASSISTANT, completion.content
        )
        if convo.title == "New conversation":
            await self._conversations.rename(
                conversation_id, user_id, user_text.strip()[:60] or "New conversation"
            )
        return message
