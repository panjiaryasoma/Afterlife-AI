from backend.main import app as canonical_app
from backend.vercel import app as vercel_app


def test_vercel_entrypoint_reuses_canonical_fastapi_app() -> None:
    assert vercel_app is canonical_app
