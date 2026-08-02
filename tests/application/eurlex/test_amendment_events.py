"""Tests for dated amendment events."""

from datetime import date

import pytest

from eke.application.eurlex import (
    EurLexAmendmentEvent,
    normalize_amendment_events,
)
from eke.domain.identity import CelexIdentifier


def test_normalizes_amendment_events() -> None:
    event = EurLexAmendmentEvent(
        amending_celex=CelexIdentifier.parse(
            "32024R0001"
        ),
        amended_celex=CelexIdentifier.parse(
            "32013R0575"
        ),
        effective_on=date(2024, 6, 1),
        source_predicate="amendment_event",
    )

    assert normalize_amendment_events(
        (event, event)
    ) == (event,)


def test_amendment_rejects_self_reference() -> None:
    celex = CelexIdentifier.parse("32013R0575")

    with pytest.raises(
        ValueError,
        match="different CELEX",
    ):
        EurLexAmendmentEvent(
            amending_celex=celex,
            amended_celex=celex,
            effective_on=date(2024, 6, 1),
            source_predicate="amendment_event",
        )
