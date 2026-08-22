from fastapi import APIRouter
from sqlalchemy import text

from backend.app.db.session import engine


router = APIRouter()


@router.get("/health")
def health():
    with engine.connect() as connection:
        connection.execute(
            text("SELECT 1")
        )

    return {
        "status": "healthy",
        "database": "connected",
    }