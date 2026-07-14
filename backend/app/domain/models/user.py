from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRole(StrEnum):
    USER = "user"
    ADMIN = "admin"


class AuthProvider(StrEnum):
    PASSWORD = "password"
    GOOGLE = "google"
    GITHUB = "github"


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    display_name: str
    role: UserRole = UserRole.USER
    auth_provider: AuthProvider = AuthProvider.PASSWORD
    avatar_url: str | None = None
    # Free-form user settings/preferences (theme, voice, persona, etc.)
    settings: dict = Field(default_factory=dict)
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None
