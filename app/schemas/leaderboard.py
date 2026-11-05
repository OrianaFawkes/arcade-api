from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class LeaderboardEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rank: int = Field(ge=1)
    display_name: str
    data: dict[str, Any]
    created_at: datetime


class LeaderboardResponse(BaseModel):
    game_slug: str
    total_entries: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)
    entries: list[LeaderboardEntry]
