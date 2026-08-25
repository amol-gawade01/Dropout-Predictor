from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import (
    auth,
    dashboard,
    faculty,
    health,
    integration,
    parent_reports,
    risk,
    student_dashboard,
    tutor,
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
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()],
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

app.include_router(
    dashboard.router,
    prefix="/api/v1",
)
app.include_router(
    tutor.router,
    prefix="/api/v1",
)

app.include_router(
    integration.router,
    prefix="/api/v1",
)

app.include_router(
    faculty.router,
    prefix="/api/v1",
)

app.include_router(
    parent_reports.router,
    prefix="/api/v1",
)

app.include_router(
    student_dashboard.router,
    prefix="/api/v1",
)

app.include_router(
    auth.router,
    prefix="/api/v1",
)


@app.get("/")
def home():
    return {
        "message": "AI Student Success Platform API",
        "docs": "/docs",
    }
