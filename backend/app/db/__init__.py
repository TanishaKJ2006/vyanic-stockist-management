"""MySQL sessions and MongoDB audit-log access."""

from functools import lru_cache
from typing import Generator

from pymongo import DESCENDING, MongoClient
from pymongo.collection import Collection
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    """Base for the SQLAlchemy models and Alembic metadata."""


@lru_cache
def get_engine() -> Engine:
    """Create the lazy MySQL engine from environment-based settings."""
    settings = get_settings()
    if not settings.mysql_user:
        raise RuntimeError("MYSQL_USER is not configured")

    return create_engine(
        settings.sqlalchemy_url,
        pool_pre_ping=True,
        pool_recycle=1800,
    )


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    """Return the cached session factory for the configured MySQL engine."""
    return sessionmaker(bind=get_engine(), autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    """Yield one SQLAlchemy session per request."""
    try:
        session = get_session_factory()()
    except RuntimeError as exc:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=503,
            detail="MySQL is not configured. Set MYSQL_USER and MYSQL_PASSWORD.",
        ) from exc

    try:
        yield session
    finally:
        session.close()


@lru_cache
def get_mongo_client() -> MongoClient:
    """Return the lazy client configured by MONGODB_URI."""
    settings = get_settings()
    return MongoClient(
        settings.mongodb_uri.get_secret_value(),
        serverSelectionTimeoutMS=2000,
        connectTimeoutMS=2000,
        tz_aware=True,
    )


def get_audit_logs_collection() -> Collection:
    """Return the assignment's existing audit_logs collection."""
    settings = get_settings()
    return get_mongo_client()[settings.mongodb_database]["audit_logs"]


def ensure_audit_log_timestamp_index() -> str:
    """Ensure audit logs sort efficiently by timestamp, newest first."""
    collection = get_audit_logs_collection()
    return collection.create_index(
        [("timestamp", DESCENDING)],
        name="ix_audit_logs_timestamp_desc",
    )
