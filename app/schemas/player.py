from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PlayerResponse(BaseModel):
    id: UUID
    display_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SessionResponse(BaseModel):
    token: str
    expires_at: datetime


class PlayerCreateResponse(BaseModel):
    player: PlayerResponse
    session: SessionResponse