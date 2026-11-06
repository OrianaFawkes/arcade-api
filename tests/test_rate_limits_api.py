
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4

from app.api.v1.endpoints import players
from app.models import Game, Player, PlayerSession
from app.services.player_service import hash_session_token


def test_player_creation_rate_limit(client, monkeypatch):
    player = SimpleNamespace(
        id=uuid4(),
        display_name="PixelFox4821",
        created_at=datetime.now(UTC),
    )
    expires_at = datetime.now(UTC) + timedelta(days=365)

    monkeypatch.setattr(
        players,
        "create_anonymous_player",
        lambda db: (player, "test-session-token", expires_at),
    )

    responses = [
        client.post("/api/v1/players")
        for _ in range(6)
    ]

    assert [r.status_code for r in responses] == [
        201, 201, 201, 201, 201, 429,
    ]


def test_get_me_rate_limit(client, db_session):
    player = Player(display_name="RateLimitPlayer0001")
    db_session.add(player)
    db_session.flush()

    token = "rate-limit-me-token"

    session = PlayerSession(
        player_id=player.id,
        token_hash=hash_session_token(token),
        expires_at=datetime.now(UTC) + timedelta(days=30),
    )
    db_session.add(session)
    db_session.flush()

    headers = {"Authorization": f"Bearer {token}"}

    responses = [
        client.get("/api/v1/players/me", headers=headers)
        for _ in range(61)
    ]

    assert all(r.status_code == 200 for r in responses[:60])
    assert responses[60].status_code == 429


def test_score_submission_rate_limit(client, db_session):
    player = Player(display_name="RateLimitScore0001")
    db_session.add(player)
    db_session.flush()

    token = "rate-limit-score-token"

    session = PlayerSession(
        player_id=player.id,
        token_hash=hash_session_token(token),
        expires_at=datetime.now(UTC) + timedelta(days=30),
    )

    game = Game(
        slug="proximity",
        name="Proximity",
        is_active=True,
    )

    db_session.add_all([session, game])
    db_session.flush()

    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "difficulty": "beginner",
        "elapsed_seconds": 183,
    }

    responses = [
        client.post(
            "/api/v1/games/proximity/scores",
            headers=headers,
            json=payload,
        )
        for _ in range(21)
    ]

    assert all(r.status_code == 201 for r in responses[:20])
    assert responses[20].status_code == 429


def test_leaderboard_rate_limit(client, db_session):
    game = Game(
        slug="powers-of-two",
        name="Powers of Two",
        is_active=True,
    )
    db_session.add(game)
    db_session.flush()

    responses = [
        client.get("/api/v1/games/powers-of-two/leaderboard")
        for _ in range(61)
    ]

    assert all(r.status_code == 200 for r in responses[:60])
    assert responses[60].status_code == 429


def test_games_catalog_rate_limit(client):
    responses = [
        client.get("/api/v1/games")
        for _ in range(121)
    ]

    assert all(r.status_code == 200 for r in responses[:120])
    assert responses[120].status_code == 429
