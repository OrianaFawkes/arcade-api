from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.models import Player, PlayerSession
from app.services.player_service import hash_session_token
from main import app


client = TestClient(app)


def test_get_me_with_valid_token(db_session):
    player = Player(display_name="AuthenticatedPlayer0001")
    db_session.add(player)
    db_session.flush()

    token = "valid-player-token"

    session = PlayerSession(
        player_id=player.id,
        token_hash=hash_session_token(token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=30),
    )

    db_session.add(session)
    db_session.commit()

    app.dependency_overrides[get_db] = lambda: db_session

    try:
        response = client.get(
            "/api/v1/players/me",
            headers={"Authorization": f"Bearer {token}"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    assert response.json()["id"] == str(player.id)
    assert response.json()["display_name"] == player.display_name


def test_get_me_without_token_returns_401(db_session):
    app.dependency_overrides[get_db] = lambda: db_session

    try:
        response = client.get("/api/v1/players/me")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required."


def test_get_me_with_invalid_token_returns_401(db_session):
    app.dependency_overrides[get_db] = lambda: db_session

    try:
        response = client.get(
            "/api/v1/players/me",
            headers={"Authorization": "Bearer invalid-token"},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired session."
