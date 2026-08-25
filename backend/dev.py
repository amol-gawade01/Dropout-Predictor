"""Local development server with FastAPI hot reload.

Run from the repository root with: uv run python -m backend.dev
"""

import os

import uvicorn


def main() -> None:
    """Start the API and restart it whenever backend Python files change."""
    uvicorn.run(
        "backend.app.main:app",
        host=os.getenv("DEV_HOST", "127.0.0.1"),
        port=int(os.getenv("DEV_PORT", "8000")),
        reload=True,
        reload_dirs=["backend", "agents", "tutor", "ml"],
        reload_excludes=["*.pyc", "__pycache__", ".venv", "frontend"],
        log_level=os.getenv("LOG_LEVEL", "info"),
    )


if __name__ == "__main__":
    main()
