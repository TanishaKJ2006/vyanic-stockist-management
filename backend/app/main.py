"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from pymongo.errors import PyMongoError

from app.api.routes.auth import router as auth_router
from app.api.routes.audit_logs import router as audit_logs_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.health import router as health_router
from app.api.routes.products import router as products_router
from app.api.routes.stockists import router as stockists_router
from app.core.config import get_settings
from app.db import ensure_audit_log_timestamp_index

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Prepare the MongoDB audit-log index when the service is available."""
    if get_settings().app_env.lower() != "test":
        try:
            index_name = await run_in_threadpool(ensure_audit_log_timestamp_index)
            logger.info("MongoDB audit log index ready: %s", index_name)
        except PyMongoError as exc:
            logger.warning(
                "MongoDB is unavailable; audit log index setup was skipped (%s).",
                type(exc).__name__,
            )
    yield

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Vyanic Technologies stockist management portal API.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(products_router)
app.include_router(stockists_router)
app.include_router(audit_logs_router)
