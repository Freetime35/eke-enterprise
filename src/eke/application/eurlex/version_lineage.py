"""Source-backed EUR-Lex consolidated-act version lineage."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from enum import StrEnum

from eke.domain.identity import CelexIdentifier

_VERSION_IDENTIFIER_PATTERN = re.compile(
    r"^0(?P<year>\d{4})(?P<type>[A-Z])"
    r"(?P<number>\d{4})-(?P<date>\d{8})$"
)


@dataclass(frozen=True, slots=True)
class EurLexVersionIdentifier:
    """Identify one dated consolidated EUR-Lex version."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise TypeError("value must be a string")

        normalized = self.value.strip().upper()
        match = _VERSION_IDENTIFIER_PATTERN.fullmatch(
            normalized
        )
        if match is None:
            raise ValueError(
                "value must be a consolidated EUR-Lex "
                "version identifier"
            )

        try:
            date.fromisoformat(
                f"{match.group('date')[:4]}-"
                f"{match.group('date')[4:6]}-"
                f"{match.group('date')[6:]}"
            )
        except ValueError as exc:
            raise ValueError(
                "version identifier must contain "
                "a valid consolidation date"
            ) from exc

        object.__setattr__(
            self,
            "value",
            normalized,
        )

    @classmethod
    def parse(
        cls,
        value: str,
    ) -> EurLexVersionIdentifier:
        """Parse a consolidated EUR-Lex version identifier."""
        return cls(value)

    @property
    def consolidation_date(self) -> date:
        """Return the date embedded in the identifier."""
        raw_date = self.value.rsplit(
            "-",
            maxsplit=1,
        )[1]

        return date.fromisoformat(
            f"{raw_date[:4]}-"
            f"{raw_date[4:6]}-"
            f"{raw_date[6:]}"
        )


class EurLexVersionLineageKind(StrEnum):
    """Canonical roles within an EUR-Lex version lineage."""

    INITIAL_ACT = "INITIAL_ACT"
    CONSOLIDATED_VERSION = "CONSOLIDATED_VERSION"
    CODIFIED_VERSION = "CODIFIED_VERSION"
    RECAST_VERSION = "RECAST_VERSION"
    CORRIGENDUM = "CORRIGENDUM"


