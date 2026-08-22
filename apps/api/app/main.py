"""FastAPI application entrypoint.

Provides health checks and a minimal API surface so the frontend
can verify connectivity. Agent runtime is intentionally not wired yet.
"""

from datetime import UTC, datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Agentic IDE API — foundation infrastructure only.",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
async def health() -> dict[str, str | bool]:
    """Liveness probe — process is up."""
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/health/ready", tags=["health"])
async def readiness() -> dict[str, str | bool]:
    """Readiness probe — ready to accept traffic.

    Future: check DB, sandbox, etc. For now always ready.
    """
    return {
        "status": "ready",
        "service": settings.app_name,
        "checks": {"api": True},
    }


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    return {
        "message": "Agentic IDE API",
        "docs": "/docs",
        "health": "/health",
    }
