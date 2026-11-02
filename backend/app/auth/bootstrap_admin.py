"""Interactively create the first administrator from a local console."""

from getpass import getpass

from pydantic import EmailStr, TypeAdapter, ValidationError
from sqlalchemy import select

from app.auth.security import hash_password
from app.core.config import get_settings
from app.db import get_session_factory
from app.models import User


def main() -> None:
    settings = get_settings()
    if not settings.mysql_user:
        raise SystemExit("Configure MYSQL_USER and MYSQL_PASSWORD in backend/.env first.")

    name = input("Administrator name: ").strip()
    if not name:
        raise SystemExit("Administrator name cannot be blank.")

    try:
        email = TypeAdapter(EmailStr).validate_python(input("Administrator email: ").strip())
    except ValidationError as exc:
        raise SystemExit("Enter a valid administrator email.") from exc
    email = str(email).lower()

    password = getpass("Administrator password (12+ characters): ")
    confirmation = getpass("Confirm password: ")
    if len(password) < 12 or len(password) > 128:
        raise SystemExit("The administrator password must contain 12 to 128 characters.")
    if password != confirmation:
        raise SystemExit("The passwords do not match.")

    with get_session_factory()() as db:
        admin_exists = db.scalar(select(User.id).where(User.role == "admin"))
        if admin_exists is not None:
            raise SystemExit("An administrator already exists; bootstrap is one-time only.")
        if db.scalar(select(User.id).where(User.email == email)) is not None:
            raise SystemExit("That email is already registered. Choose another email.")

        db.add(
            User(
                name=" ".join(name.split()),
                email=email,
                hashed_password=hash_password(password),
                role="admin",
            )
        )
        db.commit()

    print(f"Administrator account created for {email}.")


if __name__ == "__main__":
    main()
