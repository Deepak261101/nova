from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MemoryItem(BaseModel):
    """A long-term memory fact associated with a user.

    Phase 1 stores plain key/value facts; Phase 2+ adds embeddings for semantic recall.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    key: str
    value: str
    importance: int = 1
    meta: dict = Field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None
