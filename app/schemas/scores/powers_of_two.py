from pydantic import BaseModel, ConfigDict, Field, field_validator


class PowersOfTwoScoreSubmission(BaseModel):
    model_config = ConfigDict(extra="forbid")

    score: int = Field(ge=0)
    tile: int = Field(ge=2)

    @field_validator("tile")
    @classmethod
    def validate_tile(cls, value: int) -> int:
        if value & (value - 1) != 0:
            raise ValueError("Tile must be a power of two.")

        return value
