"""Stockist and pincode management operations."""

import re
from datetime import datetime, timezone

from pymongo.collection import Collection
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Stockist, StockistPincode, User
from app.schemas.audit_logs import AuditAction, AuditModule
from app.schemas.stockists import PincodeCreate, StockistCreate
from app.services.audit_logs import commit_with_audit
from app.services.errors import (
    DatabaseReadError,
    DatabaseWriteError,
    DuplicatePincodeError,
    ResourceNotFoundError,
)


def _stockist_details(stockist: Stockist) -> dict[str, object]:
    return {
        "id": stockist.id,
        "name": stockist.name,
        "contact_email": stockist.contact_email,
        "contact_phone": stockist.contact_phone,
        "city": stockist.city,
        "created_at": stockist.created_at.isoformat(),
    }


def _pincode_details(pincode: StockistPincode) -> dict[str, object]:
    return {
        "id": pincode.id,
        "stockist_id": pincode.stockist_id,
        "pincode": pincode.pincode,
        "state": pincode.state,
        "created_at": pincode.created_at.isoformat(),
    }


def _is_pincode_unique_violation(error: IntegrityError) -> bool:
    message = str(error.orig).lower()
    return (
        "uq_stockist_pincodes_pincode" in message
        or "stockist_pincodes.pincode" in message
        or bool(re.search(r"\b1062\b", message))
    )


def list_stockists(db: Session) -> list[Stockist]:
    try:
        return list(db.scalars(select(Stockist).order_by(Stockist.name, Stockist.id)).all())
    except SQLAlchemyError as exc:
        raise DatabaseReadError from exc


def create_stockist(
    db: Session,
    collection: Collection,
    actor: User,
    data: StockistCreate,
) -> Stockist:
    stockist = Stockist(
        **data.model_dump(),
        created_at=datetime.now(timezone.utc),
    )
    db.add(stockist)
    try:
        db.flush()
    except SQLAlchemyError as exc:
        db.rollback()
        raise DatabaseWriteError from exc

    try:
        commit_with_audit(
            db,
            collection,
            actor,
            AuditAction.CREATE,
            AuditModule.STOCKIST,
            {"stockist": _stockist_details(stockist)},
        )
    except SQLAlchemyError as exc:
        raise DatabaseWriteError from exc
    return stockist


def assign_pincode(
    db: Session,
    collection: Collection,
    actor: User,
    stockist_id: int,
    data: PincodeCreate,
) -> StockistPincode:
    try:
        stockist = db.get(Stockist, stockist_id)
        if stockist is None:
            raise ResourceNotFoundError("Stockist not found.")
        existing = db.scalar(
            select(StockistPincode.id).where(StockistPincode.pincode == data.pincode)
        )
    except SQLAlchemyError as exc:
        raise DatabaseReadError from exc

    if existing is not None:
        raise DuplicatePincodeError

    pincode = StockistPincode(
        stockist_id=stockist.id,
        pincode=data.pincode,
        state=data.state,
        created_at=datetime.now(timezone.utc),
    )
    db.add(pincode)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        if _is_pincode_unique_violation(exc):
            raise DuplicatePincodeError from exc
        raise DatabaseWriteError from exc
    except SQLAlchemyError as exc:
        db.rollback()
        raise DatabaseWriteError from exc

    try:
        commit_with_audit(
            db,
            collection,
            actor,
            AuditAction.CREATE,
            AuditModule.PINCODE,
            {
                "pincode": _pincode_details(pincode),
                "stockist": {
                    "id": stockist.id,
                    "name": stockist.name,
                },
            },
        )
    except SQLAlchemyError as exc:
        raise DatabaseWriteError from exc
    return pincode


def list_stockist_pincodes(db: Session, stockist_id: int) -> list[StockistPincode]:
    try:
        stockist = db.get(Stockist, stockist_id)
        if stockist is None:
            raise ResourceNotFoundError("Stockist not found.")
        return list(
            db.scalars(
                select(StockistPincode)
                .where(StockistPincode.stockist_id == stockist_id)
                .order_by(StockistPincode.pincode)
            ).all()
        )
    except SQLAlchemyError as exc:
        raise DatabaseReadError from exc
