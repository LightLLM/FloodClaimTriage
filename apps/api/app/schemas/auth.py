"""Authentication schemas"""
from uuid import UUID

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Login request schema"""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class LoginResponse(TokenResponse):
    """Login response schema"""

    user_id: UUID
    email: str
    full_name: str
    role: str


class TokenRefreshRequest(BaseModel):
    """Token refresh request schema"""

    refresh_token: str
