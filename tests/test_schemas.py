from datetime import datetime, timezone
from uuid import uuid4

from app.schemas.player import (
    PlayerCreateResponse,
    PlayerResponse,
    SessionResponse,
)


def test_player_response_from_attributes():
    player_id = uuid4()
    now = datetime.now(timezone.utc)

    # Simulates a SQLAlchemy model instance.
    class FakePlayer:
        id = player_id
        display_name = "PixelFox123"
        created_at = now

    response = PlayerResponse.model_validate(FakePlayer())

    assert response.id == player_id
    assert response.display_name == "PixelFox123"
    assert response.created_at == now


def test_session_response():
    expires_at = datetime.now(timezone.utc)

    response = SessionResponse(
        token="test-token",
        expires_at=expires_at,
    )

    assert response.token == "test-token"
    assert response.expires_at == expires_at


def test_player_create_response():
    player_id = uuid4()
    created_at = datetime.now(timezone.utc)
    expires_at = datetime.now(timezone.utc)

    response = PlayerCreateResponse(
        player=PlayerResponse(
            id=player_id,
            display_name="PixelFox123",
            created_at=created_at,
        ),
        session=SessionResponse(
            token="test-token",
            expires_at=expires_at,
        ),
    )

    assert response.player.id == player_id
    assert response.player.display_name == "PixelFox123"
    assert response.session.token == "test-token"


def test_player_create_response_serialization():
    response = PlayerCreateResponse(
        player=PlayerResponse(
            id=uuid4(),
            display_name="PixelFox123",
            created_at=datetime.now(timezone.utc),
        ),
        session=SessionResponse(
            token="test-token",
            expires_at=datetime.now(timezone.utc),
        ),
    )

    data = response.model_dump(mode="json")

    assert isinstance(data["player"]["id"], str)
    assert data["player"]["display_name"] == "PixelFox123"
    assert data["session"]["token"] == "test-token"
