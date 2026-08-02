"""Detect financial regulatory families from explicit evidence."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol, runtime_checkable

from eke.domain.identity import CelexIdentifier
from eke.domain.localization import LanguageCode


@runtime_checkable
class RegulatoryFamilyTitle(Protocol):
    """Expose the title data required for family detection."""

    @property
    def language(self) -> LanguageCode | None:
        """Return the title language."""

    @property
    def value(self) -> str:
        """Return the normalized title value."""


class EurLexRegulatoryFamily(StrEnum):
    """Canonical financial regulatory families."""

    MICA = "MICA"
    DORA = "DORA"
    CRR = "CRR"
    CRD = "CRD"
    BRRD = "BRRD"
    SRMR = "SRMR"
    PSD = "PSD"
    PSD2 = "PSD2"
    PSD3 = "PSD3"
    MIFID = "MIFID"
    MIFID_II = "MIFID_II"
    MIFIR = "MIFIR"
    EMIR = "EMIR"
    SFDR = "SFDR"
    UCITS = "UCITS"
    AIFMD = "AIFMD"
    SOLVENCY_II = "SOLVENCY_II"


class RegulatoryFamilyEvidenceKind(StrEnum):
    """Describe the source of one family match."""

    TITLE = "TITLE"
    CELEX = "CELEX"


@dataclass(frozen=True, slots=True)
class EurLexRegulatoryFamilyMatch:
    """Represent one source-backed family detection."""

    family: EurLexRegulatoryFamily
    matched_value: str
    evidence_kind: RegulatoryFamilyEvidenceKind

    def __post_init__(self) -> None:
        if not isinstance(
            self.family,
            EurLexRegulatoryFamily,
        ):
            raise TypeError(
                "family must be an "
                "EurLexRegulatoryFamily"
            )

        if not isinstance(
            self.evidence_kind,
            RegulatoryFamilyEvidenceKind,
        ):
            raise TypeError(
                "evidence_kind must be a "
                "RegulatoryFamilyEvidenceKind"
            )

        if not isinstance(
            self.matched_value,
            str,
        ):
            raise TypeError(
                "matched_value must be a string"
            )

        normalized = " ".join(
            self.matched_value.split()
        )
        if not normalized:
            raise ValueError(
                "matched_value must not be empty"
            )

        object.__setattr__(
            self,
            "matched_value",
            normalized,
        )


_TITLE_PATTERNS: tuple[
    tuple[
        EurLexRegulatoryFamily,
        tuple[re.Pattern[str], ...],
    ],
    ...,
] = (
    (
        EurLexRegulatoryFamily.MICA,
        (
            re.compile(
                r"\bMiCA\b",
                re.IGNORECASE,
            ),
            re.compile(
                r"markets in crypto-assets",
                re.IGNORECASE,
            ),
        ),
    ),
    (
        EurLexRegulatoryFamily.DORA,
        (
            re.compile(
                r"\bDORA\b",
                re.IGNORECASE,
            ),
            re.compile(
                r"digital operational resilience",
                re.IGNORECASE,
            ),
        ),
    ),
    (
        EurLexRegulatoryFamily.CRR,
        (
            re.compile(
                r"\bCRR(?:\s*[23])?\b",
                re.IGNORECASE,
            ),
            re.compile(
                r"capital requirements regulation",
                re.IGNORECASE,
            ),
        ),
    ),
    (
        EurLexRegulatoryFamily.CRD,
        (
            re.compile(
                r"\bCRD(?:\s*(?:IV|V|VI|4|5|6))?\b",
                re.IGNORECASE,
            ),
            re.compile(
                r"capital requirements directive",
                re.IGNORECASE,
            ),
        ),
    ),
    (
        EurLexRegulatoryFamily.BRRD,
        (
            re.compile(
                r"\bBRRD(?:\s*II)?\b",
                re.IGNORECASE,
            ),
            re.compile(
                r"bank recovery and resolution directive",
                re.IGNORECASE,
            ),
        ),
    ),
    (
        EurLexRegulatoryFamily.SRMR,
        (
            re.compile(
                r"\bSRMR(?:\s*II)?\b",
                re.IGNORECASE,
            ),
            re.compile(
                r"single resolution mechanism regulation",
                re.IGNORECASE,
            ),
        ),
    ),
    (
        EurLexRegulatoryFamily.PSD3,
        (
            re.compile(
                r"\bPSD\s*3\b",
                re.IGNORECASE,
            ),
            re.compile(
                r"third payment services directive",
                re.IGNORECASE,
            ),
        ),
    ),
    (
        EurLexRegulatoryFamily.PSD2,
        (
            re.compile(
                r"\bPSD\s*2\b",
                re.IGNORECASE,
            ),
            re.compile(
                r"second payment services directive",
                re.IGNORECASE,
            ),
        ),
    ),
    (
        EurLexRegulatoryFamily.PSD,
        (
            re.compile(
                r"\bPSD\b",
                re.IGNORECASE,
            ),
            re.compile(
                r"payment services directive",
                re.IGNORECASE,
            ),
        ),
    ),
    (
        EurLexRegulatoryFamily.MIFID_II,
        (
            re.compile(
                r"\bMiFID\s*II\b",
                re.IGNORECASE,
            ),
            re.compile(
                r"markets in financial instruments "
                r"directive II",
                re.IGNORECASE,
            ),
        ),
    ),
    (
        EurLexRegulatoryFamily.MIFID,
        (
            re.compile(
                r"\bMiFID\b(?!\s*II)",
                re.IGNORECASE,
            ),
            re.compile(
                r"markets in financial instruments directive(?!\s*II)"
                r"directive",
                re.IGNORECASE,
            ),
        ),
    ),
    (
        EurLexRegulatoryFamily.MIFIR,
        (
            re.compile(
                r"\bMiFIR\b",
                re.IGNORECASE,
            ),
            re.compile(
                r"markets in financial instruments "
                r"regulation",
                re.IGNORECASE,
            ),
        ),
    ),
    (
        EurLexRegulatoryFamily.EMIR,
        (
            re.compile(
                r"\bEMIR\b",
                re.IGNORECASE,
            ),
            re.compile(
                r"european market infrastructure "
                r"regulation",
                re.IGNORECASE,
            ),
        ),
    ),
    (
        EurLexRegulatoryFamily.SFDR,
        (
            re.compile(
                r"\bSFDR\b",
                re.IGNORECASE,
            ),
            re.compile(
                r"sustainable finance disclosure "
                r"regulation",
                re.IGNORECASE,
            ),
        ),
    ),
    (
        EurLexRegulatoryFamily.UCITS,
        (
            re.compile(
                r"\bUCITS\b",
                re.IGNORECASE,
            ),
            re.compile(
                r"undertakings for collective investment "
                r"in transferable securities",
                re.IGNORECASE,
            ),
        ),
    ),
    (
        EurLexRegulatoryFamily.AIFMD,
        (
            re.compile(
                r"\bAIFMD\b",
                re.IGNORECASE,
            ),
            re.compile(
                r"alternative investment fund managers "
                r"directive",
                re.IGNORECASE,
            ),
        ),
    ),
    (
        EurLexRegulatoryFamily.SOLVENCY_II,
        (
            re.compile(
                r"\bSolvency\s*II\b",
                re.IGNORECASE,
            ),
        ),
    ),
)


_CELEX_FAMILIES: dict[
    str,
    EurLexRegulatoryFamily,
] = {
    "32023R1114": EurLexRegulatoryFamily.MICA,
    "32022R2554": EurLexRegulatoryFamily.DORA,
    "32013R0575": EurLexRegulatoryFamily.CRR,
    "32013L0036": EurLexRegulatoryFamily.CRD,
    "32014L0059": EurLexRegulatoryFamily.BRRD,
    "32014R0806": EurLexRegulatoryFamily.SRMR,
    "32007L0064": EurLexRegulatoryFamily.PSD,
    "32015L2366": EurLexRegulatoryFamily.PSD2,
    "32014L0065": EurLexRegulatoryFamily.MIFID_II,
    "32004L0039": EurLexRegulatoryFamily.MIFID,
    "32014R0600": EurLexRegulatoryFamily.MIFIR,
    "32012R0648": EurLexRegulatoryFamily.EMIR,
    "32019R2088": EurLexRegulatoryFamily.SFDR,
    "32009L0065": EurLexRegulatoryFamily.UCITS,
    "32011L0061": EurLexRegulatoryFamily.AIFMD,
    "32009L0138": EurLexRegulatoryFamily.SOLVENCY_II,
}


def detect_regulatory_families(
    celex_identifier: CelexIdentifier,
    titles: tuple[RegulatoryFamilyTitle, ...],
) -> tuple[EurLexRegulatoryFamilyMatch, ...]:
    """Detect unique families from explicit CELEX/title evidence."""
    if not isinstance(
        celex_identifier,
        CelexIdentifier,
    ):
        raise TypeError(
            "celex_identifier must be a "
            "CelexIdentifier"
        )

    if not isinstance(titles, tuple):
        raise TypeError("titles must be a tuple")

    if any(
        not isinstance(
            title,
            RegulatoryFamilyTitle,
        )
        for title in titles
    ):
        raise TypeError(
            "titles must contain values exposing "
            "language and value"
        )

    matches: list[
        EurLexRegulatoryFamilyMatch
    ] = []
    seen: set[EurLexRegulatoryFamily] = set()

    celex_family = _CELEX_FAMILIES.get(
        celex_identifier.value
    )
    if celex_family is not None:
        matches.append(
            EurLexRegulatoryFamilyMatch(
                family=celex_family,
                matched_value=celex_identifier.value,
                evidence_kind=(
                    RegulatoryFamilyEvidenceKind.CELEX
                ),
            )
        )
        seen.add(celex_family)

    for title in titles:
        if (
            title.language is None
            or title.language.value != "en"
        ):
            continue

        for family, patterns in _TITLE_PATTERNS:
            if family in seen:
                continue

            if not any(
                pattern.search(title.value)
                for pattern in patterns
            ):
                continue

            matches.append(
                EurLexRegulatoryFamilyMatch(
                    family=family,
                    matched_value=title.value,
                    evidence_kind=(
                        RegulatoryFamilyEvidenceKind.TITLE
                    ),
                )
            )
            seen.add(family)

    return tuple(matches)