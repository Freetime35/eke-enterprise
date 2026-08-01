"""Shared HTTP error response schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class APIErrorResponse(BaseModel):
    """Stable application error representation."""

    model_config = ConfigDict(extra="forbid")

    code: str = Field(min_length=1)
    detail: str = Field(min_length=1)


class ValidationErrorItem(BaseModel):
    """One request validation failure."""

    model_config = ConfigDict(extra="allow")

    loc: list[str | int]
    msg: str
    type: str
    input: Any | None = None


class ValidationErrorResponse(BaseModel):
    """FastAPI-compatible request validation response."""

    model_config = ConfigDict(extra="forbid")

    detail: list[ValidationErrorItem]
