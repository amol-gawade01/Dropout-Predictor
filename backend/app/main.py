from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import (
    health,
    risk,
)
from backend.app.core.config import (
    get_settings,
)


settings = get_settings()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:3000"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["Health"],
)


app.include_router(
    risk.router,
    prefix="/api/v1",
    tags=["Student Risk"],
)


@app.get("/")
def home():
    return {
        "message":
            "AI Student Success Platform API",
        "docs":
            "/docs",
    }