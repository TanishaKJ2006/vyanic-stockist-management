"""MongoDB audit-log persistence and read helpers."""

import logging
from datetime import datetime, timezone
from typing import Any

from bson import BSON
from bson.errors import BSONError
from bson.objectid import ObjectId
from pymongo import DESCENDING
from pymongo.collection import Collection
from pymongo.errors import PyMongoError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import User
from app.schemas.audit_logs import AuditAction, AuditModule
from app.services.errors import (
    AuditReadError,
    AuditWriteError,
    DatabaseReadError,
    DatabaseWriteError,
)

logger = logging.getLogger(__name__)


def _delete_audit_document(collection: Collection, event_id: ObjectId) -> bool:
    """Best-effort cleanup for an event whose SQL change did not commit."""
    try:
        collection.delete_one({"_id": event_id})
        return True
    except (PyMongoError, BSONError):
        logger.error("Could not compensate audit event %s.", event_id)
        return False


def commit_with_audit(
    db: Session,
    collection: Collection,
    actor: User,
    action: AuditAction,
    module: AuditModule,
    details: dict[str, Any],
) -> dict[str, Any]:
    """Commit one SQL change only after its corresponding audit write succeeds.

    MongoDB and MySQL do not share a transaction. The audit is inserted while the
    SQL transaction is still open. If the audit insert fails, SQL is rolled back;
    if the SQL commit fails, the audit document is removed as compensation.
    """
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise DatabaseWriteError from exc

    event_id = ObjectId()
    event = {
        "_id": event_id,
        "user_id": actor.id,
        "user_email": actor.email,
        "action": action.value,
        "module": module.value,
        "details": details,
        "timestamp": datetime.now(timezone.utc),
    }

    try:
        BSON.encode(event)
        collection.insert_one(event)
    except (PyMongoError, BSONError, TypeError, ValueError) as exc:
        db.rollback()
        _delete_audit_document(collection, event_id)
        raise AuditWriteError from exc

    try:
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        _delete_audit_document(collection, event_id)
        raise DatabaseWriteError from exc

    return event


def read_latest_audit_logs(collection: Collection, limit: int) -> list[dict[str, Any]]:
    """Read and normalize the newest audit events from MongoDB."""
    try:
        documents = list(
            collection.find({}).sort("timestamp", DESCENDING).limit(limit)
        )
    except (PyMongoError, BSONError) as exc:
        raise AuditReadError from exc

    return [
        {
            "id": str(document.get("_id", "")),
            "user_id": document["user_id"],
            "user_email": document["user_email"],
            "action": document["action"],
            "module": document["module"],
            "details": document["details"],
            "timestamp": document["timestamp"],
        }
        for document in documents
    ]


def get_audit_log_count(collection: Collection) -> int:
    """Return the number of audit events for read-only status tooling."""
    try:
        return collection.count_documents({})
    except PyMongoError as exc:
        raise AuditReadError from exc
