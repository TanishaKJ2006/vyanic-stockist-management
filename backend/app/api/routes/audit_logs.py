"""Read-only audit-log endpoint required by the assignment."""

from fastapi import APIRouter, Depends
from pymongo.collection import Collection

from app.api.errors import raise_service_error
from app.auth.dependencies import get_current_user
from app.db import get_audit_logs_collection
from app.models import User
from app.schemas.audit_logs import AuditLogRead
from app.services.audit_logs import read_latest_audit_logs
from app.services.errors import ServiceError

router = APIRouter(prefix="/audit-logs", tags=["audit logs"])


@router.get("", response_model=list[AuditLogRead])
def read_audit_logs(
    collection: Collection = Depends(get_audit_logs_collection),
    _: User = Depends(get_current_user),
) -> list[dict[str, object]]:
    try:
        return read_latest_audit_logs(collection, limit=50)
    except ServiceError as exc:
        raise_service_error(exc)
