
from fastapi import APIRouter, Depends, Request, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.limiter import limiter
from app.schemas.leaderboard import LeaderboardResponse
from app.schemas.scores import ProximityDifficulty
from app.services.leaderboard_service import get_leaderboard


router = APIRouter()


@router.get(
    "/{game_slug}/leaderboard",
    response_model=LeaderboardResponse,
)
@limiter.limit("60/minute")
def read_leaderboard(
    request: Request,
    game_slug: str,
    difficulty: ProximityDifficulty | None = Query(
        default=None),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    try:
        return get_leaderboard(
            db=db,
            game_slug=game_slug,
            difficulty=difficulty,
            limit=limit,
            offset=offset,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc
