"""FastAPI entry point for Afterlife AI."""

from fastapi import FastAPI

from backend.api.routes import router as api_router

app = FastAPI(
    title="Afterlife AI",
    version="0.1.0",
)

app.include_router(api_router)


@app.get("/")
def root() -> dict[str, str]:
    """Return basic service metadata."""
    return {
        "service": "afterlife-ai",
        "status": "ready",
    }


@app.get("/health")
def health() -> dict[str, str]:
    """Return deterministic health status."""
    return {
        "status": "ok",
        "service": "afterlife-ai",
    }