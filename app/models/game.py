from datetime import datetime
from typing import List
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class Game(Base):
    __tablename__ = "games"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    slug: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    scores = relationship("Score", back_populates="game")
