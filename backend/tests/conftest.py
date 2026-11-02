"""Shared isolated fixtures for API integration tests."""

from copy import deepcopy
from datetime import datetime
from types import SimpleNamespace

import pytest
from bson.objectid import ObjectId
from fastapi.testclient import TestClient
from pymongo.errors import PyMongoError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.security import hash_password
from app.core.config import get_settings
from app.db import Base, get_audit_logs_collection, get_db, get_mongo_client
from app.main import app
from app.models import User


class MemoryCursor:
    def __init__(self, documents: list[dict]):
        self.documents = documents

    def sort(self, field: str, direction: int):
        self.documents.sort(
            key=lambda document: document.get(field, datetime.min),
            reverse=direction < 0,
        )
        return self

    def limit(self, count: int):
        self.documents = self.documents[:count]
        return self

    def __iter__(self):
        return iter(self.documents)


class MemoryAuditCollection:
    """Small Mongo collection test double for API behavior and failures."""

    def __init__(self):
        self.documents: list[dict] = []
        self.fail_writes = False
        self.fail_reads = False

    def insert_one(self, document: dict):
        if self.fail_writes:
            raise PyMongoError("test audit write failure")
        stored = deepcopy(document)
        stored.setdefault("_id", ObjectId())
        self.documents.append(stored)
        return SimpleNamespace(inserted_id=stored["_id"])

    def delete_one(self, query: dict):
        self.documents = [
            document for document in self.documents if document.get("_id") != query.get("_id")
        ]
        return SimpleNamespace(deleted_count=0)

    def find(self, query: dict | None = None):
        if self.fail_reads:
            raise PyMongoError("test audit read failure")
        return MemoryCursor(deepcopy(self.documents))

    def seed(self, *, timestamp: datetime, action: str = "CREATE", module: str = "Product"):
        self.documents.append(
            {
                "_id": ObjectId(),
                "user_id": 1,
                "user_email": "auditor@example.com",
                "action": action,
                "module": module,
                "details": {"source": "test"},
                "timestamp": timestamp,
            }
        )


@pytest.fixture
def api_client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("JWT_SECRET", "test-secret-for-vyanic-apis-at-least-32-characters")
    get_settings.cache_clear()

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    audit_collection = MemoryAuditCollection()

    def override_get_db():
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_audit_logs_collection] = lambda: audit_collection

    with session_factory() as session:
        session.add_all(
            [
                User(
                    name="Portal Admin",
                    email="admin@example.com",
                    hashed_password=hash_password("Admin-test-password-123"),
                    role="admin",
                ),
                User(
                    name="Portal Stockist",
                    email="stockist@example.com",
                    hashed_password=hash_password("Stockist-test-password-123"),
                    role="stockist",
                ),
                User(
                    name="Portal Viewer",
                    email="viewer@example.com",
                    hashed_password=hash_password("Viewer-test-password-123"),
                    role="viewer",
                ),
            ]
        )
        session.commit()

    client = TestClient(app)
    yield client, session_factory, audit_collection

    client.close()
    app.dependency_overrides.clear()
    engine.dispose()
    get_settings.cache_clear()


@pytest.fixture
def mongo_audit_client(api_client):
    """Use a temporary real Mongo collection without polluting audit_logs."""
    client, session_factory, _ = api_client
    mongo_client = get_mongo_client()
    collection_name = f"stage3a_test_audit_{ObjectId()}"
    collection = mongo_client[get_settings().mongodb_database][collection_name]
    collection.drop()
    app.dependency_overrides[get_audit_logs_collection] = lambda: collection
    yield client, session_factory, collection
    collection.drop()


def login_headers(client: TestClient, role: str = "admin") -> dict[str, str]:
    credentials = {
        "admin": ("admin@example.com", "Admin-test-password-123"),
        "stockist": ("stockist@example.com", "Stockist-test-password-123"),
        "viewer": ("viewer@example.com", "Viewer-test-password-123"),
    }[role]
    response = client.post(
        "/auth/login",
        json={"email": credentials[0], "password": credentials[1]},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
