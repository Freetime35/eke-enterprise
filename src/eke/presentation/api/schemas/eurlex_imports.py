"""Pydantic schemas for EUR-Lex imports."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from eke.presentation.api.schemas.resources import ResourceResponse


class EurLexImportRequest(BaseModel):
    """Request import of one legal resource by CELEX."""

    model_config = ConfigDict(extra="forbid")

    celex: str = Field(
        min_length=1,
        examples=["32023R1114"],
    )


class EurLexImportResponse(BaseModel):
    """Report the imported or previously existing Resource."""

    model_config = ConfigDict(extra="forbid")

    created: bool
    resource: ResourceResponse
