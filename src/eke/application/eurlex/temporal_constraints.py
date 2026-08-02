"""Explicit temporal constraints derived from EUR-Lex compliance rules."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum


def _normalize_required_text(
    value: str,
    *,
    name: str,
) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")

    normalized = " ".join(value.split())
    if not normalized:
        raise ValueError(f"{name} must not be empty")

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


class EurLexTemporalConstraintKind(StrEnum):
    """Canonical kinds of explicit temporal constraints."""

    DEADLINE = "DEADLINE"
    START = "START"
    END = "END"
    DURATION = "DURATION"
    FREQUENCY = "FREQUENCY"
    RELATIVE_OFFSET = "RELATIVE_OFFSET"


class EurLexTemporalRelation(StrEnum):
    """Canonical temporal relations."""

    BEFORE = "BEFORE"
    AFTER = "AFTER"
    WITHIN = "WITHIN"
    FROM = "FROM"
    UNTIL = "UNTIL"
    NO_LATER_THAN = "NO_LATER_THAN"
    NO_EARLIER_THAN = "NO_EARLIER_THAN"
    FOR = "FOR"
    EVERY = "EVERY"
    ANNUALLY = "ANNUALLY"
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"


class EurLexTemporalUnit(StrEnum):
    """Canonical temporal quantity units."""

    DAY = "DAY"
    WEEK = "WEEK"
    MONTH = "MONTH"
    YEAR = "YEAR"


@dataclass(frozen=True, slots=True)
class EurLexTemporalConstraint:
    """Represent one explicit source-backed temporal constraint."""

    constraint_id: str
    kind: EurLexTemporalConstraintKind
    relation: EurLexTemporalRelation
    text: str
    source_rule_id: str
    source_requirement_id: str
    source_node_id: str
    source_text: str
    absolute_date: date | None = None
    quantity: int | None = None
    unit: EurLexTemporalUnit | None = None
    anchor_text: str | None = None
    source_qualifier_id: str | None = None

    def __post_init__(self) -> None:
        for name in (
            "constraint_id",
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

        for name in (
            "anchor_text",
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

        if not isinstance(
            self.kind,
            EurLexTemporalConstraintKind,
        ):
            raise TypeError(
                "kind must be an "
                "EurLexTemporalConstraintKind"
            )

        if not isinstance(
            self.relation,
            EurLexTemporalRelation,
        ):
            raise TypeError(
                "relation must be an "
                "EurLexTemporalRelation"
            )

        if (
            self.absolute_date is not None
            and not isinstance(
                self.absolute_date,
                date,
            )
        ):
            raise TypeError(
                "absolute_date must be a date or None"
            )

        if self.quantity is not None:
            if (
                not isinstance(self.quantity, int)
                or isinstance(self.quantity, bool)
            ):
                raise TypeError(
                    "quantity must be an integer or None"
                )
            if self.quantity <= 0:
                raise ValueError(
                    "quantity must be strictly positive"
                )

        if (
            self.unit is not None
            and not isinstance(
                self.unit,
                EurLexTemporalUnit,
            )
        ):
            raise TypeError(
                "unit must be an "
                "EurLexTemporalUnit or None"
            )

        if (
            self.quantity is None
            and self.unit is not None
        ):
            raise ValueError(
                "unit requires quantity"
            )

        if (
            self.quantity is not None
            and self.unit is None
        ):
            raise ValueError(
                "quantity requires unit"
            )

        if (
            self.absolute_date is not None
            and self.quantity is not None
        ):
            raise ValueError(
                "absolute_date and quantity are "
                "mutually exclusive"
            )

        if (
            self.kind
            is EurLexTemporalConstraintKind.FREQUENCY
            and self.relation
            not in {
                EurLexTemporalRelation.EVERY,
                EurLexTemporalRelation.ANNUALLY,
                EurLexTemporalRelation.MONTHLY,
                EurLexTemporalRelation.QUARTERLY,
            }
        ):
            raise ValueError(
                "frequency constraints require a "
                "frequency relation"
            )

        if (
            self.relation
            in {
                EurLexTemporalRelation.ANNUALLY,
                EurLexTemporalRelation.MONTHLY,
                EurLexTemporalRelation.QUARTERLY,
            }
            and (
                self.quantity is not None
                or self.unit is not None
                or self.absolute_date is not None
            )
        ):
            raise ValueError(
                "lexical frequencies must not define "
                "quantity, unit or absolute_date"
            )

        if (
            self.relation
            is EurLexTemporalRelation.EVERY
            and (
                self.quantity is None
                or self.unit is None
            )
        ):
            raise ValueError(
                "EVERY requires quantity and unit"
            )

        if (
            self.kind
            is EurLexTemporalConstraintKind.DURATION
            and self.relation
            is not EurLexTemporalRelation.FOR
        ):
            raise ValueError(
                "duration constraints require FOR"
            )


@dataclass(frozen=True, slots=True)
class EurLexTemporalConstraints:
    """Contain explicit temporal constraints."""

    constraints: tuple[
        EurLexTemporalConstraint,
        ...,
    ] = ()

    def __post_init__(self) -> None:
        if not isinstance(
            self.constraints,
            tuple,
        ):
            raise TypeError(
                "constraints must be a tuple"
            )

        if any(
            not isinstance(
                constraint,
                EurLexTemporalConstraint,
            )
            for constraint in self.constraints
        ):
            raise TypeError(
                "constraints must contain "
                "EurLexTemporalConstraint values"
            )

        constraint_ids = tuple(
            constraint.constraint_id
            for constraint in self.constraints
        )
        if len(constraint_ids) != len(
            set(constraint_ids)
        ):
            raise ValueError(
                "constraint identifiers must be unique"
            )

    def constraint_by_id(
        self,
        constraint_id: str,
    ) -> EurLexTemporalConstraint | None:
        """Return one temporal constraint by identifier."""
        normalized = _normalize_required_text(
            constraint_id,
            name="constraint_id",
        )

        return next(
            (
                constraint
                for constraint in self.constraints
                if constraint.constraint_id
                == normalized
            ),
            None,
        )

    def constraints_for_rule(
        self,
        source_rule_id: str,
    ) -> tuple[EurLexTemporalConstraint, ...]:
        """Return constraints attached to one rule."""
        normalized = _normalize_required_text(
            source_rule_id,
            name="source_rule_id",
        )

        return tuple(
            constraint
            for constraint in self.constraints
            if constraint.source_rule_id
            == normalized
        )

    def constraints_for_qualifier(
        self,
        source_qualifier_id: str,
    ) -> tuple[EurLexTemporalConstraint, ...]:
        """Return constraints attached to one qualifier."""
        normalized = _normalize_required_text(
            source_qualifier_id,
            name="source_qualifier_id",
        )

        return tuple(
            constraint
            for constraint in self.constraints
            if constraint.source_qualifier_id
            == normalized
        )

    def constraints_by_kind(
        self,
        kind: EurLexTemporalConstraintKind,
    ) -> tuple[EurLexTemporalConstraint, ...]:
        """Return constraints of one kind."""
        if not isinstance(
            kind,
            EurLexTemporalConstraintKind,
        ):
            raise TypeError(
                "kind must be an "
                "EurLexTemporalConstraintKind"
            )

        return tuple(
            constraint
            for constraint in self.constraints
            if constraint.kind is kind
        )

    def deadlines(
        self,
    ) -> tuple[EurLexTemporalConstraint, ...]:
        """Return explicit deadlines."""
        return self.constraints_by_kind(
            EurLexTemporalConstraintKind.DEADLINE
        )


def normalize_temporal_constraints(
    constraints: tuple[
        EurLexTemporalConstraint,
        ...,
    ],
) -> EurLexTemporalConstraints:
    """Deduplicate constraints while preserving source order."""
    if not isinstance(constraints, tuple):
        raise TypeError(
            "constraints must be a tuple"
        )

    if any(
        not isinstance(
            constraint,
            EurLexTemporalConstraint,
        )
        for constraint in constraints
    ):
        raise TypeError(
            "constraints must contain "
            "EurLexTemporalConstraint values"
        )

    return EurLexTemporalConstraints(
        constraints=tuple(
            dict.fromkeys(constraints)
        )
    )
