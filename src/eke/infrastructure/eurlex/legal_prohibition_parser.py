"""Extract explicit English legal prohibitions from document structure."""

from __future__ import annotations

import re

from eke.application.eurlex.document_structure import (
    EurLexDocumentNode,
    EurLexDocumentNodeKind,
    EurLexDocumentStructure,
)
from eke.application.eurlex.legal_prohibitions import (
    EurLexLegalProhibition,
    EurLexLegalProhibitionKind,
    EurLexLegalProhibitions,
    normalize_legal_prohibitions,
)
from eke.domain.localization import LanguageCode

_PROHIBITION_PATTERNS: tuple[
    tuple[
        EurLexLegalProhibitionKind,
        re.Pattern[str],
    ],
    ...,
] = (
    (
        EurLexLegalProhibitionKind.PROHIBITED_FROM,
        re.compile(
            r"""
            ^\s*
            (?P<subject>.+?)
            \s+
            (?:is|are)\s+prohibited\s+from
            \s+
            (?P<action>.+?)
            \s*$
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
    (
        EurLexLegalProhibitionKind.NOT_AUTHORISED_TO,
        re.compile(
            r"""
            ^\s*
            (?P<subject>.+?)
            \s+
            (?:is|are)\s+not\s+authorised\s+to
            \s+
            (?P<action>.+?)
            \s*$
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
    (
        EurLexLegalProhibitionKind.NOT_ALLOWED_TO,
        re.compile(
            r"""
            ^\s*
            (?P<subject>.+?)
            \s+
            (?:is|are)\s+not\s+allowed\s+to
            \s+
            (?P<action>.+?)
            \s*$
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
    (
        EurLexLegalProhibitionKind.SHALL_NOT,
        re.compile(
            r"""
            ^\s*
            (?P<subject>.+?)
            \s+shall\s+not\s+
            (?P<action>.+?)
            \s*$
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
    (
        EurLexLegalProhibitionKind.MUST_NOT,
        re.compile(
            r"""
            ^\s*
            (?P<subject>.+?)
            \s+must\s+not\s+
            (?P<action>.+?)
            \s*$
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
    (
        EurLexLegalProhibitionKind.MAY_NOT,
        re.compile(
            r"""
            ^\s*
            (?P<subject>.+?)
            \s+may\s+not\s+
            (?P<action>.+?)
            \s*$
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
)

_ALLOWED_NODE_KINDS = frozenset(
    {
        EurLexDocumentNodeKind.PARAGRAPH,
        EurLexDocumentNodeKind.SUBPARAGRAPH,
        EurLexDocumentNodeKind.POINT,
        EurLexDocumentNodeKind.INDENT,
    }
)


class EurLexLegalProhibitionParseError(
    ValueError
):
    """Raised when legal-prohibition extraction input is invalid."""


class EurLexLegalProhibitionParser:
    """Extract only explicit English prohibitions."""

    def parse(
        self,
        structure: EurLexDocumentStructure,
        *,
        language: LanguageCode,
    ) -> EurLexLegalProhibitions:
        """Extract prohibitions from structured English content."""
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
            return EurLexLegalProhibitions()

        prohibitions: list[
            EurLexLegalProhibition
        ] = []

        for node in structure.nodes:
            if node.kind not in _ALLOWED_NODE_KINDS:
                continue
            if node.text is None:
                continue

            parsed = _parse_prohibition(
                node.text
            )
            if parsed is None:
                continue

            kind, subject, action = parsed
            prohibitions.append(
                EurLexLegalProhibition(
                    subject=subject,
                    action=action,
                    kind=kind,
                    source_node_id=node.node_id,
                    source_text=node.text,
                    language=language,
                    article_node_id=(
                        _nearest_ancestor_id(
                            structure,
                            node,
                            EurLexDocumentNodeKind
                            .ARTICLE,
                        )
                    ),
                    paragraph_node_id=(
                        _nearest_ancestor_id(
                            structure,
                            node,
                            EurLexDocumentNodeKind
                            .PARAGRAPH,
                        )
                    ),
                )
            )

        return normalize_legal_prohibitions(
            tuple(prohibitions)
        )


def _parse_prohibition(
    text: str,
) -> tuple[
    EurLexLegalProhibitionKind,
    str,
    str,
] | None:
    for kind, pattern in _PROHIBITION_PATTERNS:
        match = pattern.fullmatch(text)
        if match is None:
            continue

        subject = match.group(
            "subject"
        ).strip(" ,;:")
        action = match.group(
            "action"
        ).strip()

        if not subject or not action:
            return None

        return kind, subject, action

    return None


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
