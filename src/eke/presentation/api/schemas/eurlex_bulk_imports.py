"""Pydantic schemas for bulk EUR-Lex imports."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from eke.application.eurlex import EurLexBulkImportStatus


class EurLexBulkImportRequest(BaseModel):
    """Request import of several CELEX identifiers."""

    model_config = ConfigDict(extra="forbid")

    celex: list[str] = Field(
        min_length=1,
        max_length=100,
        examples=[["32023R1114", "32013R0575"]],
    )


class EurLexBulkImportItemResponse(BaseModel):
    """Represent one item in a bulk import response."""

    model_config = ConfigDict(extra="forbid")

    celex: str
    status: EurLexBulkImportStatus
    resource_uuid: str | None = None
    error_code: str | None = None
    detail: str | None = None


class EurLexBulkImportResponse(BaseModel):
    """Summarize a complete bulk import request."""

    model_config = ConfigDict(extra="forbid")

    total: int
    created: int
    existing: int
    failed: int
    items: list[EurLexBulkImportItemResponse]
