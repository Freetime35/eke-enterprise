"""Pydantic schemas for Resource classification operations."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from eke.domain.classification import ClassificationScheme


class ResourceClassificationCreateRequest(BaseModel):
    """Assign a classification concept to a Resource."""

    model_config = ConfigDict(extra="forbid")

    scheme: ClassificationScheme
    code: str = Field(min_length=1)
    language: str = Field(min_length=2, max_length=35)
    label: str = Field(min_length=1)
    valid_from: date | None = None
    valid_to: date | None = None


class ResourceClassificationResponse(BaseModel):
    """HTTP representation of a classification assignment."""

    model_config = ConfigDict(extra="forbid")

    scheme: ClassificationScheme
    code: str
    language: str
    label: str
    valid_from: date | None
    valid_to: date | None
