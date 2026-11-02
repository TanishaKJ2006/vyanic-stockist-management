"""Protected stockist and service-pincode endpoints."""

from fastapi import APIRouter, Depends, status
from pymongo.collection import Collection
from sqlalchemy.orm import Session

from app.api.errors import raise_service_error
from app.auth.dependencies import get_current_user, require_roles
from app.db import get_audit_logs_collection, get_db
from app.models import Stockist, StockistPincode, User
from app.schemas.stockists import PincodeCreate, PincodeRead, StockistCreate, StockistRead
from app.services.errors import ServiceError
from app.services.stockists import (
    assign_pincode,
    create_stockist,
    list_stockist_pincodes,
    list_stockists,
)

router = APIRouter(prefix="/stockists", tags=["stockists"])


@router.get("", response_model=list[StockistRead])
def read_stockists(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[Stockist]:
    try:
        return list_stockists(db)
    except ServiceError as exc:
        raise_service_error(exc)


@router.post("", response_model=StockistRead, status_code=status.HTTP_201_CREATED)
def add_stockist(
    payload: StockistCreate,
    db: Session = Depends(get_db),
    collection: Collection = Depends(get_audit_logs_collection),
    actor: User = Depends(require_roles("admin")),
) -> Stockist:
    try:
        return create_stockist(db, collection, actor, payload)
    except ServiceError as exc:
        raise_service_error(exc)


@router.post(
    "/{stockist_id}/pincodes",
    response_model=PincodeRead,
    status_code=status.HTTP_201_CREATED,
)
def add_pincode(
    stockist_id: int,
    payload: PincodeCreate,
    db: Session = Depends(get_db),
    collection: Collection = Depends(get_audit_logs_collection),
    actor: User = Depends(require_roles("admin")),
) -> StockistPincode:
    try:
        return assign_pincode(db, collection, actor, stockist_id, payload)
    except ServiceError as exc:
        raise_service_error(exc)


@router.get("/{stockist_id}/pincodes", response_model=list[PincodeRead])
def read_stockist_pincodes(
    stockist_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[StockistPincode]:
    try:
        return list_stockist_pincodes(db, stockist_id)
    except ServiceError as exc:
        raise_service_error(exc)
