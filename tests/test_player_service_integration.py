from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.models import Player, PlayerSession
from app.services import player_service
from app.services.player_service import (
    create_anonymous_player,
    hash_session_token,
)


def test_player_and_session_are_persisted(db_session):
    before = datetime.now(timezone.utc)

    player, token, expires_at = create_anonymous_player(db_session)

    stored_player = db_session.get(Player, player.id)

    stored_session = db_session.scalar(
        select(PlayerSession).where(
            PlayerSession.player_id == player.id
        )
    )

    assert stored_player is not None
    assert stored_player.display_name == player.display_name

    assert stored_session is not None
    assert stored_session.token_hash == hash_session_token(token)
    assert stored_session.token_hash != token

    assert stored_session.expires_at == expires_at

    lifetime = expires_at - before

    assert timedelta(days=365) <= lifetime
    assert lifetime < timedelta(days=365, seconds=5)


def test_display_name_collision_is_retried(
    db_session,
    monkeypatch,
):
    existing_player = Player(
        display_name="PixelFox4821",
    )

    db_session.add(existing_player)
    db_session.commit()

    generated_names = iter([
        "pixelfox4821",
        "CosmicPanda0001",
    ])

    monkeypatch.setattr(
        player_service,
        "generate_display_name",
        lambda: next(generated_names),
    )

    player, token, expires_at = create_anonymous_player(
        db_session,
    )

    assert player.display_name == "CosmicPanda0001"


def test_failed_session_creation_rolls_back_player(
    db_session,
    monkeypatch,
):
    existing_player = Player(
        display_name="ExistingPlayer0001",
    )

    db_session.add(existing_player)
    db_session.flush()

    existing_token = "already-used-token"

    existing_session = PlayerSession(
        player_id=existing_player.id,
        token_hash=hash_session_token(existing_token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=365),
    )

    db_session.add(existing_session)
    db_session.commit()

    # Force the service to generate a token whose hash
    # already exists in the database.
    monkeypatch.setattr(
        player_service.secrets,
        "token_urlsafe",
        lambda _: existing_token,
    )

    with pytest.raises(IntegrityError):
        create_anonymous_player(db_session)

    player_count = db_session.scalar(
        select(func.count()).select_from(Player)
    )

    # The original player remains, but the failed creation
    # must not leave another player behind.
    assert player_count == 1