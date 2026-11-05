from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ProximityDifficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class ProximityScoreSubmission(BaseModel):
    model_config = ConfigDict(extra="forbid")
    
    difficulty: ProximityDifficulty
    elapsed_seconds: int = Field(gt=0)