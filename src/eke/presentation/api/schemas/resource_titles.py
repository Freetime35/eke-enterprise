"""Pydantic schemas for ResourceTitle operations."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class ResourceTitleCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    language: str = Field(min_length=2, max_length=35)
    value: str = Field(min_length=1)
    valid_from: date | None = None
    valid_to: date | None = None


class ResourceTitleResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    language: str
    value: str
    valid_from: date | None
    valid_to: date | None
