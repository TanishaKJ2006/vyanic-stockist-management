"""Product catalog business operations."""

import math
from datetime import datetime, timezone
from decimal import Decimal

from pymongo.collection import Collection
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Product, User
from app.schemas.audit_logs import AuditAction, AuditModule
from app.schemas.products import ProductWrite
from app.services.audit_logs import commit_with_audit
from app.services.errors import (
    DatabaseReadError,
    DatabaseWriteError,
    DuplicateSkuError,
    ResourceNotFoundError,
)


def _product_details(product: Product) -> dict[str, object]:
    return {
        "id": product.id,
        "name": product.name,
        "sku_code": product.sku_code,
        "category": product.category,
        "price": format(Decimal(product.price), ".2f"),
        "stock_quantity": product.stock_quantity,
        "created_at": product.created_at.isoformat(),
    }


def list_products(
    db: Session,
    *,
    page: int,
    limit: int,
    search: str | None,
    category: str | None,
) -> dict[str, object]:
    filters = []
    normalized_search = search.strip() if search else ""
    normalized_category = category.strip() if category else ""

    if normalized_search:
        pattern = f"%{normalized_search}%"
        filters.append(
            or_(
                Product.name.ilike(pattern),
                Product.sku_code.ilike(pattern),
                Product.category.ilike(pattern),
            )
        )
    if normalized_category:
        filters.append(func.lower(Product.category) == normalized_category.lower())

    try:
        total = db.scalar(
            select(func.count()).select_from(Product).where(*filters)
        ) or 0
        products = db.scalars(
            select(Product)
            .where(*filters)
            .order_by(Product.name.asc(), Product.id.asc())
            .offset((page - 1) * limit)
            .limit(limit)
        ).all()
    except SQLAlchemyError as exc:
        raise DatabaseReadError from exc

    return {
        "items": products,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": math.ceil(total / limit) if total else 0,
    }


def _ensure_sku_is_available(
    db: Session,
    sku_code: str,
    *,
    exclude_product_id: int | None = None,
) -> None:
    query = select(Product.id).where(Product.sku_code == sku_code)
    if exclude_product_id is not None:
        query = query.where(Product.id != exclude_product_id)
    try:
        if db.scalar(query) is not None:
            raise DuplicateSkuError
    except SQLAlchemyError as exc:
        raise DatabaseReadError from exc


def create_product(
    db: Session,
    collection: Collection,
    actor: User,
    data: ProductWrite,
) -> Product:
    _ensure_sku_is_available(db, data.sku_code)
    product = Product(
        **data.model_dump(),
        created_at=datetime.now(timezone.utc),
    )
    db.add(product)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateSkuError from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise DatabaseWriteError from exc

    try:
        commit_with_audit(
            db,
            collection,
            actor,
            AuditAction.CREATE,
            AuditModule.PRODUCT,
            {"product": _product_details(product)},
        )
    except IntegrityError as exc:
        raise DuplicateSkuError from exc
    except SQLAlchemyError as exc:
        raise DatabaseWriteError from exc
    return product


def update_product(
    db: Session,
    collection: Collection,
    actor: User,
    product_id: int,
    data: ProductWrite,
) -> Product:
    try:
        product = db.get(Product, product_id)
    except SQLAlchemyError as exc:
        raise DatabaseReadError from exc
    if product is None:
        raise ResourceNotFoundError("Product not found.")

    _ensure_sku_is_available(db, data.sku_code, exclude_product_id=product_id)
    before = _product_details(product)
    for field_name, value in data.model_dump().items():
        setattr(product, field_name, value)

    try:
        commit_with_audit(
            db,
            collection,
            actor,
            AuditAction.UPDATE,
            AuditModule.PRODUCT,
            {"before": before, "after": _product_details(product)},
        )
    except IntegrityError as exc:
        raise DuplicateSkuError from exc
    except SQLAlchemyError as exc:
        raise DatabaseWriteError from exc
    return product


def delete_product(
    db: Session,
    collection: Collection,
    actor: User,
    product_id: int,
) -> None:
    try:
        product = db.get(Product, product_id)
    except SQLAlchemyError as exc:
        raise DatabaseReadError from exc
    if product is None:
        raise ResourceNotFoundError("Product not found.")

    details = {"product": _product_details(product)}
    db.delete(product)
    try:
        commit_with_audit(
            db,
            collection,
            actor,
            AuditAction.DELETE,
            AuditModule.PRODUCT,
            details,
        )
    except IntegrityError as exc:
        raise DatabaseWriteError from exc
    except SQLAlchemyError as exc:
        raise DatabaseWriteError from exc
