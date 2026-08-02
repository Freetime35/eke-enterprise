"""Extract explicit English legal definitions from document structure."""

from __future__ import annotations

import re

from eke.application.eurlex.document_structure import (
    EurLexDocumentNode,
    EurLexDocumentNodeKind,
    EurLexDocumentStructure,
)
from eke.application.eurlex.legal_definitions import (
    EurLexLegalDefinition,
    EurLexLegalDefinitions,
    normalize_legal_definitions,
)
from eke.domain.localization import LanguageCode

_DEFINITION_PATTERN = re.compile(
    r"""
    ^\s*
    (?:
        [“"'](?P<quoted_term>[^”"']+)[”"']
        |
        (?P<plain_term>
            [A-Za-z][A-Za-z0-9 /(),.'\-]{1,120}?
        )
    )
    \s+
    (?:
        means
        |
        shall\s+mean
        |
        is\s+to\s+be\s+understood\s+as
        |
        has\s+the\s+meaning
    )
    \s+
    (?P<definition>.+?)
    \s*$
    """,
    re.IGNORECASE | re.VERBOSE,
)

_ALLOWED_NODE_KINDS = frozenset(
    {
        EurLexDocumentNodeKind.PARAGRAPH,
        EurLexDocumentNodeKind.SUBPARAGRAPH,
        EurLexDocumentNodeKind.POINT,
        EurLexDocumentNodeKind.INDENT,
    }
)


class EurLexLegalDefinitionParseError(
    ValueError
):
    """Raised when legal-definition extraction input is invalid."""


class EurLexLegalDefinitionParser:
    """Extract only explicit English legal definitions."""

    def parse(
        self,
        structure: EurLexDocumentStructure,
        *,
        language: LanguageCode,
    ) -> EurLexLegalDefinitions:
        """Extract definitions from structured English content."""
        if not isinstance(
            structure,
            EurLexDocumentStructure,
        ):
            raise TypeError(
                "structure must be an "
                "EurLexDocumentStructure"
            )

        if not isinstance(
            language,
            LanguageCode,
        ):
            raise TypeError(
                "language must be a LanguageCode"
            )

        if language != LanguageCode("en"):
            return EurLexLegalDefinitions()

        definitions: list[
            EurLexLegalDefinition
        ] = []

        for node in structure.nodes:
            if node.kind not in _ALLOWED_NODE_KINDS:
                continue
            if node.text is None:
                continue

            match = _DEFINITION_PATTERN.fullmatch(
                node.text
            )
            if match is None:
                continue

            term = (
                match.group("quoted_term")
                or match.group("plain_term")
            )
            if term is None:
                continue

            article_node_id = (
                _nearest_ancestor_id(
                    structure,
                    node,
                    EurLexDocumentNodeKind.ARTICLE,
                )
            )
            paragraph_node_id = (
                _nearest_ancestor_id(
                    structure,
                    node,
                    EurLexDocumentNodeKind.PARAGRAPH,
                )
            )

            definitions.append(
                EurLexLegalDefinition(
                    term=term,
                    definition=match.group(
                        "definition"
                    ),
                    source_node_id=node.node_id,
                    source_text=node.text,
                    language=language,
                    article_node_id=(
                        article_node_id
                    ),
                    paragraph_node_id=(
                        paragraph_node_id
                    ),
                )
            )

        return normalize_legal_definitions(
            tuple(definitions)
        )


def _nearest_ancestor_id(
    structure: EurLexDocumentStructure,
    node: EurLexDocumentNode,
    kind: EurLexDocumentNodeKind,
) -> str | None:
    current = node

    if current.kind is kind:
        return current.node_id

    while current.parent_id is not None:
        parent = structure.node_by_id(
            current.parent_id
        )
        if parent is None:
            return None
        if parent.kind is kind:
            return parent.node_id
        current = parent

    return None
