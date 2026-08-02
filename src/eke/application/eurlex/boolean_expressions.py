"""Structured Boolean expressions derived from explicit rule qualifiers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


def _required_text(value: str, *, name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    normalized = " ".join(value.split())
    if not normalized:
        raise ValueError(f"{name} must not be empty")
    return normalized


def _identifier_tuple(
    values: tuple[str, ...],
    *,
    name: str,
) -> tuple[str, ...]:
    if not isinstance(values, tuple):
        raise TypeError(f"{name} must be a tuple")
    return tuple(
        _required_text(value, name=name)
        for value in values
    )


class EurLexBooleanOperator(StrEnum):
    """Canonical Boolean operators."""

    AND = "AND"
    OR = "OR"
    NOT = "NOT"


@dataclass(frozen=True, slots=True)
class EurLexBooleanAtom:
    """Represent one source-backed Boolean atom."""

    expression_id: str
    text: str
    source_text: str

    def __post_init__(self) -> None:
        for name in (
            "expression_id",
            "text",
            "source_text",
        ):
            object.__setattr__(
                self,
                name,
                _required_text(
                    getattr(self, name),
                    name=name,
                ),
            )


@dataclass(frozen=True, slots=True)
class EurLexBooleanOperation:
    """Represent one Boolean operation node."""

    expression_id: str
    operator: EurLexBooleanOperator
    operand_ids: tuple[str, ...]
    source_text: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "expression_id",
            _required_text(
                self.expression_id,
                name="expression_id",
            ),
        )
        object.__setattr__(
            self,
            "source_text",
            _required_text(
                self.source_text,
                name="source_text",
            ),
        )
        object.__setattr__(
            self,
            "operand_ids",
            _identifier_tuple(
                self.operand_ids,
                name="operand_ids",
            ),
        )

        if not isinstance(
            self.operator,
            EurLexBooleanOperator,
        ):
            raise TypeError(
                "operator must be an "
                "EurLexBooleanOperator"
            )

        if (
            self.operator
            is EurLexBooleanOperator.NOT
            and len(self.operand_ids) != 1
        ):
            raise ValueError(
                "NOT must have exactly one operand"
            )

        if (
            self.operator
            in {
                EurLexBooleanOperator.AND,
                EurLexBooleanOperator.OR,
            }
            and len(self.operand_ids) < 2
        ):
            raise ValueError(
                "AND and OR must have at least "
                "two operands"
            )


@dataclass(frozen=True, slots=True)
class EurLexBooleanExpressionTree:
    """Contain one closed acyclic Boolean expression tree."""

    qualifier_id: str
    root_expression_id: str
    atoms: tuple[EurLexBooleanAtom, ...] = ()
    operations: tuple[
        EurLexBooleanOperation,
        ...,
    ] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "qualifier_id",
            _required_text(
                self.qualifier_id,
                name="qualifier_id",
            ),
        )
        object.__setattr__(
            self,
            "root_expression_id",
            _required_text(
                self.root_expression_id,
                name="root_expression_id",
            ),
        )

        if not isinstance(self.atoms, tuple):
            raise TypeError("atoms must be a tuple")
        if not isinstance(self.operations, tuple):
            raise TypeError(
                "operations must be a tuple"
            )
        if any(
            not isinstance(atom, EurLexBooleanAtom)
            for atom in self.atoms
        ):
            raise TypeError(
                "atoms must contain "
                "EurLexBooleanAtom values"
            )
        if any(
            not isinstance(
                operation,
                EurLexBooleanOperation,
            )
            for operation in self.operations
        ):
            raise TypeError(
                "operations must contain "
                "EurLexBooleanOperation values"
            )

        expression_ids = tuple(
            atom.expression_id for atom in self.atoms
        ) + tuple(
            operation.expression_id
            for operation in self.operations
        )
        if len(expression_ids) != len(
            set(expression_ids)
        ):
            raise ValueError(
                "expression identifiers must be unique"
            )

        known_ids = set(expression_ids)
        if self.root_expression_id not in known_ids:
            raise ValueError(
                "root expression must exist"
            )

        for operation in self.operations:
            if any(
                operand_id not in known_ids
                for operand_id
                in operation.operand_ids
            ):
                raise ValueError(
                    "operation operands must exist"
                )

        _assert_acyclic(
            root_expression_id=(
                self.root_expression_id
            ),
            operations=self.operations,
        )

    def atom_by_id(
        self,
        expression_id: str,
    ) -> EurLexBooleanAtom | None:
        """Return one atom by identifier."""
        normalized = _required_text(
            expression_id,
            name="expression_id",
        )
        return next(
            (
                atom
                for atom in self.atoms
                if atom.expression_id == normalized
            ),
            None,
        )

    def operation_by_id(
        self,
        expression_id: str,
    ) -> EurLexBooleanOperation | None:
        """Return one operation by identifier."""
        normalized = _required_text(
            expression_id,
            name="expression_id",
        )
        return next(
            (
                operation
                for operation in self.operations
                if operation.expression_id
                == normalized
            ),
            None,
        )


@dataclass(frozen=True, slots=True)
class EurLexStructuredRuleQualifier:
    """Link one qualifier to its Boolean tree."""

    qualifier_id: str
    expression_tree: EurLexBooleanExpressionTree

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "qualifier_id",
            _required_text(
                self.qualifier_id,
                name="qualifier_id",
            ),
        )
        if not isinstance(
            self.expression_tree,
            EurLexBooleanExpressionTree,
        ):
            raise TypeError(
                "expression_tree must be an "
                "EurLexBooleanExpressionTree"
            )
        if (
            self.qualifier_id
            != self.expression_tree.qualifier_id
        ):
            raise ValueError(
                "qualifier identifiers must match"
            )


@dataclass(frozen=True, slots=True)
class EurLexStructuredRuleQualifiers:
    """Contain structured Boolean qualifier expressions."""

    qualifiers: tuple[
        EurLexStructuredRuleQualifier,
        ...,
    ] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.qualifiers, tuple):
            raise TypeError(
                "qualifiers must be a tuple"
            )
        if any(
            not isinstance(
                qualifier,
                EurLexStructuredRuleQualifier,
            )
            for qualifier in self.qualifiers
        ):
            raise TypeError(
                "qualifiers must contain "
                "EurLexStructuredRuleQualifier values"
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

    def expression_for_qualifier(
        self,
        qualifier_id: str,
    ) -> EurLexBooleanExpressionTree | None:
        """Return the Boolean tree for one qualifier."""
        normalized = _required_text(
            qualifier_id,
            name="qualifier_id",
        )
        return next(
            (
                qualifier.expression_tree
                for qualifier in self.qualifiers
                if qualifier.qualifier_id
                == normalized
            ),
            None,
        )


def _assert_acyclic(
    *,
    root_expression_id: str,
    operations: tuple[
        EurLexBooleanOperation,
        ...,
    ],
) -> None:
    operands_by_id = {
        operation.expression_id: (
            operation.operand_ids
        )
        for operation in operations
    }
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(expression_id: str) -> None:
        if expression_id in visiting:
            raise ValueError(
                "Boolean expression tree "
                "must be acyclic"
            )
        if expression_id in visited:
            return

        visiting.add(expression_id)
        for operand_id in operands_by_id.get(
            expression_id,
            (),
        ):
            visit(operand_id)
        visiting.remove(expression_id)
        visited.add(expression_id)

    visit(root_expression_id)
