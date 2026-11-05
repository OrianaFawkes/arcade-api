from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.models import Game, Player, PlayerSession, Score
from app.services.player_service import hash_session_token
from main import app


client = TestClient(app)


def create_authenticated_player(db_session):
    player = Player(display_name="ScoreTestPlayer0001")
    db_session.add(player)
    db_session.flush()

    token = "score-test-token"

    session = PlayerSession(
        player_id=player.id,
        token_hash=hash_session_token(token),
        expires_at=datetime.now(UTC) + timedelta(days=30),
    )

    db_session.add(session)
    db_session.commit()

    return player, token


def create_game(db_session, slug):
    game = Game(
        slug=slug,
        name=slug.replace("-", " ").title(),
        is_active=True,
    )

    db_session.add(game)
    db_session.commit()

    return game


def test_submit_proximity_score(db_session):
    player, token = create_authenticated_player(db_session)
    game = create_game(db_session, "proximity")

    app.dependency_overrides[get_db] = lambda: db_session

    try:
        response = client.post(
            "/api/v1/games/proximity/scores",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "difficulty": "beginner",
                "elapsed_seconds": 183,
            },
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 201

    data = response.json()

    assert data["game_id"] == str(game.id)
    assert data["data"] == {
        "difficulty": "beginner",
        "elapsed_seconds": 183,
    }
    assert data["ranking_value"] == 183

    score = db_session.query(Score).one()

    assert score.player_id == player.id


def test_submit_powers_of_two_score(db_session):
    _, token = create_authenticated_player(db_session)
    game = create_game(db_session, "powers-of-two")

    app.dependency_overrides[get_db] = lambda: db_session

    try:
        response = client.post(
            "/api/v1/games/powers-of-two/scores",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "score": 123456,
                "tile": 2048,
            },
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 201

    data = response.json()

    assert data["game_id"] == str(game.id)
    assert data["data"] == {
        "score": 123456,
        "tile": 2048,
    }
    assert data["ranking_value"] == 123456


def test_submit_score_requires_authentication(db_session):
    create_game(db_session, "proximity")

    app.dependency_overrides[get_db] = lambda: db_session

    try:
        response = client.post(
            "/api/v1/games/proximity/scores",
            json={
                "difficulty": "beginner",
                "elapsed_seconds": 183,
            },
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 401


def test_submit_score_rejects_unknown_game(db_session):
    _, token = create_authenticated_player(db_session)

    app.dependency_overrides[get_db] = lambda: db_session

    try:
        response = client.post(
            "/api/v1/games/unknown-game/scores",
            headers={"Authorization": f"Bearer {token}"},
            json={"score": 100},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 404


def test_submit_score_rejects_inactive_game(db_session):
    _, token = create_authenticated_player(db_session)

    db_session.add(
        Game(
            slug="proximity",
            name="Proximity",
            is_active=False,
        )
    )
    db_session.commit()

    app.dependency_overrides[get_db] = lambda: db_session

    try:
        response = client.post(
            "/api/v1/games/proximity/scores",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "difficulty": "beginner",
                "elapsed_seconds": 183,
            },
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 404


def test_submit_proximity_score_rejects_invalid_payload(db_session):
    _, token = create_authenticated_player(db_session)
    create_game(db_session, "proximity")

    app.dependency_overrides[get_db] = lambda: db_session

    try:
        response = client.post(
            "/api/v1/games/proximity/scores",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "difficulty": "impossible",
                "elapsed_seconds": -1,
            },
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 422


def test_submit_powers_of_two_rejects_invalid_tile(db_session):
    _, token = create_authenticated_player(db_session)
    create_game(db_session, "powers-of-two")

    app.dependency_overrides[get_db] = lambda: db_session

    try:
        response = client.post(
            "/api/v1/games/powers-of-two/scores",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "score": 100,
                "tile": 1000,
            },
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 422


def test_submit_score_rejects_extra_fields(db_session):
    _, token = create_authenticated_player(db_session)
    create_game(db_session, "proximity")

    app.dependency_overrides[get_db] = lambda: db_session

    try:
        response = client.post(
            "/api/v1/games/proximity/scores",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "difficulty": "beginner",
                "elapsed_seconds": 183,
                "ranking_value": 999999,
            },
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 422


def test_submit_score_sets_three_year_expiration(db_session):
    _, token = create_authenticated_player(db_session)
    create_game(db_session, "proximity")

    app.dependency_overrides[get_db] = lambda: db_session

    try:
        response = client.post(
            "/api/v1/games/proximity/scores",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "difficulty": "beginner",
                "elapsed_seconds": 183,
            },
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 201

    score = db_session.query(Score).one()

    expected_expiry = score.created_at + timedelta(days=365 * 3)

    assert score.expires_at == expected_expiry
