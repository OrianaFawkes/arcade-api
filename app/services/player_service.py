import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Player, PlayerSession


SESSION_LIFETIME = timedelta(days=365)
MAX_NAME_ATTEMPTS = 5

DISPLAY_NAME_INDEX = "ix_players_display_name_lower"

ADJECTIVES = [
    "Pixel",
    "Cosmic",
    "Neon",
    "Lucky",
    "Turbo",
    "Mighty",
    "Silent",
    "Rapid",
    "Golden",
    "Clever",
]

NOUNS = [
    "Fox",
    "Panda",
    "Tiger",
    "Koala",
    "Falcon",
    "Otter",
    "Dragon",
    "Comet",
    "Robot",
    "Ninja",
]


def generate_display_name() -> str:
    adjective = secrets.choice(ADJECTIVES)
    noun = secrets.choice(NOUNS)
    number = secrets.randbelow(10_000)

    return f"{adjective}{noun}{number:04d}"


def hash_session_token(token: str) -> str:
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def create_anonymous_player(
    db: Session,
) -> tuple[Player, str, datetime]:
    for _ in range(MAX_NAME_ATTEMPTS):
        player = Player(
            display_name=generate_display_name(),
        )

        db.add(player)

        try:
            # Send the INSERT to PostgreSQL now, so we can
            # detect a display-name collision before creating
            # the session.
            db.flush()

        except IntegrityError as exc:
            db.rollback()

            constraint_name = getattr(
                getattr(exc.orig, "diag", None),
                "constraint_name",
                None,
            )

            # Only retry when the display-name index caused
            # the collision. Other integrity errors are real
            # failures and should not be hidden.
            if constraint_name == DISPLAY_NAME_INDEX:
                continue

            raise

        token = secrets.token_urlsafe(32)
        token_hash = hash_session_token(token)

        expires_at = (
            datetime.now(timezone.utc) + SESSION_LIFETIME
        )

        session = PlayerSession(
            player_id=player.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        db.add(session)

        try:
            # Player and session are committed together.
            db.commit()
            db.refresh(player)

        except Exception:
            db.rollback()
            raise

        return player, token, expires_at

    raise RuntimeError(
        "Could not generate a unique player display name."
    )