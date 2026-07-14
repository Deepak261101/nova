"""Long-term memory endpoints."""

from __future__ import annotations

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, MemoryServiceDep
from app.api.schemas import MemoryResponse, MemoryUpsertRequest

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("", response_model=list[MemoryResponse])
async def list_memory(user: CurrentUser, memory: MemoryServiceDep) -> list[MemoryResponse]:
    items = await memory.recall(user.id)
    return [MemoryResponse.model_validate(i.model_dump()) for i in items]


@router.put("", response_model=MemoryResponse)
async def upsert_memory(
    body: MemoryUpsertRequest, user: CurrentUser, memory: MemoryServiceDep
) -> MemoryResponse:
    item = await memory.remember(user.id, body.key, body.value, body.importance)
    return MemoryResponse.model_validate(item.model_dump())


@router.delete("/{key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(key: str, user: CurrentUser, memory: MemoryServiceDep) -> None:
    await memory.forget(user.id, key)
