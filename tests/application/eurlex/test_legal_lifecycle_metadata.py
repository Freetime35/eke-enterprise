"""Tests for legal lifecycle metadata integration."""

from datetime import date

import pytest

from eke.application.eurlex import (
    EurLexAmendmentEvent,
    EurLexLegalLifecycleEvent,
    EurLexLegalLifecycleEventKind,
    EurLexMetadata,
)
from eke.domain.identity import CelexIdentifier


def test_metadata_accepts_lifecycle_and_amendment_events() -> None:
    metadata = EurLexMetadata(
        celex_identifier=CelexIdentifier.parse(
            "32023R1114"
        ),
        legal_lifecycle=(
            EurLexLegalLifecycleEvent(
                kind=(
                    EurLexLegalLifecycleEventKind
                    .PUBLICATION
                ),
                occurred_on=date(2023, 6, 9),
                source_predicate="work_date_publication",
            ),
        ),
        amendment_events=(
            EurLexAmendmentEvent(
                amending_celex=CelexIdentifier.parse(
                    "32024R0001"
                ),
                amended_celex=CelexIdentifier.parse(
                    "32023R1114"
                ),
                effective_on=date(2024, 6, 1),
                source_predicate="amendment_event",
            ),
        ),
    )

    assert len(metadata.legal_lifecycle) == 1
    assert len(metadata.amendment_events) == 1


def test_metadata_rejects_invalid_lifecycle_values() -> None:
    with pytest.raises(
        TypeError,
        match="legal_lifecycle",
    ):
        EurLexMetadata(
            celex_identifier=CelexIdentifier.parse(
                "32023R1114"
            ),
            legal_lifecycle=(
                "PUBLICATION",  # type: ignore[arg-type]
            ),
        )
