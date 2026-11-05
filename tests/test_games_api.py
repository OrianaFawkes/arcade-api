from fastapi.testclient import TestClient

from app.core.database import get_db
from app.models import Game
from main import app


client = TestClient(app)


def test_list_games_returns_active_games(db_session):
    active_game = Game(
        slug="2048",
        name="2048",
        is_active=True,
    )

    inactive_game = Game(
        slug="lights-out",
        name="Lights Out",
        is_active=False,
    )

    db_session.add_all([active_game, inactive_game])
    db_session.commit()

    app.dependency_overrides[get_db] = lambda: db_session

    try:
        response = client.get("/api/v1/games")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == str(active_game.id)
    assert data[0]["slug"] == "2048"
    assert data[0]["name"] == "2048"


def test_list_games_returns_empty_list(db_session):
    app.dependency_overrides[get_db] = lambda: db_session

    try:
        response = client.get("/api/v1/games")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    assert response.json() == []


def test_list_games_does_not_require_authentication(db_session):
    game = Game(
        slug="minesweeper",
        name="Minesweeper",
        is_active=True,
    )

    db_session.add(game)
    db_session.commit()

    app.dependency_overrides[get_db] = lambda: db_session

    try:
        response = client.get("/api/v1/games")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200