@dataclass(frozen=True, slots=True)
class EurLexVersionLineage:
    """Represent one explicit act or version in a legal lineage."""

    kind: EurLexVersionLineageKind
    source_predicate: str
    act_celex: CelexIdentifier | None = None
    version_identifier: (
        EurLexVersionIdentifier | None
    ) = None
    base_act: CelexIdentifier | None = None
    consolidation_date: date | None = None

    def __post_init__(self) -> None:
        if not isinstance(
            self.kind,
            EurLexVersionLineageKind,
        ):
            raise TypeError(
                "kind must be an "
                "EurLexVersionLineageKind"
            )

        if (
            self.act_celex is not None
            and not isinstance(
                self.act_celex,
                CelexIdentifier,
            )
        ):
            raise TypeError(
                "act_celex must be a "
                "CelexIdentifier or None"
            )

        if (
            self.version_identifier is not None
            and not isinstance(
                self.version_identifier,
                EurLexVersionIdentifier,
            )
        ):
            raise TypeError(
                "version_identifier must be an "
                "EurLexVersionIdentifier or None"
            )

        if (
            self.base_act is not None
            and not isinstance(
                self.base_act,
                CelexIdentifier,
            )
        ):
            raise TypeError(
                "base_act must be a "
                "CelexIdentifier or None"
            )

        if (
            self.consolidation_date is not None
            and not isinstance(
                self.consolidation_date,
                date,
            )
        ):
            raise TypeError(
                "consolidation_date must be a date or None"
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

        if (
            self.kind
            is EurLexVersionLineageKind
            .CONSOLIDATED_VERSION
        ):
            self._validate_consolidated_version()
        else:
            self._validate_legal_act_entry()

    def _validate_consolidated_version(
        self,
    ) -> None:
        """Validate a consolidated-version lineage entry."""
        if self.version_identifier is None:
            raise ValueError(
                "a consolidated version must define "
                "version_identifier"
            )

        if self.base_act is None:
            raise ValueError(
                "a consolidated version must identify "
                "its base act"
            )

        if self.act_celex is not None:
            raise ValueError(
                "a consolidated version must not use "
                "act_celex"
            )

        if (
            self.consolidation_date is not None
            and self.consolidation_date
            != self.version_identifier.consolidation_date
        ):
            raise ValueError(
                "consolidation_date must match the "
                "version identifier date"
            )

    def _validate_legal_act_entry(
        self,
    ) -> None:
        """Validate a non-consolidated lineage entry."""
        if self.act_celex is None:
            raise ValueError(
                "a non-consolidated lineage entry "
                "must define act_celex"
            )

        if self.version_identifier is not None:
            raise ValueError(
                "a non-consolidated lineage entry "
                "must not define version_identifier"
            )


_VERSION_KIND_BY_PREDICATE: dict[
    str,
    EurLexVersionLineageKind,
] = {
    "initial_act": (
        EurLexVersionLineageKind.INITIAL_ACT
    ),
    "work_initial_act": (
        EurLexVersionLineageKind.INITIAL_ACT
    ),
    "consolidated_version": (
        EurLexVersionLineageKind
        .CONSOLIDATED_VERSION
    ),
    "work_consolidated_version": (
        EurLexVersionLineageKind
        .CONSOLIDATED_VERSION
    ),
    "work_is_consolidated_by": (
        EurLexVersionLineageKind
        .CONSOLIDATED_VERSION
    ),
    "codified_version": (
        EurLexVersionLineageKind.CODIFIED_VERSION
    ),
    "work_codified_version": (
        EurLexVersionLineageKind.CODIFIED_VERSION
    ),
    "recast_version": (
        EurLexVersionLineageKind.RECAST_VERSION
    ),
    "work_recast_version": (
        EurLexVersionLineageKind.RECAST_VERSION
    ),
    "corrigendum": (
        EurLexVersionLineageKind.CORRIGENDUM
    ),
    "work_has_corrigendum": (
        EurLexVersionLineageKind.CORRIGENDUM
    ),
}


def version_lineage_kind_from_predicate(
    predicate: str,
) -> EurLexVersionLineageKind | None:
    """Resolve a supported version-lineage predicate."""
    if not isinstance(predicate, str):
        raise TypeError("predicate must be a string")

    normalized = (
        predicate.strip()
        .replace("-", "_")
        .casefold()
    )
    if not normalized:
        return None

    return _VERSION_KIND_BY_PREDICATE.get(
        normalized
    )


def _version_lineage_identifier_value(
    entry: EurLexVersionLineage,
) -> str:
    """Return the concrete identifier used for ordering."""
    if entry.version_identifier is not None:
        return entry.version_identifier.value

    if entry.act_celex is None:
        raise ValueError(
            "version lineage entry must define "
            "an identifier"
        )

    return entry.act_celex.value


def normalize_version_lineage(
    entries: tuple[EurLexVersionLineage, ...],
) -> tuple[EurLexVersionLineage, ...]:
    """Deduplicate and order version-lineage entries."""
    if not isinstance(entries, tuple):
        raise TypeError("entries must be a tuple")

    if any(
        not isinstance(
            entry,
            EurLexVersionLineage,
        )
        for entry in entries
    ):
        raise TypeError(
            "entries must contain "
            "EurLexVersionLineage values"
        )

    unique = dict.fromkeys(entries)

    return tuple(
        sorted(
            unique,
            key=lambda entry: (
                entry.consolidation_date is None,
                entry.consolidation_date or date.max,
                entry.kind.value,
                _version_lineage_identifier_value(
                    entry
                ),
                entry.source_predicate,
            ),
        )
    )