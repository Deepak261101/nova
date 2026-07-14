"""API request/response schemas (DTOs)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.domain.models.chat import MessageRole


# --- Auth ---
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(default="", max_length=120)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# --- Users ---
class UserResponse(BaseModel):
    id: str
    email: EmailStr
    display_name: str
    role: str
    auth_provider: str
    avatar_url: str | None = None
    settings: dict = Field(default_factory=dict)


class UpdateProfileRequest(BaseModel):
    display_name: str | None = Field(default=None, max_length=120)
    avatar_url: str | None = None


class UpdateSettingsRequest(BaseModel):
    settings: dict


# --- Conversations ---
class CreateConversationRequest(BaseModel):
    title: str = "New conversation"


class RenameConversationRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)


class MessageResponse(BaseModel):
    id: str
    role: MessageRole
    content: str
    meta: dict = Field(default_factory=dict)
    created_at: datetime | None = None


class ConversationSummary(BaseModel):
    id: str
    title: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ConversationDetail(ConversationSummary):
    messages: list[MessageResponse] = Field(default_factory=list)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)


# --- Memory ---
class MemoryUpsertRequest(BaseModel):
    key: str = Field(min_length=1, max_length=200)
    value: str = Field(min_length=1)
    importance: int = 1


class MemoryResponse(BaseModel):
    id: str
    key: str
    value: str
    importance: int


# --- Auth response bundle ---
class AuthResponse(BaseModel):
    user: UserResponse
    tokens: TokenResponse
