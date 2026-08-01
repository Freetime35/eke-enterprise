"""Tests for shared HTTP error schemas."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from eke.presentation.api.schemas import (
    APIErrorResponse,
    ValidationErrorItem,
    ValidationErrorResponse,
)


def test_api_error_response_is_strict() -> None:
    response = APIErrorResponse(
        code="resource_not_found",
        detail="resource not found",
    )

    assert response.model_dump() == {
        "code": "resource_not_found",
        "detail": "resource not found",
    }


def test_api_error_response_rejects_empty_values() -> None:
    with pytest.raises(ValidationError):
        APIErrorResponse(code="", detail="")


def test_validation_error_response_accepts_fastapi_shape() -> None:
    response = ValidationErrorResponse(
        detail=[
            ValidationErrorItem(
                loc=["body", "status"],
                msg="Input should be valid",
                type="enum",
                input="INVALID",
            )
        ]
    )

    assert response.detail[0].loc == ["body", "status"]
