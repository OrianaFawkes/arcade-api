from datetime import datetime, timedelta, timezone

from app.models import Player, PlayerSession
from app.services.player_service import hash_session_token
from app.services.session_service import get_valid_session


def test_get_valid_session(db_session):
    player = Player(display_name="ValidPlayer0001")
    db_session.add(player)
    db_session.flush()

    token = "valid-session-token"

    session = PlayerSession(
        player_id=player.id,
        token_hash=hash_session_token(token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=30),
    )

    db_session.add(session)
    db_session.commit()

    result = get_valid_session(db_session, token)

    assert result is not None
    assert result.id == session.id
    assert result.player.id == player.id


def test_invalid_token_returns_none(db_session):
    result = get_valid_session(
        db_session,
        "nonexistent-token",
    )

    assert result is None


def test_expired_session_returns_none(db_session):
    player = Player(display_name="ExpiredPlayer0001")
    db_session.add(player)
    db_session.flush()

    token = "expired-session-token"

    session = PlayerSession(
        player_id=player.id,
        token_hash=hash_session_token(token),
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),
    )

    db_session.add(session)
    db_session.commit()

    result = get_valid_session(db_session, token)

    assert result is None


def test_revoked_session_returns_none(db_session):
    player = Player(display_name="RevokedPlayer0001")
    db_session.add(player)
    db_session.flush()

    token = "revoked-session-token"

    session = PlayerSession(
        player_id=player.id,
        token_hash=hash_session_token(token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        revoked_at=datetime.now(timezone.utc),
    )

    db_session.add(session)
    db_session.commit()

    result = get_valid_session(db_session, token)

    assert result is None