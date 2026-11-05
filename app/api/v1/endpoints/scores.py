from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_session
from app.core.database import get_db
from app.models import PlayerSession
from app.schemas.score import ScoreResponse
from app.services.score_service import submit_score


router = APIRouter()


@router.post(
    "/{game_slug}/scores",
    response_model=ScoreResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_score(
    game_slug: str,
    payload: dict,
    current_session: Annotated[
        PlayerSession,
        Depends(get_current_session),
    ],
    db: Annotated[Session, Depends(get_db)],
):
    try:
        return submit_score(
            db=db,
            player=current_session.player,
            game_slug=game_slug,
            payload=payload,
        )

    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=exc.errors(
                include_url=False,
                include_context=False,
                include_input=False,
            ),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc