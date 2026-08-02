"""Deterministic compliance rules derived from requirements graphs."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from eke.domain.localization import LanguageCode


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


class EurLexComplianceRuleKind(StrEnum):
    """Canonical compliance-rule kinds."""

    REQUIREMENT = "REQUIREMENT"
    PERMISSION = "PERMISSION"
    PROHIBITION = "PROHIBITION"


@dataclass(frozen=True, slots=True)
class EurLexComplianceRule:
    """Represent one rule derived from one graph requirement."""

    rule_id: str
    kind: EurLexComplianceRuleKind
    subject: str
    action: str
    source_requirement_id: str
    source_node_id: str
    source_text: str
    language: LanguageCode
    article_node_id: str | None = None
    paragraph_node_id: str | None = None
    referenced_node_ids: tuple[str, ...] = ()
    definition_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in (
            "rule_id",
            "subject",
            "action",
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
            "article_node_id",
            "paragraph_node_id",
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
            "referenced_node_ids",
            _normalize_identifier_tuple(
                self.referenced_node_ids,
                name="referenced_node_ids",
            ),
        )
        object.__setattr__(
            self,
            "definition_ids",
            _normalize_identifier_tuple(
                self.definition_ids,
                name="definition_ids",
            ),
        )

        if not isinstance(
            self.kind,
            EurLexComplianceRuleKind,
        ):
            raise TypeError(
                "kind must be an "
                "EurLexComplianceRuleKind"
            )

        if not isinstance(
            self.language,
            LanguageCode,
        ):
            raise TypeError(
                "language must be a LanguageCode"
            )

    @property
    def normalized_subject(self) -> str:
        """Return a case-insensitive subject key."""
        return self.subject.casefold()


@dataclass(frozen=True, slots=True)
class EurLexComplianceRules:
    """Contain compliance rules derived from one graph."""

    rules: tuple[
        EurLexComplianceRule,
        ...,
    ] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.rules, tuple):
            raise TypeError(
                "rules must be a tuple"
            )

        if any(
            not isinstance(
                rule,
                EurLexComplianceRule,
            )
            for rule in self.rules
        ):
            raise TypeError(
                "rules must contain "
                "EurLexComplianceRule values"
            )

        rule_ids = tuple(
            rule.rule_id
            for rule in self.rules
        )
        if len(rule_ids) != len(
            set(rule_ids)
        ):
            raise ValueError(
                "rule identifiers must be unique"
            )

        source_requirement_ids = tuple(
            rule.source_requirement_id
            for rule in self.rules
        )
        if len(source_requirement_ids) != len(
            set(source_requirement_ids)
        ):
            raise ValueError(
                "each source requirement must "
                "produce at most one rule"
            )

    def rule_by_id(
        self,
        rule_id: str,
    ) -> EurLexComplianceRule | None:
        """Return one rule by identifier."""
        normalized = _normalize_required_text(
            rule_id,
            name="rule_id",
        )

        return next(
            (
                rule
                for rule in self.rules
                if rule.rule_id == normalized
            ),
            None,
        )

    def rules_for_subject(
        self,
        subject: str,
    ) -> tuple[EurLexComplianceRule, ...]:
        """Return rules for one exact normalized subject."""
        normalized = _normalize_required_text(
            subject,
            name="subject",
        ).casefold()

        return tuple(
            rule
            for rule in self.rules
            if rule.normalized_subject
            == normalized
        )

    def rules_for_article(
        self,
        article_node_id: str,
    ) -> tuple[EurLexComplianceRule, ...]:
        """Return rules attached to one article."""
        normalized = _normalize_required_text(
            article_node_id,
            name="article_node_id",
        )

        return tuple(
            rule
            for rule in self.rules
            if rule.article_node_id
            == normalized
        )

    def rules_by_kind(
        self,
        kind: EurLexComplianceRuleKind,
    ) -> tuple[EurLexComplianceRule, ...]:
        """Return rules of one kind."""
        if not isinstance(
            kind,
            EurLexComplianceRuleKind,
        ):
            raise TypeError(
                "kind must be an "
                "EurLexComplianceRuleKind"
            )

        return tuple(
            rule
            for rule in self.rules
            if rule.kind is kind
        )
