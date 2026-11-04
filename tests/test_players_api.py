from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.v1.endpoints import players
from app.core.database import get_db
from main import app


client = TestClient(app)


def test_create_player(monkeypatch):
    player_id = uuid4()
    created_at = datetime.now(timezone.utc)
    expires_at = created_at + timedelta(days=365)

    fake_player = SimpleNamespace(
        id=player_id,
        display_name="PixelFox4821",
        created_at=created_at,
    )

    def fake_create_anonymous_player(db):
        return fake_player, "test-session-token", expires_at

    monkeypatch.setattr(
        players,
        "create_anonymous_player",
        fake_create_anonymous_player,
    )

    app.dependency_overrides[get_db] = lambda: object()

    try:
        response = client.post("/api/v1/players")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 201

    data = response.json()

    assert data["player"]["id"] == str(player_id)
    assert data["player"]["display_name"] == "PixelFox4821"
    assert data["session"]["token"] == "test-session-token"
    assert data["session"]["expires_at"] is not None