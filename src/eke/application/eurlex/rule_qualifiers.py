"""Source-backed conditions and exceptions for compliance rules."""

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


class EurLexRuleQualifierKind(StrEnum):
    """Canonical qualifier kinds."""

    CONDITION = "CONDITION"
    EXCEPTION = "EXCEPTION"


class EurLexRuleQualifierMarker(StrEnum):
    """Canonical explicit qualifier markers."""

    IF = "IF"
    WHERE = "WHERE"
    WHEN = "WHEN"
    PROVIDED_THAT = "PROVIDED_THAT"
    SUBJECT_TO = "SUBJECT_TO"
    UNLESS = "UNLESS"
    EXCEPT_WHERE = "EXCEPT_WHERE"
    EXCEPT_IF = "EXCEPT_IF"
    SAVE_WHERE = "SAVE_WHERE"


@dataclass(frozen=True, slots=True)
class EurLexRuleQualifier:
    """Represent one explicit rule condition or exception."""

    qualifier_id: str
    kind: EurLexRuleQualifierKind
    marker: EurLexRuleQualifierMarker
    text: str
    source_rule_id: str
    source_requirement_id: str
    source_node_id: str
    source_text: str
    referenced_node_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in (
            "qualifier_id",
            "text",
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

        object.__setattr__(
            self,
            "referenced_node_ids",
            _normalize_identifier_tuple(
                self.referenced_node_ids,
                name="referenced_node_ids",
            ),
        )

        if not isinstance(
            self.kind,
            EurLexRuleQualifierKind,
        ):
            raise TypeError(
                "kind must be an "
                "EurLexRuleQualifierKind"
            )

        if not isinstance(
            self.marker,
            EurLexRuleQualifierMarker,
        ):
            raise TypeError(
                "marker must be an "
                "EurLexRuleQualifierMarker"
            )


@dataclass(frozen=True, slots=True)
class EurLexRuleQualifiers:
    """Contain explicit rule qualifiers."""

    qualifiers: tuple[
        EurLexRuleQualifier,
        ...,
    ] = ()

    def __post_init__(self) -> None:
        if not isinstance(
            self.qualifiers,
            tuple,
        ):
            raise TypeError(
                "qualifiers must be a tuple"
            )

        if any(
            not isinstance(
                qualifier,
                EurLexRuleQualifier,
            )
            for qualifier in self.qualifiers
        ):
            raise TypeError(
                "qualifiers must contain "
                "EurLexRuleQualifier values"
            )

        qualifier_ids = tuple(
            qualifier.qualifier_id
            for qualifier in self.qualifiers
        )
        if len(qualifier_ids) != len(
            set(qualifier_ids)
        ):
            raise ValueError(
                "qualifier identifiers must be unique"
            )

    def qualifier_by_id(
        self,
        qualifier_id: str,
    ) -> EurLexRuleQualifier | None:
        """Return one qualifier by identifier."""
        normalized = _normalize_required_text(
            qualifier_id,
            name="qualifier_id",
        )

        return next(
            (
                qualifier
                for qualifier in self.qualifiers
                if qualifier.qualifier_id
                == normalized
            ),
            None,
        )

    def qualifiers_for_rule(
        self,
        source_rule_id: str,
    ) -> tuple[EurLexRuleQualifier, ...]:
        """Return qualifiers attached to one rule."""
        normalized = _normalize_required_text(
            source_rule_id,
            name="source_rule_id",
        )

        return tuple(
            qualifier
            for qualifier in self.qualifiers
            if qualifier.source_rule_id
            == normalized
        )

    def qualifiers_by_kind(
        self,
        kind: EurLexRuleQualifierKind,
    ) -> tuple[EurLexRuleQualifier, ...]:
        """Return qualifiers of one kind."""
        if not isinstance(
            kind,
            EurLexRuleQualifierKind,
        ):
            raise TypeError(
                "kind must be an "
                "EurLexRuleQualifierKind"
            )

        return tuple(
            qualifier
            for qualifier in self.qualifiers
            if qualifier.kind is kind
        )

    def conditions_for_rule(
        self,
        source_rule_id: str,
    ) -> tuple[EurLexRuleQualifier, ...]:
        """Return conditions attached to one rule."""
        return tuple(
            qualifier
            for qualifier
            in self.qualifiers_for_rule(
                source_rule_id
            )
            if qualifier.kind
            is EurLexRuleQualifierKind.CONDITION
        )

    def exceptions_for_rule(
        self,
        source_rule_id: str,
    ) -> tuple[EurLexRuleQualifier, ...]:
        """Return exceptions attached to one rule."""
        return tuple(
            qualifier
            for qualifier
            in self.qualifiers_for_rule(
                source_rule_id
            )
            if qualifier.kind
            is EurLexRuleQualifierKind.EXCEPTION
        )
