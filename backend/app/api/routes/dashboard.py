"""Dashboard summary endpoint."""

from fastapi import APIRouter, Depends
from pymongo.collection import Collection
from sqlalchemy.orm import Session

from app.api.errors import raise_service_error
from app.auth.dependencies import get_current_user
from app.db import get_audit_logs_collection, get_db
from app.models import User
from app.schemas.dashboard import DashboardStats
from app.services.dashboard import get_dashboard_stats
from app.services.errors import ServiceError

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def read_dashboard_stats(
    db: Session = Depends(get_db),
    collection: Collection = Depends(get_audit_logs_collection),
    _: User = Depends(get_current_user),
) -> dict[str, object]:
    try:
        return get_dashboard_stats(db, collection)
    except ServiceError as exc:
        raise_service_error(exc)
