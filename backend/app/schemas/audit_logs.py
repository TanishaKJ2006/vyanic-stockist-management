"""MongoDB audit-log API schemas."""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel


class AuditAction(StrEnum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class AuditModule(StrEnum):
    PRODUCT = "Product"
    STOCKIST = "Stockist"
    PINCODE = "Pincode"


class AuditLogRead(BaseModel):
    id: str
    user_id: int
    user_email: str
    action: AuditAction
    module: AuditModule
    details: dict[str, Any]
    timestamp: datetime
