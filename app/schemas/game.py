from uuid import UUID

from pydantic import BaseModel, ConfigDict


class GameResponse(BaseModel):
    id: UUID
    slug: str
    name: str

    model_config = ConfigDict(from_attributes=True)
