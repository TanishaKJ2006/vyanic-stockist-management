"""Validated authentication request and response schemas."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class PublicRole(StrEnum):
    """Role allowed through public registration."""

    STOCKIST = "stockist"
    VIEWER = "viewer"


class UserRole(StrEnum):
    """Roles stored by the portal."""

    ADMIN = "admin"
    STOCKIST = "stockist"
    VIEWER = "viewer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    role: UserRole


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    role: PublicRole = PublicRole.STOCKIST

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("Name cannot be blank.")
        return normalized

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
