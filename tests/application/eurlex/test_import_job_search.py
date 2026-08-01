"""Tests for import-job search criteria and page values."""

from datetime import UTC, datetime

import pytest

from eke.application.eurlex import (
    ImportJobSearchCriteria,
)
from eke.domain.imports import ImportJobStatus


def test_search_criteria_accepts_filters() -> None:
    criteria = ImportJobSearchCriteria(
        status=ImportJobStatus.FAILED,
        created_from=datetime(
            2026, 8, 1, tzinfo=UTC
        ),
        created_to=datetime(
            2026, 8, 2, tzinfo=UTC
        ),
        limit=10,
        offset=20,
    )

    assert criteria.status is ImportJobStatus.FAILED
    assert criteria.limit == 10
    assert criteria.offset == 20


def test_search_criteria_rejects_invalid_window() -> None:
    with pytest.raises(
        ValueError,
        match="created_from must not be after created_to",
    ):
        ImportJobSearchCriteria(
            created_from=datetime(
                2026, 8, 2, tzinfo=UTC
            ),
            created_to=datetime(
                2026, 8, 1, tzinfo=UTC
            ),
        )
