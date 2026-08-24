from datetime import datetime
from enum import Enum

from pydantic import BaseModel, field_validator


class ConditionEnum(str, Enum):
    MINT = "mint"
    EXCELLENT = "excellent"
    VERY_GOOD = "very_good"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class TrackSchema(BaseModel):
    title: str
    duration: str | None = None


class RecordCreate(BaseModel):
    artist: str
    album: str
    year: int | None = None
    genre: str | None = None
    label: str | None = None
    condition: ConditionEnum | None = None
    tracks: list[TrackSchema] | None = None

    @field_validator("artist")
    @classmethod
    def validate_artist(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("artist must not be empty")
        return v

    @field_validator("year")
    @classmethod
    def validate_year(cls, v: int | None) -> int | None:
        if v is not None:
            if v < 1900:
                raise ValueError("year must be > 1900")
            from datetime import date

            if v > date.today().year + 1:
                raise ValueError("year must be <= current year + 1")
        return v

    @field_validator("tracks")
    @classmethod
    def validate_tracks(cls, v: list[TrackSchema] | None) -> list[TrackSchema] | None:
        if v is not None:
            for track in v:
                if not track.title.strip():
                    raise ValueError("track title must not be empty")
        return v


class RecordResponse(BaseModel):
    id: int
    artist: str
    album: str
    year: int | None = None
    genre: str | None = None
    label: str | None = None
    condition: str | None = None
    tracks: list[TrackSchema] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RecordListResponse(BaseModel):
    items: list[RecordResponse]
    total: int
    limit: int
    offset: int
