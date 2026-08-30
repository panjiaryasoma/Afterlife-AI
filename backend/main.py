"""FastAPI entry point for Afterlife AI."""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.api.impact_routes import router as impact_router
from backend.api.routes import router as api_router

ROOT_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT_DIR / "frontend"

app = FastAPI(
    title="Afterlife AI",
    version="0.1.0",
)

app.include_router(api_router)
app.include_router(impact_router)

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR / "static"),
    name="static",
)

templates = Jinja2Templates(
    directory=FRONTEND_DIR / "templates"
)


@app.get("/", response_class=HTMLResponse)
def root(request: Request) -> HTMLResponse:
    """Render the single-page inventory analysis interface."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@app.get("/health")
def health() -> dict[str, str]:
    """Return deterministic health status."""
    return {
        "status": "ok",
        "service": "afterlife-ai",
    }
