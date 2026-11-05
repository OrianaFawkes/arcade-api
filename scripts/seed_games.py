from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models import Game


INITIAL_GAMES = (
    {
        "slug": "proximity",
        "name": "Proximity",
    },
    {
        "slug": "powers-of-two",
        "name": "Powers of Two",
    },
)


def seed_games(db: Session) -> int:
    """Insert initial games that do not already exist.

    Returns the number of games inserted.
    """
    inserted_count = 0

    for game_data in INITIAL_GAMES:
        existing_game = db.scalar(
            select(Game).where(Game.slug == game_data["slug"])
        )

        if existing_game is not None:
            continue

        db.add(
            Game(
                slug=game_data["slug"],
                name=game_data["name"],
                is_active=True,
            )
        )
        inserted_count += 1

    db.commit()

    return inserted_count


def main() -> None:
    with SessionLocal() as db:
        inserted_count = seed_games(db)

    if inserted_count:
        print(f"Seeded {inserted_count} game(s).")
    else:
        print("No games needed seeding.")


if __name__ == "__main__":
    main()