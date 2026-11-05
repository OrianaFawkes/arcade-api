from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Index,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Score(Base):
    __tablename__ = "scores"

    __table_args__ = (
        Index(
            "ix_scores_game_leaderboard",
            "game_id",
            "archived_at",
            "ranking_value",
        ),
        Index(
            "ix_scores_player_history",
            "player_id",
            "game_id",
            "archived_at",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    player_id: Mapped[UUID] = mapped_column(
        ForeignKey("players.id", ondelete="RESTRICT"),
        nullable=False,
    )

    game_id: Mapped[UUID] = mapped_column(
        ForeignKey("games.id", ondelete="RESTRICT"),
        nullable=False,
    )

    data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
    )

    ranking_value: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    player = relationship("Player", back_populates="scores")

    game = relationship("Game", back_populates="scores")
