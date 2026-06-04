"""User schemas for authentication endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# --- Request schemas (what the client sends) ---

class UserRegister(BaseModel):
    """POST /auth/register request body."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=100)


class UserLogin(BaseModel):
    """POST /auth/login request body."""
    email: EmailStr
    password: str


# --- Response schemas (what the API returns) ---

class UserResponse(BaseModel):
    """User data returned to the client (no password hash!)."""
    id: uuid.UUID
    email: str
    full_name: str | None
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """JWT tokens returned after login/register."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """POST /auth/refresh request body."""
    refresh_token: str
