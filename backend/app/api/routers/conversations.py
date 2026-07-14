"""Conversation CRUD + streaming chat (SSE)."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, status
from fastapi.responses import StreamingResponse

from app.api.deps import ConversationServiceDep, CurrentUser
from app.api.schemas import (
    ChatRequest,
    ConversationDetail,
    ConversationSummary,
    CreateConversationRequest,
    MessageResponse,
    RenameConversationRequest,
)

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=list[ConversationSummary])
async def list_conversations(
    user: CurrentUser, service: ConversationServiceDep
) -> list[ConversationSummary]:
    convos = await service.list_all(user.id)
    return [ConversationSummary.model_validate(c.model_dump()) for c in convos]


@router.post("", response_model=ConversationDetail, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    body: CreateConversationRequest, user: CurrentUser, service: ConversationServiceDep
) -> ConversationDetail:
    convo = await service.create(user.id, body.title)
    return ConversationDetail.model_validate(convo.model_dump())


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: str, user: CurrentUser, service: ConversationServiceDep
) -> ConversationDetail:
    convo = await service.get(conversation_id, user.id)
    return ConversationDetail.model_validate(convo.model_dump())


@router.patch("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def rename_conversation(
    conversation_id: str,
    body: RenameConversationRequest,
    user: CurrentUser,
    service: ConversationServiceDep,
) -> None:
    await service.rename(conversation_id, user.id, body.title)


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: str, user: CurrentUser, service: ConversationServiceDep
) -> None:
    await service.delete(conversation_id, user.id)


@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: str,
    body: ChatRequest,
    user: CurrentUser,
    service: ConversationServiceDep,
) -> MessageResponse:
    """Non-streaming send: returns the full assistant message."""
    message = await service.reply(conversation_id, user.id, body.message)
    return MessageResponse.model_validate(message.model_dump())


@router.post("/{conversation_id}/stream")
async def stream_message(
    conversation_id: str,
    body: ChatRequest,
    user: CurrentUser,
    service: ConversationServiceDep,
) -> StreamingResponse:
    """Server-Sent Events stream of assistant token deltas."""

    async def event_source() -> AsyncIterator[bytes]:
        async for delta in service.stream_reply(conversation_id, user.id, body.message):
            yield f"data: {json.dumps({'delta': delta})}\n\n".encode()
        yield b"event: done\ndata: {}\n\n"

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
