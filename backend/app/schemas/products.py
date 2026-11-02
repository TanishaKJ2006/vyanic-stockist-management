"""Product API schemas."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductWrite(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    sku_code: str = Field(min_length=1, max_length=64)
    category: str = Field(min_length=1, max_length=120)
    price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    stock_quantity: int = Field(ge=0, strict=True)

    @field_validator("name", "category")
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("This field cannot be blank.")
        return normalized

    @field_validator("sku_code")
    @classmethod
    def normalize_sku(cls, value: str) -> str:
        normalized = value.strip().upper()
        if not normalized:
            raise ValueError("SKU code cannot be blank.")
        return normalized


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sku_code: str
    category: str
    price: Decimal
    stock_quantity: int
    created_at: datetime


class ProductPage(BaseModel):
    items: list[ProductRead]
    total: int
    page: int
    limit: int
    pages: int
