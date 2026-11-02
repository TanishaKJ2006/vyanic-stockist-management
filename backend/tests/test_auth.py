"""Authentication API, password hashing, and protected route tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.security import hash_password, verify_password
from app.core.config import get_settings
from app.db import Base, get_db
from app.main import app
from app.models import User


@pytest.fixture
def auth_client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("JWT_SECRET", "test-only-secret-with-more-than-32-characters")
    get_settings.cache_clear()

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    test_session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )

    def override_get_db():
        with test_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client, test_session_factory
    client.close()
    app.dependency_overrides.clear()
    engine.dispose()
    get_settings.cache_clear()


def register_stockist(client: TestClient, email: str = "stockist@example.com"):
    return client.post(
        "/auth/register",
        json={
            "name": "  Taylor   Stockist ",
            "email": email,
            "password": "a-safe-password-123",
        },
    )


def test_registration_creates_stockist_and_hashes_password(auth_client) -> None:
    client, session_factory = auth_client
    response = register_stockist(client)

    assert response.status_code == 201
    assert response.json()["name"] == "Taylor Stockist"
    assert response.json()["role"] == "stockist"
    assert "hashed_password" not in response.json()

    with session_factory() as session:
        user = session.scalar(select(User).where(User.email == "stockist@example.com"))

    assert user is not None
    assert user.hashed_password != "a-safe-password-123"
    assert user.hashed_password.startswith("$argon2")
    assert verify_password("a-safe-password-123", user.hashed_password)


def test_public_registration_supports_pdf_viewer_role(auth_client) -> None:
    client, session_factory = auth_client
    response = client.post(
        "/auth/register",
        json={
            "name": "Read Only Viewer",
            "email": "viewer@example.com",
            "password": "a-safe-password-123",
            "role": "viewer",
        },
    )

    assert response.status_code == 201
    assert response.json()["role"] == "viewer"
    with session_factory() as session:
        user = session.scalar(select(User).where(User.email == "viewer@example.com"))
    assert user is not None
    assert verify_password("a-safe-password-123", user.hashed_password)


def test_public_registration_cannot_create_admin(auth_client) -> None:
    client, _ = auth_client
    response = client.post(
        "/auth/register",
        json={
            "name": "Attempted Admin",
            "email": "admin@example.com",
            "password": "a-safe-password-123",
            "role": "admin",
        },
    )

    assert response.status_code == 422


def test_login_issues_token_and_protects_current_user(auth_client) -> None:
    client, _ = auth_client
    register_response = register_stockist(client)
    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={"email": "STOCKIST@example.com", "password": "a-safe-password-123"},
    )

    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    assert login_response.json()["token_type"] == "bearer"
    assert login_response.json()["expires_in"] > 0

    current_user = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert current_user.status_code == 200
    assert current_user.json()["email"] == "stockist@example.com"
    assert current_user.json()["role"] == "stockist"


def test_login_rejects_invalid_credentials(auth_client) -> None:
    client, _ = auth_client
    register_stockist(client)

    response = client.post(
        "/auth/login",
        json={"email": "stockist@example.com", "password": "incorrect-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Email or password is incorrect."


def test_current_user_requires_valid_bearer_token(auth_client) -> None:
    client, _ = auth_client

    assert client.get("/auth/me").status_code == 401
    assert client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid.token.value"},
    ).status_code == 401


def test_registration_validates_email_password_and_duplicate_email(auth_client) -> None:
    client, _ = auth_client
    invalid = client.post(
        "/auth/register",
        json={"name": "Taylor", "email": "not-an-email", "password": "short"},
    )
    assert invalid.status_code == 422

    assert register_stockist(client).status_code == 201
    duplicate = register_stockist(client)
    assert duplicate.status_code == 409


def test_password_hashing_uses_salted_non_reversible_hash() -> None:
    password = "another-safe-password-123"

    first_hash = hash_password(password)
    second_hash = hash_password(password)

    assert first_hash != second_hash
    assert password not in first_hash
    assert verify_password(password, first_hash)
    assert not verify_password("wrong-password", first_hash)
