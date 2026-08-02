"""Tests for legal lifecycle event values."""

from datetime import date

import pytest

from eke.application.eurlex import (
    EurLexLegalLifecycleEvent,
    EurLexLegalLifecycleEventKind,
    normalize_lifecycle_events,
)


def test_normalizes_lifecycle_events_chronologically() -> None:
    publication = EurLexLegalLifecycleEvent(
        kind=EurLexLegalLifecycleEventKind.PUBLICATION,
        occurred_on=date(2023, 6, 9),
        source_predicate="work_date_publication",
    )
    adoption = EurLexLegalLifecycleEvent(
        kind=EurLexLegalLifecycleEventKind.ADOPTION,
        occurred_on=date(2023, 5, 31),
        source_predicate="work_date_adoption",
    )

    assert normalize_lifecycle_events(
        (publication, adoption, adoption)
    ) == (
        adoption,
        publication,
    )


def test_lifecycle_event_rejects_invalid_date() -> None:
    with pytest.raises(
        TypeError,
        match="occurred_on",
    ):
        EurLexLegalLifecycleEvent(
            kind=(
                EurLexLegalLifecycleEventKind.PUBLICATION
            ),
            occurred_on="2023-06-09",  # type: ignore[arg-type]
            source_predicate="work_date_publication",
        )
