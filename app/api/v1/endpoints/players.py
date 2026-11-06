from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.limiter import limiter
from app.models.player_session import PlayerSession
from app.schemas.player import PlayerCreateResponse, PlayerResponse, SessionResponse
from app.services.player_service import create_anonymous_player

from typing import Annotated

from app.api.dependencies import get_current_session

router = APIRouter()


@router.post(
    "",
    response_model=PlayerCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("5/minute")
def create_player(
    request: Request,
    db: Session = Depends(get_db),
):
    player, token, expires_at = create_anonymous_player(db)

    return PlayerCreateResponse(
        player=PlayerResponse.model_validate(player),
        session=SessionResponse(
            token=token,
            expires_at=expires_at,
        ),
    )


@router.get(
    "/me",
    response_model=PlayerResponse,
)
@limiter.limit("60/minute")
def get_me(
    request: Request,
    current_session: Annotated[
        PlayerSession,
        Depends(get_current_session),
    ],
):
    return current_session.player
