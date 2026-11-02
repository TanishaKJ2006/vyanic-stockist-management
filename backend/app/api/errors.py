"""Translate service-layer errors into safe HTTP responses."""

from fastapi import HTTPException, status

from app.services.errors import (
    AuditReadError,
    AuditWriteError,
    DatabaseReadError,
    DatabaseWriteError,
    DuplicatePincodeError,
    DuplicateSkuError,
    ResourceNotFoundError,
)

PINCODE_DUPLICATE_MESSAGE = "This pincode is already assigned to another stockist."


def raise_service_error(error: Exception) -> None:
    if isinstance(error, DuplicateSkuError):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A product with this SKU code already exists.",
        ) from error
    if isinstance(error, DuplicatePincodeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=PINCODE_DUPLICATE_MESSAGE,
        ) from error
    if isinstance(error, ResourceNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error) or "The requested record was not found.",
        ) from error
    if isinstance(error, AuditWriteError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The change was not saved because its audit log could not be written.",
        ) from error
    if isinstance(error, AuditReadError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The audit log service is unavailable.",
        ) from error
    if isinstance(error, (DatabaseReadError, DatabaseWriteError)):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The database operation could not be completed.",
        ) from error
    raise error
