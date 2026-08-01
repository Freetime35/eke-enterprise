"""Tests for Resource search criteria and pages."""

from __future__ import annotations

import pytest

from eke.domain.repositories import (
    ResourceSearchCriteria,
    ResourceSearchPage,
)


def test_default_search_criteria() -> None:
    criteria = ResourceSearchCriteria()

    assert criteria.limit == 20
    assert criteria.offset == 0


@pytest.mark.parametrize("limit", [0, 101])
def test_invalid_limit_is_rejected(limit: int) -> None:
    with pytest.raises(
        ValueError,
        match="limit must be between 1 and 100",
    ):
        ResourceSearchCriteria(limit=limit)


def test_negative_offset_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="offset must be greater than or equal to zero",
    ):
        ResourceSearchCriteria(offset=-1)


def test_empty_search_page_is_valid() -> None:
    page = ResourceSearchPage(
        items=(),
        total=0,
        limit=20,
        offset=0,
    )

    assert page.items == ()
    assert page.total == 0
