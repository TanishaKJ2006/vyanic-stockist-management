"""Stockist and service-pincode API schemas."""

import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class StockistCreate(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    contact_email: EmailStr
    contact_phone: str = Field(min_length=7, max_length=32)
    city: str = Field(min_length=1, max_length=120)

    @field_validator("name", "city")
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("This field cannot be blank.")
        return normalized

    @field_validator("contact_email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("contact_phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not re.fullmatch(r"\+?[0-9\s().-]+", normalized):
            raise ValueError("Enter a valid phone number.")
        digits = re.sub(r"\D", "", normalized)
        if not 7 <= len(digits) <= 15:
            raise ValueError("Phone number must contain 7 to 15 digits.")
        return normalized


class StockistRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    contact_email: EmailStr
    contact_phone: str
    city: str
    created_at: datetime


class PincodeCreate(BaseModel):
    pincode: str = Field(min_length=6, max_length=6)
    state: str = Field(min_length=1, max_length=120)

    @field_validator("pincode")
    @classmethod
    def validate_pincode(cls, value: str) -> str:
        normalized = value.strip()
        if not re.fullmatch(r"[0-9]{6}", normalized):
            raise ValueError("Pincode must contain exactly 6 digits.")
        return normalized

    @field_validator("state")
    @classmethod
    def normalize_state(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("State cannot be blank.")
        return normalized


class PincodeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    stockist_id: int
    pincode: str
    state: str
    created_at: datetime
