from typing import Annotated

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.limiter import limiter
from app.models import Game
from app.schemas.game import GameResponse


router = APIRouter()


@router.get(
    "",
    response_model=list[GameResponse],
)
@limiter.limit("120/minute")
def list_games(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
):
    statement = (
        select(Game)
        .where(Game.is_active.is_(True))
        .order_by(Game.name, Game.slug)
    )

    games = db.scalars(statement).all()

    return games
