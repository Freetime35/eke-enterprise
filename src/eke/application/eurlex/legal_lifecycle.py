"""Source-backed EUR-Lex legal lifecycle and amendment events."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum

from eke.domain.identity import CelexIdentifier


class EurLexLegalLifecycleEventKind(StrEnum):
    """Canonical legal lifecycle milestones."""

    DOCUMENT = "DOCUMENT"
    ADOPTION = "ADOPTION"
    SIGNATURE = "SIGNATURE"
    NOTIFICATION = "NOTIFICATION"
    PUBLICATION = "PUBLICATION"
    ENTRY_INTO_FORCE = "ENTRY_INTO_FORCE"
    TAKING_EFFECT = "TAKING_EFFECT"
    APPLICATION = "APPLICATION"
    TRANSPOSITION_DEADLINE = "TRANSPOSITION_DEADLINE"
    END_OF_VALIDITY = "END_OF_VALIDITY"
    REPEAL = "REPEAL"
    WITHDRAWAL = "WITHDRAWAL"


@dataclass(frozen=True, slots=True)
class EurLexLegalLifecycleEvent:
    """Represent one dated legal lifecycle milestone."""

    kind: EurLexLegalLifecycleEventKind
    occurred_on: date
    source_predicate: str

    def __post_init__(self) -> None:
        if not isinstance(
            self.kind,
            EurLexLegalLifecycleEventKind,
        ):
            raise TypeError(
                "kind must be an "
                "EurLexLegalLifecycleEventKind"
            )
        if not isinstance(self.occurred_on, date):
            raise TypeError("occurred_on must be a date")
        if not isinstance(self.source_predicate, str):
            raise TypeError(
                "source_predicate must be a string"
            )

        normalized = " ".join(
            self.source_predicate.split()
        )
        if not normalized:
            raise ValueError(
                "source_predicate must not be empty"
            )
        object.__setattr__(
            self,
            "source_predicate",
            normalized,
        )


@dataclass(frozen=True, slots=True)
class EurLexAmendmentEvent:
    """Represent one explicitly dated amendment impact."""

    amending_celex: CelexIdentifier
    amended_celex: CelexIdentifier
    effective_on: date
    source_predicate: str

    def __post_init__(self) -> None:
        if not isinstance(
            self.amending_celex,
            CelexIdentifier,
        ):
            raise TypeError(
                "amending_celex must be a CelexIdentifier"
            )
        if not isinstance(
            self.amended_celex,
            CelexIdentifier,
        ):
            raise TypeError(
                "amended_celex must be a CelexIdentifier"
            )
        if self.amending_celex == self.amended_celex:
            raise ValueError(
                "an amendment must reference two "
                "different CELEX identifiers"
            )
        if not isinstance(self.effective_on, date):
            raise TypeError("effective_on must be a date")
        if not isinstance(self.source_predicate, str):
            raise TypeError(
                "source_predicate must be a string"
            )

        normalized = " ".join(
            self.source_predicate.split()
        )
        if not normalized:
            raise ValueError(
                "source_predicate must not be empty"
            )
        object.__setattr__(
            self,
            "source_predicate",
            normalized,
        )


def normalize_lifecycle_events(
    events: tuple[EurLexLegalLifecycleEvent, ...],
) -> tuple[EurLexLegalLifecycleEvent, ...]:
    """Deduplicate and order lifecycle events chronologically."""
    if not isinstance(events, tuple):
        raise TypeError("events must be a tuple")
    if any(
        not isinstance(
            event,
            EurLexLegalLifecycleEvent,
        )
        for event in events
    ):
        raise TypeError(
            "events must contain "
            "EurLexLegalLifecycleEvent values"
        )

    unique = dict.fromkeys(events)
    return tuple(
        sorted(
            unique,
            key=lambda event: (
                event.occurred_on,
                event.kind.value,
                event.source_predicate,
            ),
        )
    )


def normalize_amendment_events(
    events: tuple[EurLexAmendmentEvent, ...],
) -> tuple[EurLexAmendmentEvent, ...]:
    """Deduplicate and order amendment events chronologically."""
    if not isinstance(events, tuple):
        raise TypeError("events must be a tuple")
    if any(
        not isinstance(event, EurLexAmendmentEvent)
        for event in events
    ):
        raise TypeError(
            "events must contain EurLexAmendmentEvent values"
        )

    unique = dict.fromkeys(events)
    return tuple(
        sorted(
            unique,
            key=lambda event: (
                event.effective_on,
                event.amending_celex.value,
                event.amended_celex.value,
                event.source_predicate,
            ),
        )
    )
