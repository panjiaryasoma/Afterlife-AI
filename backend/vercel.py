"""Vercel-specific FastAPI entry point.

Vercel executes the application from the repository root without installing
the local ``src/afterlife_ai`` package into the function environment. Add the
repository ``src`` directory to ``sys.path`` before importing the production
application.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from backend.main import app  # noqa: E402

__all__ = ["app"]
