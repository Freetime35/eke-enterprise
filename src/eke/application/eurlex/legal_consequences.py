"""Explicit legal consequences derived from EUR-Lex compliance rules."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


def _normalize_required_text(
    value: str,
    *,
    name: str,
) -> str:
    if not isinstance(value, str):
        raise TypeError(
            f"{name} must be a string"
        )

    normalized = " ".join(value.split())
    if not normalized:
        raise ValueError(
            f"{name} must not be empty"
        )

    return normalized


def _normalize_optional_text(
    value: str | None,
    *,
    name: str,
) -> str | None:
    if value is None:
        return None

    if not isinstance(value, str):
        raise TypeError(
            f"{name} must be a string or None"
        )

    normalized = " ".join(value.split())
    return normalized or None


def _normalize_identifier_tuple(
    values: tuple[str, ...],
    *,
    name: str,
) -> tuple[str, ...]:
    if not isinstance(values, tuple):
        raise TypeError(
            f"{name} must be a tuple"
        )

    normalized: list[str] = []
    for value in values:
        normalized.append(
            _normalize_required_text(
                value,
                name=name,
            )
        )

    return tuple(
        dict.fromkeys(normalized)
    )


class EurLexLegalConsequenceKind(StrEnum):
    """Canonical kinds of explicit legal consequences."""

    FINE = "FINE"
    ADMINISTRATIVE_PENALTY = (
        "ADMINISTRATIVE_PENALTY"
    )
    CRIMINAL_PENALTY = "CRIMINAL_PENALTY"
    SUSPENSION = "SUSPENSION"
    REVOCATION = "REVOCATION"
    WITHDRAWAL = "WITHDRAWAL"
    REJECTION = "REJECTION"
    RECOVERY = "RECOVERY"
    INVALIDATION = "INVALIDATION"
    OTHER = "OTHER"


class EurLexLegalConsequenceModality(StrEnum):
    """Canonical modalities of legal consequences."""

    MANDATORY = "MANDATORY"
    PERMITTED = "PERMITTED"
    POSSIBLE = "POSSIBLE"


@dataclass(frozen=True, slots=True)
class EurLexLegalConsequence:
    """Represent one explicit source-backed consequence."""

    consequence_id: str
    kind: EurLexLegalConsequenceKind
    modality: EurLexLegalConsequenceModality
    text: str
    action_text: str
    source_rule_id: str
    source_requirement_id: str
    source_node_id: str
    source_text: str
    subject_text: str | None = None
    source_qualifier_id: str | None = None
    quantitative_threshold_ids: tuple[str, ...] = ()
    temporal_constraint_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in (
            "consequence_id",
            "text",
            "action_text",
            "source_rule_id",
            "source_requirement_id",
            "source_node_id",
            "source_text",
        ):
            object.__setattr__(
                self,
                name,
                _normalize_required_text(
                    getattr(self, name),
                    name=name,
                ),
            )

        for name in (
            "subject_text",
            "source_qualifier_id",
        ):
            object.__setattr__(
                self,
                name,
                _normalize_optional_text(
                    getattr(self, name),
                    name=name,
                ),
            )

        object.__setattr__(
            self,
            "quantitative_threshold_ids",
            _normalize_identifier_tuple(
                self.quantitative_threshold_ids,
                name="quantitative_threshold_ids",
            ),
        )
        object.__setattr__(
            self,
            "temporal_constraint_ids",
            _normalize_identifier_tuple(
                self.temporal_constraint_ids,
                name="temporal_constraint_ids",
            ),
        )

        if not isinstance(
            self.kind,
            EurLexLegalConsequenceKind,
        ):
            raise TypeError(
                "kind must be an "
                "EurLexLegalConsequenceKind"
            )

        if not isinstance(
            self.modality,
            EurLexLegalConsequenceModality,
        ):
            raise TypeError(
                "modality must be an "
                "EurLexLegalConsequenceModality"
            )


@dataclass(frozen=True, slots=True)
class EurLexLegalConsequences:
    """Contain explicit legal consequences."""

    consequences: tuple[
        EurLexLegalConsequence,
        ...,
    ] = ()

    def __post_init__(self) -> None:
        if not isinstance(
            self.consequences,
            tuple,
        ):
            raise TypeError(
                "consequences must be a tuple"
            )

        if any(
            not isinstance(
                consequence,
                EurLexLegalConsequence,
            )
            for consequence in self.consequences
        ):
            raise TypeError(
                "consequences must contain "
                "EurLexLegalConsequence values"
            )

        consequence_ids = tuple(
            consequence.consequence_id
            for consequence in self.consequences
        )
        if len(consequence_ids) != len(
            set(consequence_ids)
        ):
            raise ValueError(
                "consequence identifiers must be unique"
            )

    def consequence_by_id(
        self,
        consequence_id: str,
    ) -> EurLexLegalConsequence | None:
        """Return one consequence by identifier."""
        normalized = _normalize_required_text(
            consequence_id,
            name="consequence_id",
        )

        return next(
            (
                consequence
                for consequence in self.consequences
                if consequence.consequence_id
                == normalized
            ),
            None,
        )

    def consequences_for_rule(
        self,
        source_rule_id: str,
    ) -> tuple[EurLexLegalConsequence, ...]:
        """Return consequences attached to one rule."""
        normalized = _normalize_required_text(
            source_rule_id,
            name="source_rule_id",
        )

        return tuple(
            consequence
            for consequence in self.consequences
            if consequence.source_rule_id
            == normalized
        )

    def consequences_for_qualifier(
        self,
        source_qualifier_id: str,
    ) -> tuple[EurLexLegalConsequence, ...]:
        """Return consequences attached to one qualifier."""
        normalized = _normalize_required_text(
            source_qualifier_id,
            name="source_qualifier_id",
        )

        return tuple(
            consequence
            for consequence in self.consequences
            if consequence.source_qualifier_id
            == normalized
        )

    def consequences_by_kind(
        self,
        kind: EurLexLegalConsequenceKind,
    ) -> tuple[EurLexLegalConsequence, ...]:
        """Return consequences of one kind."""
        if not isinstance(
            kind,
            EurLexLegalConsequenceKind,
        ):
            raise TypeError(
                "kind must be an "
                "EurLexLegalConsequenceKind"
            )

        return tuple(
            consequence
            for consequence in self.consequences
            if consequence.kind is kind
        )

    def consequences_by_modality(
        self,
        modality: EurLexLegalConsequenceModality,
    ) -> tuple[EurLexLegalConsequence, ...]:
        """Return consequences with one modality."""
        if not isinstance(
            modality,
            EurLexLegalConsequenceModality,
        ):
            raise TypeError(
                "modality must be an "
                "EurLexLegalConsequenceModality"
            )

        return tuple(
            consequence
            for consequence in self.consequences
            if consequence.modality is modality
        )

    def consequences_for_threshold(
        self,
        threshold_id: str,
    ) -> tuple[EurLexLegalConsequence, ...]:
        """Return consequences linked to one threshold."""
        normalized = _normalize_required_text(
            threshold_id,
            name="threshold_id",
        )

        return tuple(
            consequence
            for consequence in self.consequences
            if normalized
            in consequence.quantitative_threshold_ids
        )

    def consequences_for_temporal_constraint(
        self,
        temporal_constraint_id: str,
    ) -> tuple[EurLexLegalConsequence, ...]:
        """Return consequences linked to one temporal constraint."""
        normalized = _normalize_required_text(
            temporal_constraint_id,
            name="temporal_constraint_id",
        )

        return tuple(
            consequence
            for consequence in self.consequences
            if normalized
            in consequence.temporal_constraint_ids
        )


def normalize_legal_consequences(
    consequences: tuple[
        EurLexLegalConsequence,
        ...,
    ],
) -> EurLexLegalConsequences:
    """Deduplicate consequences while preserving source order."""
    if not isinstance(
        consequences,
        tuple,
    ):
        raise TypeError(
            "consequences must be a tuple"
        )

    if any(
        not isinstance(
            consequence,
            EurLexLegalConsequence,
        )
        for consequence in consequences
    ):
        raise TypeError(
            "consequences must contain "
            "EurLexLegalConsequence values"
        )

    return EurLexLegalConsequences(
        consequences=tuple(
            dict.fromkeys(consequences)
        )
    )
