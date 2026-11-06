from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.router import router as v1_router
from app.core.config import settings
from app.core.database import get_db

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.limiter import limiter

app = FastAPI(
    title="Arcade API",
    description="Backend API for Arcade.",
    version="0.1.0",
)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(v1_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/health/database")
def database_health_check(
    db: Session = Depends(get_db),
):
    db.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "database": "connected",
    }
