"""Normalize EUR-Lex institutional provenance."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from eke.domain.provenance import ProvenanceSource


class EurLexInstitutionType(StrEnum):
    """Canonical type for a recognized EU institution."""

    EU_INSTITUTION = "EU_INSTITUTION"
    EU_BODY = "EU_BODY"
    EU_AGENCY = "EU_AGENCY"
    EU_COURT = "EU_COURT"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class EurLexInstitution:
    """Represent one normalized institution from EUR-Lex."""

    uri: str
    name: str
    short_name: str | None
    institution_type: EurLexInstitutionType
    provenance_source: ProvenanceSource | None = None

    def __post_init__(self) -> None:
        for field_name, value in (
            ("uri", self.uri),
            ("name", self.name),
        ):
            if not isinstance(value, str):
                raise TypeError(
                    f"{field_name} must be a string"
                )
            normalized = " ".join(value.split())
            if not normalized:
                raise ValueError(
                    f"{field_name} must not be empty"
                )
            object.__setattr__(
                self,
                field_name,
                normalized,
            )

        if self.short_name is not None:
            if not isinstance(self.short_name, str):
                raise TypeError(
                    "short_name must be a string or None"
                )
            normalized_short_name = " ".join(
                self.short_name.split()
            )
            object.__setattr__(
                self,
                "short_name",
                normalized_short_name or None,
            )

        if not isinstance(
            self.institution_type,
            EurLexInstitutionType,
        ):
            raise TypeError(
                "institution_type must be an "
                "EurLexInstitutionType"
            )

        if (
            self.provenance_source is not None
            and not isinstance(
                self.provenance_source,
                ProvenanceSource,
            )
        ):
            raise TypeError(
                "provenance_source must be a "
                "ProvenanceSource or None"
            )


_INSTITUTIONS: dict[
    str,
    tuple[
        str,
        str | None,
        EurLexInstitutionType,
        ProvenanceSource | None,
    ],
] = {
    "ECB": (
        "European Central Bank",
        "ECB",
        EurLexInstitutionType.EU_INSTITUTION,
        ProvenanceSource.ECB,
    ),
    "EBA": (
        "European Banking Authority",
        "EBA",
        EurLexInstitutionType.EU_AGENCY,
        ProvenanceSource.EBA,
    ),
    "ESMA": (
        "European Securities and Markets Authority",
        "ESMA",
        EurLexInstitutionType.EU_AGENCY,
        ProvenanceSource.ESMA,
    ),
    "EIOPA": (
        "European Insurance and Occupational "
        "Pensions Authority",
        "EIOPA",
        EurLexInstitutionType.EU_AGENCY,
        ProvenanceSource.EIOPA,
    ),
    "SRB": (
        "Single Resolution Board",
        "SRB",
        EurLexInstitutionType.EU_BODY,
        ProvenanceSource.SRB,
    ),
    "COM": (
        "European Commission",
        "Commission",
        EurLexInstitutionType.EU_INSTITUTION,
        None,
    ),
    "EP": (
        "European Parliament",
        "Parliament",
        EurLexInstitutionType.EU_INSTITUTION,
        None,
    ),
    "CONSIL": (
        "Council of the European Union",
        "Council",
        EurLexInstitutionType.EU_INSTITUTION,
        None,
    ),
    "CJUE": (
        "Court of Justice of the European Union",
        "CJEU",
        EurLexInstitutionType.EU_COURT,
        None,
    ),
}


def institution_from_uri(
    uri: str,
) -> EurLexInstitution:
    """Normalize a corporate-body URI deterministically."""
    if not isinstance(uri, str):
        raise TypeError("uri must be a string")

    normalized_uri = uri.strip()
    if not normalized_uri:
        raise ValueError("uri must not be empty")

    token = (
        normalized_uri.rstrip("/")
        .rsplit("/", maxsplit=1)[-1]
        .replace("-", "_")
        .upper()
    )
    resolved = _INSTITUTIONS.get(token)

    if resolved is None:
        return EurLexInstitution(
            uri=normalized_uri,
            name=token.replace("_", " ").title(),
            short_name=None,
            institution_type=(
                EurLexInstitutionType.UNKNOWN
            ),
            provenance_source=None,
        )

    (
        name,
        short_name,
        institution_type,
        provenance_source,
    ) = resolved

    return EurLexInstitution(
        uri=normalized_uri,
        name=name,
        short_name=short_name,
        institution_type=institution_type,
        provenance_source=provenance_source,
    )


def normalize_institutions(
    uris: tuple[str, ...],
) -> tuple[EurLexInstitution, ...]:
    """Normalize and deduplicate institutions by source URI."""
    institutions: list[EurLexInstitution] = []
    seen: set[str] = set()

    for uri in uris:
        institution = institution_from_uri(uri)
        if institution.uri in seen:
            continue
        seen.add(institution.uri)
        institutions.append(institution)

    return tuple(institutions)
