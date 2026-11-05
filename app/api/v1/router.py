from fastapi import APIRouter

from app.api.v1.endpoints import games, players, scores


router = APIRouter(prefix="/api/v1")

router.include_router(
    players.router,
    prefix="/players",
    tags=["Players"],
)

router.include_router(
    games.router,
    prefix="/games",
    tags=["Games"],
)

router.include_router(
    scores.router,
    prefix="/games",
    tags=["Scores"],
)
