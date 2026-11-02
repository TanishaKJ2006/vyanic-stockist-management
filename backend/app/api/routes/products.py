"""Protected product catalog endpoints."""

from fastapi import APIRouter, Depends, Query, Response, status
from pymongo.collection import Collection
from sqlalchemy.orm import Session

from app.api.errors import raise_service_error
from app.auth.dependencies import get_current_user, require_roles
from app.db import get_audit_logs_collection, get_db
from app.models import Product, User
from app.schemas.products import ProductPage, ProductRead, ProductWrite
from app.services.errors import ServiceError
from app.services.products import (
    create_product,
    delete_product,
    list_products,
    update_product,
)

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=ProductPage)
def read_products(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    search: str | None = Query(default=None, max_length=120),
    category: str | None = Query(default=None, max_length=120),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> dict[str, object]:
    try:
        return list_products(
            db,
            page=page,
            limit=limit,
            search=search,
            category=category,
        )
    except ServiceError as exc:
        raise_service_error(exc)


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def add_product(
    payload: ProductWrite,
    db: Session = Depends(get_db),
    collection: Collection = Depends(get_audit_logs_collection),
    actor: User = Depends(require_roles("admin")),
) -> Product:
    try:
        return create_product(db, collection, actor, payload)
    except ServiceError as exc:
        raise_service_error(exc)


@router.put("/{product_id}", response_model=ProductRead)
def edit_product(
    product_id: int,
    payload: ProductWrite,
    db: Session = Depends(get_db),
    collection: Collection = Depends(get_audit_logs_collection),
    actor: User = Depends(require_roles("admin")),
) -> Product:
    try:
        return update_product(db, collection, actor, product_id, payload)
    except ServiceError as exc:
        raise_service_error(exc)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_product(
    product_id: int,
    db: Session = Depends(get_db),
    collection: Collection = Depends(get_audit_logs_collection),
    actor: User = Depends(require_roles("admin")),
) -> Response:
    try:
        delete_product(db, collection, actor, product_id)
    except ServiceError as exc:
        raise_service_error(exc)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
