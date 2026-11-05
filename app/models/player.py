from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import text

from app.models.base import Base


class Player(Base):
    __tablename__ = "players"

    __table_args__ = (
        Index(
            "ix_players_display_name_lower",
            func.lower(text("display_name")),
            unique=True,
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    display_name: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    sessions = relationship("PlayerSession", back_populates="player")

    scores = relationship("Score", back_populates="player")
