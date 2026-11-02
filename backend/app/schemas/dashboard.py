"""Dashboard statistics schema."""

from pydantic import BaseModel

from app.schemas.audit_logs import AuditLogRead


class DashboardStats(BaseModel):
    total_products: int
    total_stockists: int
    total_pincodes_assigned: int
    recent_activity: list[AuditLogRead]
