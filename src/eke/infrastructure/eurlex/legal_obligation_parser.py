"""Extract explicit English legal obligations from document structure."""

from __future__ import annotations

import re

from eke.application.eurlex.document_structure import (
    EurLexDocumentNode,
    EurLexDocumentNodeKind,
    EurLexDocumentStructure,
)
from eke.application.eurlex.legal_obligations import (
    EurLexLegalObligation,
    EurLexLegalObligationKind,
    EurLexLegalObligations,
    normalize_legal_obligations,
)
from eke.domain.localization import LanguageCode

_OBLIGATION_PATTERNS: tuple[
    tuple[
        EurLexLegalObligationKind,
        re.Pattern[str],
    ],
    ...,
] = (
    (
        EurLexLegalObligationKind.REQUIRED_TO,
        re.compile(
            r"""
            ^\s*
            (?P<subject>.+?)
            \s+
            (?:is|are)\s+required\s+to
            \s+
            (?P<action>.+?)
            \s*$
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
    (
        EurLexLegalObligationKind.HAS_TO,
        re.compile(
            r"""
            ^\s*
            (?P<subject>.+?)
            \s+
            (?:has|have)\s+to
            \s+
            (?P<action>.+?)
            \s*$
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
    (
        EurLexLegalObligationKind.SHALL,
        re.compile(
            r"""
            ^\s*
            (?P<subject>.+?)
            \s+shall\s+
            (?!not\b)
            (?P<action>.+?)
            \s*$
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
    (
        EurLexLegalObligationKind.MUST,
        re.compile(
            r"""
            ^\s*
            (?P<subject>.+?)
            \s+must\s+
            (?!not\b)
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


class EurLexLegalObligationParseError(
    ValueError
):
    """Raised when legal-obligation extraction input is invalid."""


class EurLexLegalObligationParser:
    """Extract only explicit positive English obligations."""

    def parse(
        self,
        structure: EurLexDocumentStructure,
        *,
        language: LanguageCode,
    ) -> EurLexLegalObligations:
        """Extract obligations from structured English content."""
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
            return EurLexLegalObligations()

        obligations: list[
            EurLexLegalObligation
        ] = []

        for node in structure.nodes:
            if node.kind not in _ALLOWED_NODE_KINDS:
                continue
            if node.text is None:
                continue

            parsed = _parse_obligation(
                node.text
            )
            if parsed is None:
                continue

            kind, subject, action = parsed
            obligations.append(
                EurLexLegalObligation(
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

        return normalize_legal_obligations(
            tuple(obligations)
        )


def _parse_obligation(
    text: str,
) -> tuple[
    EurLexLegalObligationKind,
    str,
    str,
] | None:
    for kind, pattern in _OBLIGATION_PATTERNS:
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
