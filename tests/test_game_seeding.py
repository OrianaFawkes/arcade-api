from sqlalchemy import select

from app.models import Game
from scripts.seed_games import seed_games


def test_seed_games_inserts_initial_games(db_session):
    inserted_count = seed_games(db_session)

    assert inserted_count == 2

    games = db_session.scalars(
        select(Game).order_by(Game.slug)
    ).all()

    assert [(game.slug, game.name, game.is_active) for game in games] == [
        ("powers-of-two", "Powers of Two", True),
        ("proximity", "Proximity", True),
    ]


def test_seed_games_is_idempotent(db_session):
    first_inserted_count = seed_games(db_session)

    assert first_inserted_count == 2

    second_inserted_count = seed_games(db_session)

    assert second_inserted_count == 0

    games = db_session.scalars(select(Game)).all()

    assert len(games) == 2


def test_seed_games_does_not_overwrite_existing_game(db_session):
    db_session.add(
        Game(
            slug="proximity",
            name="Custom Proximity Name",
            is_active=False,
        )
    )
    db_session.commit()

    inserted_count = seed_games(db_session)

    assert inserted_count == 1

    proximity = db_session.scalar(
        select(Game).where(Game.slug == "proximity")
    )

    assert proximity is not None
    assert proximity.name == "Custom Proximity Name"
    assert proximity.is_active is False