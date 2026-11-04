from fastapi import APIRouter

from app.api.v1.endpoints import players


router = APIRouter(
    prefix="/api/v1",
)

router.include_router(
    players.router,
    prefix="/players",
    tags=["Players"],
)