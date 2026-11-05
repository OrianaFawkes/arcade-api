
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest

from app.models import Game, Player, Score


def create_game(
    db_session,
    slug: str,
    *,
    is_active: bool = True,
) -> Game:
    game = Game(
        slug=slug,
        name=slug.replace("-", " ").title(),
        is_active=is_active,
    )
    db_session.add(game)
    db_session.flush()
    return game


def create_player(db_session, display_name: str) -> Player:
    player = Player(display_name=display_name)
    db_session.add(player)
    db_session.flush()
    return player


def create_score(
    db_session,
    *,
    player: Player,
    game: Game,
    data: dict,
    ranking_value: int,
    created_at: datetime | None = None,
    expires_at: datetime | None = None,
    archived_at: datetime | None = None,
    score_id: UUID | None = None,
) -> Score:
    now = datetime.now(UTC)

    score = Score(
        id=score_id or uuid4(),
        player_id=player.id,
        game_id=game.id,
        data=data,
        ranking_value=ranking_value,
        created_at=created_at or now,
        expires_at=expires_at or now + timedelta(days=30),
        archived_at=archived_at,
    )
    db_session.add(score)
    db_session.flush()
    return score


def test_proximity_leaderboard_selects_best_attempt_per_player(
    client,
    db_session,
):
    game = create_game(db_session, "proximity")

    player_a = create_player(db_session, "PlayerA")
    player_b = create_player(db_session, "PlayerB")
    player_c = create_player(db_session, "PlayerC")

    now = datetime.now(UTC)

    # Player A has multiple beginner attempts.
    create_score(
        db_session,
        player=player_a,
        game=game,
        data={"difficulty": "beginner", "elapsed_seconds": 100},
        ranking_value=100,
        created_at=now - timedelta(minutes=3),
    )
    create_score(
        db_session,
        player=player_a,
        game=game,
        data={"difficulty": "beginner", "elapsed_seconds": 80},
        ranking_value=80,
        created_at=now - timedelta(minutes=2),
    )

    # A different difficulty must not affect the beginner board.
    create_score(
        db_session,
        player=player_a,
        game=game,
        data={"difficulty": "intermediate", "elapsed_seconds": 10},
        ranking_value=10,
    )

    create_score(
        db_session,
        player=player_b,
        game=game,
        data={"difficulty": "beginner", "elapsed_seconds": 90},
        ranking_value=90,
    )

    # Player C's expired best attempt must be ignored.
    create_score(
        db_session,
        player=player_c,
        game=game,
        data={"difficulty": "beginner", "elapsed_seconds": 1},
        ranking_value=1,
        expires_at=now - timedelta(days=1),
    )
    create_score(
        db_session,
        player=player_c,
        game=game,
        data={"difficulty": "beginner", "elapsed_seconds": 110},
        ranking_value=110,
    )

    response = client.get(
        "/api/v1/games/proximity/leaderboard",
        params={"difficulty": "beginner"},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["game_slug"] == "proximity"
    assert body["total_entries"] == 3
    assert len(body["entries"]) == 3

    entries = body["entries"]

    assert [entry["display_name"] for entry in entries] == [
        "PlayerA",
        "PlayerB",
        "PlayerC",
    ]
    assert [entry["rank"] for entry in entries] == [1, 2, 3]
    assert [
        entry["data"]["elapsed_seconds"]
        for entry in entries
    ] == [80, 90, 110]


def test_proximity_leaderboard_excludes_archived_scores(
    client,
    db_session,
):
    game = create_game(db_session, "proximity")
    player = create_player(db_session, "PlayerA")

    now = datetime.now(UTC)

    create_score(
        db_session,
        player=player,
        game=game,
        data={"difficulty": "beginner", "elapsed_seconds": 5},
        ranking_value=5,
        archived_at=now,
    )

    create_score(
        db_session,
        player=player,
        game=game,
        data={"difficulty": "beginner", "elapsed_seconds": 60},
        ranking_value=60,
    )

    response = client.get(
        "/api/v1/games/proximity/leaderboard",
        params={"difficulty": "beginner"},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total_entries"] == 1
    assert len(body["entries"]) == 1
    assert body["entries"][0]["data"]["elapsed_seconds"] == 60


def test_powers_of_two_leaderboard_applies_tiebreakers(
    client,
    db_session,
):
    game = create_game(db_session, "powers-of-two")

    player_a = create_player(db_session, "PlayerA")
    player_b = create_player(db_session, "PlayerB")
    player_c = create_player(db_session, "PlayerC")
    player_d = create_player(db_session, "PlayerD")

    now = datetime.now(UTC)

    # Same score, but B has the higher tile.
    create_score(
        db_session,
        player=player_a,
        game=game,
        data={"score": 200, "tile": 512},
        ranking_value=200,
    )
    create_score(
        db_session,
        player=player_b,
        game=game,
        data={"score": 200, "tile": 1024},
        ranking_value=200,
        created_at=now - timedelta(minutes=2),
    )

    # Same score and tile as B, but submitted later.
    create_score(
        db_session,
        player=player_c,
        game=game,
        data={"score": 200, "tile": 1024},
        ranking_value=200,
        created_at=now - timedelta(minutes=1),
    )

    # Lower score cannot outrank the others, even with a higher tile.
    create_score(
        db_session,
        player=player_d,
        game=game,
        data={"score": 199, "tile": 2048},
        ranking_value=199,
    )

    response = client.get(
        "/api/v1/games/powers-of-two/leaderboard"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total_entries"] == 4
    assert [
        entry["display_name"]
        for entry in body["entries"]
    ] == [
        "PlayerB",
        "PlayerC",
        "PlayerA",
        "PlayerD",
    ]
    assert [
        entry["rank"]
        for entry in body["entries"]
    ] == [1, 2, 3, 4]


def test_leaderboard_pagination_preserves_global_ranks(
    client,
    db_session,
):
    game = create_game(db_session, "powers-of-two")

    for index, score_value in enumerate([300, 200, 100], start=1):
        player = create_player(db_session, f"Player{index}")
        create_score(
            db_session,
            player=player,
            game=game,
            data={"score": score_value, "tile": 128},
            ranking_value=score_value,
        )

    response = client.get(
        "/api/v1/games/powers-of-two/leaderboard",
        params={"limit": 1, "offset": 1},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total_entries"] == 3
    assert body["limit"] == 1
    assert body["offset"] == 1
    assert len(body["entries"]) == 1

    assert body["entries"][0]["display_name"] == "Player2"
    assert body["entries"][0]["rank"] == 2


def test_leaderboard_returns_empty_entries_when_no_scores_exist(
    client,
    db_session,
):
    create_game(db_session, "powers-of-two")

    response = client.get(
        "/api/v1/games/powers-of-two/leaderboard"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total_entries"] == 0
    assert body["entries"] == []


@pytest.mark.parametrize(
    "game_slug",
    ["unknown-game", "inactive-game"],
)
def test_leaderboard_returns_404_for_unavailable_games(
    client,
    db_session,
    game_slug,
):
    if game_slug == "inactive-game":
        create_game(
            db_session,
            game_slug,
            is_active=False,
        )

    response = client.get(
        f"/api/v1/games/{game_slug}/leaderboard"
    )

    assert response.status_code == 404


def test_proximity_leaderboard_requires_difficulty(
    client,
    db_session,
):
    create_game(db_session, "proximity")

    response = client.get(
        "/api/v1/games/proximity/leaderboard"
    )

    assert response.status_code == 422


def test_powers_of_two_rejects_difficulty(
    client,
    db_session,
):
    create_game(db_session, "powers-of-two")

    response = client.get(
        "/api/v1/games/powers-of-two/leaderboard",
        params={"difficulty": "beginner"},
    )

    assert response.status_code == 422


def test_leaderboard_validates_pagination(
    client,
    db_session,
):
    create_game(db_session, "powers-of-two")

    invalid_requests = [
        {"limit": 0},
        {"limit": 101},
        {"offset": -1},
    ]

    for params in invalid_requests:
        response = client.get(
            "/api/v1/games/powers-of-two/leaderboard",
            params=params,
        )

        assert response.status_code == 422


def test_leaderboard_is_public(
    client,
    db_session,
):
    game = create_game(db_session, "powers-of-two")
    player = create_player(db_session, "PublicPlayer")

    create_score(
        db_session,
        player=player,
        game=game,
        data={"score": 100, "tile": 128},
        ranking_value=100,
    )

    response = client.get(
        "/api/v1/games/powers-of-two/leaderboard"
    )

    assert response.status_code == 200
    assert response.json()["total_entries"] == 1


def test_powers_of_two_uses_score_id_as_final_tiebreaker(
    client,
    db_session,
):
    game = create_game(db_session, "powers-of-two")

    player_a = create_player(db_session, "PlayerA")
    player_b = create_player(db_session, "PlayerB")

    now = datetime.now(UTC)
    shared_time = now - timedelta(minutes=1)

    # Both scores have identical ranking values and timestamps.
    # The lower UUID should rank first.
    create_score(
        db_session,
        player=player_a,
        game=game,
        data={"score": 200, "tile": 1024},
        ranking_value=200,
        created_at=shared_time,
        score_id=UUID(int=2),
    )

    create_score(
        db_session,
        player=player_b,
        game=game,
        data={"score": 200, "tile": 1024},
        ranking_value=200,
        created_at=shared_time,
        score_id=UUID(int=1),
    )

    response = client.get(
        "/api/v1/games/powers-of-two/leaderboard"
    )

    assert response.status_code == 200

    entries = response.json()["entries"]

    assert [entry["display_name"] for entry in entries] == [
        "PlayerB",
        "PlayerA",
    ]
    assert [entry["rank"] for entry in entries] == [1, 2]
