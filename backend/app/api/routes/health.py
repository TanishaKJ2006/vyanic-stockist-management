"""Health check route for local development and process monitoring."""

from fastapi import APIRouter

from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Return the application's process health without querying databases."""
    return HealthResponse(status="ok")
