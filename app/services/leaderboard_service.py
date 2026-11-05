
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Game, Player, Score
from app.schemas.leaderboard import (
    LeaderboardEntry,
    LeaderboardResponse,
)
from app.schemas.scores import ProximityDifficulty


def get_leaderboard(
    db: Session,
    game_slug: str,
    limit: int = 10,
    offset: int = 0,
    difficulty: ProximityDifficulty | None = None,
) -> LeaderboardResponse:
    game = db.scalar(
        select(Game).where(
            Game.slug == game_slug,
            Game.is_active.is_(True),
        )
    )

    if game is None:
        raise LookupError("Game not found or inactive.")

    now = datetime.now(UTC)

    # Configure game-specific eligibility and ranking rules.
    if game_slug == "proximity":
        if difficulty is None:
            raise ValueError("Difficulty is required for Proximity.")

        filters = (
            Score.data["difficulty"].as_string() == difficulty.value,
        )

        attempt_order = (
            Score.ranking_value.asc(),
            Score.created_at.asc(),
            Score.id.asc(),
        )

        leaderboard_order = (
            "proximity",
        )

    elif game_slug == "powers-of-two":
        if difficulty is not None:
            raise ValueError(
                "Difficulty is not supported for Powers of Two."
            )

        filters = ()

        attempt_order = (
            Score.ranking_value.desc(),
            Score.data["tile"].as_integer().desc(),
            Score.created_at.asc(),
            Score.id.asc(),
        )

        leaderboard_order = (
            "powers-of-two",
        )

    else:
        raise ValueError("Leaderboard is not supported for this game.")

    # First, rank each player's eligible attempts.
    ranked_attempts = (
        select(
            Score.id.label("score_id"),
            Score.player_id.label("player_id"),
            Player.display_name.label("display_name"),
            Score.data.label("data"),
            Score.ranking_value.label("ranking_value"),
            Score.created_at.label("created_at"),
            func.row_number()
            .over(
                partition_by=Score.player_id,
                order_by=attempt_order,
            )
            .label("attempt_number"),
        )
        .join(Player, Player.id == Score.player_id)
        .where(
            Score.game_id == game.id,
            Score.archived_at.is_(None),
            Score.expires_at > now,
            *filters,
        )
        .cte("ranked_attempts")
    )

    # Keep only each player's best eligible attempt.
    best_attempts = (
        select(
            ranked_attempts.c.score_id,
            ranked_attempts.c.display_name,
            ranked_attempts.c.data,
            ranked_attempts.c.ranking_value,
            ranked_attempts.c.created_at,
        )
        .where(ranked_attempts.c.attempt_number == 1)
        .cte("best_attempts")
    )

    # Define the global ordering for the selected attempts.
    if leaderboard_order == ("proximity",):
        rank_order = (
            best_attempts.c.ranking_value.asc(),
            best_attempts.c.created_at.asc(),
            best_attempts.c.score_id.asc(),
        )
    else:
        rank_order = (
            best_attempts.c.ranking_value.desc(),
            best_attempts.c.data["tile"].as_integer().desc(),
            best_attempts.c.created_at.asc(),
            best_attempts.c.score_id.asc(),
        )

    # Assign global ranks before applying pagination.
    ranked_entries = (
        select(
            best_attempts.c.display_name,
            best_attempts.c.data,
            best_attempts.c.created_at,
            func.row_number()
            .over(order_by=rank_order)
            .label("rank"),
        )
        .cte("ranked_entries")
    )

    # Count players, not individual score attempts.
    total_entries = db.scalar(
        select(func.count()).select_from(best_attempts)
    ) or 0

    # Retrieve only the requested page.
    rows = db.execute(
        select(
            ranked_entries.c.rank,
            ranked_entries.c.display_name,
            ranked_entries.c.data,
            ranked_entries.c.created_at,
        )
        .order_by(ranked_entries.c.rank.asc())
        .limit(limit)
        .offset(offset)
    ).mappings().all()

    entries = [
        LeaderboardEntry(**row)
        for row in rows
    ]

    return LeaderboardResponse(
        game_slug=game_slug,
        total_entries=total_entries,
        limit=limit,
        offset=offset,
        entries=entries,
    )
