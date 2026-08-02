"""Parse explicit Boolean logic from rule qualifier text."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from eke.application.eurlex.boolean_expressions import (
    EurLexBooleanAtom,
    EurLexBooleanExpressionTree,
    EurLexBooleanOperation,
    EurLexBooleanOperator,
    EurLexStructuredRuleQualifier,
    EurLexStructuredRuleQualifiers,
)
from eke.application.eurlex.rule_qualifiers import (
    EurLexRuleQualifier,
    EurLexRuleQualifiers,
)


class EurLexBooleanExpressionParseError(
    ValueError
):
    """Raised when explicit Boolean syntax is invalid."""


class _TokenKind(StrEnum):
    ATOM = "ATOM"
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"


@dataclass(frozen=True, slots=True)
class _Token:
    kind: _TokenKind
    value: str
    position: int


@dataclass(frozen=True, slots=True)
class _ParsedNode:
    expression_id: str
    source_text: str
    position: int


_BOUNDARY_PATTERN = re.compile(
    r"\s+\b(and|or)\b\s+|[()]",
    re.IGNORECASE,
)


class EurLexBooleanExpressionParser:
    """Parse qualifier text using NOT > AND > OR precedence."""

    def parse(
        self,
        qualifier: EurLexRuleQualifier,
    ) -> EurLexBooleanExpressionTree:
        """Parse one qualifier into a closed Boolean tree."""
        if not isinstance(
            qualifier,
            EurLexRuleQualifier,
        ):
            raise TypeError(
                "qualifier must be an "
                "EurLexRuleQualifier"
            )

        parser = _RecursiveParser(
            qualifier_id=qualifier.qualifier_id,
            tokens=_tokenize(qualifier.text),
        )
        root = parser.parse()

        return EurLexBooleanExpressionTree(
            qualifier_id=qualifier.qualifier_id,
            root_expression_id=root.expression_id,
            atoms=tuple(parser.atoms),
            operations=tuple(parser.operations),
        )

    def parse_all(
        self,
        qualifiers: EurLexRuleQualifiers,
    ) -> EurLexStructuredRuleQualifiers:
        """Parse all qualifiers in source order."""
        if not isinstance(
            qualifiers,
            EurLexRuleQualifiers,
        ):
            raise TypeError(
                "qualifiers must be an "
                "EurLexRuleQualifiers"
            )

        return EurLexStructuredRuleQualifiers(
            qualifiers=tuple(
                EurLexStructuredRuleQualifier(
                    qualifier_id=(
                        qualifier.qualifier_id
                    ),
                    expression_tree=self.parse(
                        qualifier
                    ),
                )
                for qualifier
                in qualifiers.qualifiers
            )
        )


class _RecursiveParser:
    def __init__(
        self,
        *,
        qualifier_id: str,
        tokens: tuple[_Token, ...],
    ) -> None:
        self.qualifier_id = qualifier_id
        self.tokens = tokens
        self.index = 0
        self.atoms: list[EurLexBooleanAtom] = []
        self.operations: list[
            EurLexBooleanOperation
        ] = []

    def parse(self) -> _ParsedNode:
        if not self.tokens:
            raise EurLexBooleanExpressionParseError(
                "Boolean expression must not be empty"
            )

        node = self._parse_or()
        if self._current() is not None:
            raise EurLexBooleanExpressionParseError(
                "unexpected token in Boolean expression"
            )
        return node

    def _parse_or(self) -> _ParsedNode:
        operands = [self._parse_and()]
        while self._matches(_TokenKind.OR):
            self._advance()
            operands.append(self._parse_and())
        return self._combine(
            EurLexBooleanOperator.OR,
            operands,
        )

    def _parse_and(self) -> _ParsedNode:
        operands = [self._parse_not()]
        while self._matches(_TokenKind.AND):
            self._advance()
            operands.append(self._parse_not())
        return self._combine(
            EurLexBooleanOperator.AND,
            operands,
        )

    def _parse_not(self) -> _ParsedNode:
        if self._matches(_TokenKind.NOT):
            token = self._advance()
            operand = self._parse_not()
            return self._create_operation(
                operator=EurLexBooleanOperator.NOT,
                operands=(operand,),
                source_text=(
                    f"not {operand.source_text}"
                ),
                position=token.position,
            )
        return self._parse_primary()

    def _parse_primary(self) -> _ParsedNode:
        token = self._current()
        if token is None:
            raise EurLexBooleanExpressionParseError(
                "missing Boolean operand"
            )

        if token.kind is _TokenKind.LPAREN:
            opening = self._advance()
            node = self._parse_or()
            if not self._matches(
                _TokenKind.RPAREN
            ):
                raise EurLexBooleanExpressionParseError(
                    "unbalanced parentheses"
                )
            self._advance()
            return _ParsedNode(
                expression_id=node.expression_id,
                source_text=f"({node.source_text})",
                position=opening.position,
            )

        if token.kind is _TokenKind.RPAREN:
            raise EurLexBooleanExpressionParseError(
                "unexpected closing parenthesis"
            )

        if token.kind is not _TokenKind.ATOM:
            raise EurLexBooleanExpressionParseError(
                "missing Boolean operand"
            )

        atom_token = self._advance()
        expression_id = _stable_id(
            "boolean-atom",
            self.qualifier_id,
            str(atom_token.position),
            atom_token.value,
        )
        self.atoms.append(
            EurLexBooleanAtom(
                expression_id=expression_id,
                text=atom_token.value,
                source_text=atom_token.value,
            )
        )
        return _ParsedNode(
            expression_id=expression_id,
            source_text=atom_token.value,
            position=atom_token.position,
        )

    def _combine(
        self,
        operator: EurLexBooleanOperator,
        operands: list[_ParsedNode],
    ) -> _ParsedNode:
        if len(operands) == 1:
            return operands[0]

        source_text = (
            f" {operator.value.casefold()} "
        ).join(
            operand.source_text
            for operand in operands
        )
        return self._create_operation(
            operator=operator,
            operands=tuple(operands),
            source_text=source_text,
            position=operands[0].position,
        )

    def _create_operation(
        self,
        *,
        operator: EurLexBooleanOperator,
        operands: tuple[_ParsedNode, ...],
        source_text: str,
        position: int,
    ) -> _ParsedNode:
        expression_id = _stable_id(
            "boolean-operation",
            self.qualifier_id,
            operator.value,
            str(position),
            source_text,
        )
        self.operations.append(
            EurLexBooleanOperation(
                expression_id=expression_id,
                operator=operator,
                operand_ids=tuple(
                    operand.expression_id
                    for operand in operands
                ),
                source_text=source_text,
            )
        )
        return _ParsedNode(
            expression_id=expression_id,
            source_text=source_text,
            position=position,
        )

    def _current(self) -> _Token | None:
        if self.index >= len(self.tokens):
            return None
        return self.tokens[self.index]

    def _matches(
        self,
        kind: _TokenKind,
    ) -> bool:
        token = self._current()
        return (
            token is not None
            and token.kind is kind
        )

    def _advance(self) -> _Token:
        token = self._current()
        if token is None:
            raise EurLexBooleanExpressionParseError(
                "unexpected end of Boolean expression"
            )
        self.index += 1
        return token


def _tokenize(text: str) -> tuple[_Token, ...]:
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    normalized = " ".join(text.split())
    if not normalized:
        raise EurLexBooleanExpressionParseError(
            "Boolean expression must not be empty"
        )

    raw_tokens: list[_Token] = []
    cursor = 0

    for match in _BOUNDARY_PATTERN.finditer(
        normalized
    ):
        _append_atom_tokens(
            raw_tokens,
            normalized[cursor:match.start()],
            cursor,
        )

        boundary = match.group(0)
        operator = match.group(1)
        if boundary == "(":
            raw_tokens.append(
                _Token(
                    _TokenKind.LPAREN,
                    boundary,
                    match.start(),
                )
            )
        elif boundary == ")":
            raw_tokens.append(
                _Token(
                    _TokenKind.RPAREN,
                    boundary,
                    match.start(),
                )
            )
        elif operator is not None:
            raw_tokens.append(
                _Token(
                    (
                        _TokenKind.AND
                        if operator.casefold()
                        == "and"
                        else _TokenKind.OR
                    ),
                    operator.casefold(),
                    match.start(),
                )
            )

        cursor = match.end()

    _append_atom_tokens(
        raw_tokens,
        normalized[cursor:],
        cursor,
    )

    return tuple(raw_tokens)


def _append_atom_tokens(
    tokens: list[_Token],
    raw_text: str,
    position: int,
) -> None:
    text = " ".join(raw_text.split())
    if not text:
        return

    if text.casefold() == "not":
        tokens.append(
            _Token(
                _TokenKind.NOT,
                "not",
                position,
            )
        )
        return

    if text.casefold().startswith("not "):
        tokens.append(
            _Token(
                _TokenKind.NOT,
                "not",
                position,
            )
        )
        atom = text[4:].strip()
        if not atom:
            raise EurLexBooleanExpressionParseError(
                "missing Boolean operand"
            )
        tokens.append(
            _Token(
                _TokenKind.ATOM,
                atom,
                position + 4,
            )
        )
        return

    tokens.append(
        _Token(
            _TokenKind.ATOM,
            text,
            position,
        )
    )


def _stable_id(
    prefix: str,
    *parts: str,
) -> str:
    digest = sha256(
        "\x1f".join(parts).encode("utf-8")
    ).hexdigest()[:16]
    return f"{prefix}-{digest}"
