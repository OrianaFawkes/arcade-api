from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import PlayerSession
from app.services.player_service import hash_session_token


def get_valid_session(
    db: Session,
    token: str,
) -> PlayerSession | None:
    token_hash = hash_session_token(token)

    now = datetime.now(timezone.utc)

    statement = (
        select(PlayerSession)
        .options(joinedload(PlayerSession.player))
        .where(
            PlayerSession.token_hash == token_hash,
            PlayerSession.revoked_at.is_(None),
            PlayerSession.expires_at > now,
        )
    )

    return db.scalar(statement)
