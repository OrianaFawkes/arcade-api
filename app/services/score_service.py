from datetime import UTC, datetime
from typing import Type

from pydantic import BaseModel, ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.policies import SCORE_RETENTION
from app.models import Game, Player, Score
from app.schemas.scores import (
    PowersOfTwoScoreSubmission,
    ProximityScoreSubmission,
)


SCORE_SCHEMAS: dict[str, Type[BaseModel]] = {
    "proximity": ProximityScoreSubmission,
    "powers-of-two": PowersOfTwoScoreSubmission,
}


def submit_score(
    db: Session,
    player: Player,
    game_slug: str,
    payload: dict,
) -> Score:
    game = db.scalar(
        select(Game).where(
            Game.slug == game_slug,
            Game.is_active.is_(True),
        )
    )

    if game is None:
        raise ValueError("Game not found or inactive.")

    schema = SCORE_SCHEMAS.get(game.slug)

    if schema is None:
        raise ValueError("Score submission is not supported for this game.")

    validated_data = schema.model_validate(payload)

    data = validated_data.model_dump(mode="json")

    if game.slug == "proximity":
        ranking_value = data["elapsed_seconds"]

    elif game.slug == "powers-of-two":
        ranking_value = data["score"]

    else:
        raise ValueError("Score submission is not supported for this game.")

    now = datetime.now(UTC)

    score = Score(
        player_id=player.id,
        game_id=game.id,
        data=data,
        ranking_value=ranking_value,
        created_at=now,
        expires_at=now + SCORE_RETENTION,
    )

    db.add(score)
    db.commit()
    db.refresh(score)

    return score
