"""Source-backed EUR-Lex corrigenda and identifiers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

from eke.domain.identity import CelexIdentifier

_CORRIGENDUM_IDENTIFIER_PATTERN = re.compile(
    r"^(?P<base>\d[A-Z0-9]{9})R\((?P<sequence>\d{2})\)$"
)


@dataclass(frozen=True, slots=True)
class EurLexCorrigendumIdentifier:
    """Identify one EUR-Lex corrigendum."""

    base_act: CelexIdentifier
    sequence: int

    def __post_init__(self) -> None:
        if not isinstance(
            self.base_act,
            CelexIdentifier,
        ):
            raise TypeError(
                "base_act must be a CelexIdentifier"
            )

        if not isinstance(self.sequence, int):
            raise TypeError(
                "sequence must be an integer"
            )

        if isinstance(self.sequence, bool):
            raise TypeError(
                "sequence must be an integer"
            )

        if self.sequence <= 0:
            raise ValueError(
                "sequence must be strictly positive"
            )

        if self.sequence > 99:
            raise ValueError(
                "sequence must not exceed 99"
            )

    @classmethod
    def parse(
        cls,
        value: str,
    ) -> EurLexCorrigendumIdentifier:
        """Parse a canonical EUR-Lex corrigendum identifier."""
        if not isinstance(value, str):
            raise TypeError("value must be a string")

        normalized = value.strip().upper()

        match = _CORRIGENDUM_IDENTIFIER_PATTERN.fullmatch(
            normalized
        )
        if match is None:
            raise ValueError(
                "value must be an EUR-Lex corrigendum "
                "identifier"
            )

        base_value = match.group("base")

        # Corrigenda always refer to legal acts, never to
        # consolidated-version identifiers (which begin with '0').
        if base_value.startswith("0"):
            raise ValueError(
                "corrigenda must reference a legal act "
                "rather than a consolidated version"
            )

        return cls(
            base_act=CelexIdentifier.parse(
                base_value
            ),
            sequence=int(
                match.group("sequence")
            ),
        )

    @property
    def value(self) -> str:
        """Return the canonical corrigendum identifier."""
        return (
            f"{self.base_act.value}"
            f"R({self.sequence:02d})"
        )


@dataclass(frozen=True, slots=True)
class EurLexCorrigendum:
    """Represent one explicit corrigendum relation."""

    identifier: EurLexCorrigendumIdentifier
    source_predicate: str
    publication_date: date | None = None

    def __post_init__(self) -> None:
        if not isinstance(
            self.identifier,
            EurLexCorrigendumIdentifier,
        ):
            raise TypeError(
                "identifier must be an "
                "EurLexCorrigendumIdentifier"
            )

        if (
            self.publication_date is not None
            and not isinstance(
                self.publication_date,
                date,
            )
        ):
            raise TypeError(
                "publication_date must be a date or None"
            )

        if not isinstance(
            self.source_predicate,
            str,
        ):
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

    @property
    def corrected_act(self) -> CelexIdentifier:
        """Return the act corrected by this corrigendum."""
        return self.identifier.base_act


def normalize_corrigenda(
    corrigenda: tuple[EurLexCorrigendum, ...],
) -> tuple[EurLexCorrigendum, ...]:
    """Deduplicate and order corrigenda deterministically."""
    if not isinstance(corrigenda, tuple):
        raise TypeError("corrigenda must be a tuple")

    if any(
        not isinstance(
            corrigendum,
            EurLexCorrigendum,
        )
        for corrigendum in corrigenda
    ):
        raise TypeError(
            "corrigenda must contain "
            "EurLexCorrigendum values"
        )

    unique = dict.fromkeys(corrigenda)

    return tuple(
        sorted(
            unique,
            key=lambda corrigendum: (
                corrigendum.corrected_act.value,
                corrigendum.identifier.sequence,
                corrigendum.publication_date is None,
                corrigendum.publication_date or date.max,
                corrigendum.source_predicate,
            ),
        )
    )