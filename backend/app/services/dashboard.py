"""Dashboard aggregates backed by SQL and MongoDB."""

from pymongo.collection import Collection
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Product, Stockist, StockistPincode
from app.services.audit_logs import read_latest_audit_logs
from app.services.errors import DatabaseReadError


def get_dashboard_stats(db: Session, collection: Collection) -> dict[str, object]:
    try:
        total_products = db.scalar(select(func.count()).select_from(Product)) or 0
        total_stockists = db.scalar(select(func.count()).select_from(Stockist)) or 0
        total_pincodes = db.scalar(
            select(func.count()).select_from(StockistPincode)
        ) or 0
    except SQLAlchemyError as exc:
        raise DatabaseReadError from exc

    recent_activity = read_latest_audit_logs(collection, limit=5)
    return {
        "total_products": total_products,
        "total_stockists": total_stockists,
        "total_pincodes_assigned": total_pincodes,
        "recent_activity": recent_activity,
    }
