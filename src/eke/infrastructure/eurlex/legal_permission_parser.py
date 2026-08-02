"""Extract explicit English legal permissions from document structure."""

from __future__ import annotations

import re

from eke.application.eurlex.document_structure import (
    EurLexDocumentNode,
    EurLexDocumentNodeKind,
    EurLexDocumentStructure,
)
from eke.application.eurlex.legal_permissions import (
    EurLexLegalPermission,
    EurLexLegalPermissionKind,
    EurLexLegalPermissions,
    normalize_legal_permissions,
)
from eke.domain.localization import LanguageCode

_PERMISSION_PATTERNS: tuple[
    tuple[
        EurLexLegalPermissionKind,
        re.Pattern[str],
    ],
    ...,
] = (
    (
        EurLexLegalPermissionKind.ENTITLED_TO,
        re.compile(
            r"""
            ^\s*
            (?P<subject>.+?)
            \s+
            (?:is|are)\s+entitled\s+to
            \s+
            (?P<action>.+?)
            \s*$
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
    (
        EurLexLegalPermissionKind.AUTHORISED_TO,
        re.compile(
            r"""
            ^\s*
            (?P<subject>.+?)
            \s+
            (?:is|are)\s+authorised\s+to
            \s+
            (?P<action>.+?)
            \s*$
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
    (
        EurLexLegalPermissionKind.ALLOWED_TO,
        re.compile(
            r"""
            ^\s*
            (?P<subject>.+?)
            \s+
            (?:is|are)\s+allowed\s+to
            \s+
            (?P<action>.+?)
            \s*$
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
    (
        EurLexLegalPermissionKind.MAY,
        re.compile(
            r"""
            ^\s*
            (?P<subject>.+?)
            \s+may\s+
            (?!not\b)
            (?P<action>.+?)
            \s*$
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
)

_NEGATIVE_PERMISSION_PATTERN = re.compile(
    r"""
    \b
    (?:
        may\s+not
        |
        (?:is|are)\s+not\s+entitled\s+to
        |
        (?:is|are)\s+not\s+authorised\s+to
        |
        (?:is|are)\s+not\s+allowed\s+to
    )
    \b
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


class EurLexLegalPermissionParseError(
    ValueError
):
    """Raised when legal-permission extraction input is invalid."""


class EurLexLegalPermissionParser:
    """Extract only explicit positive English permissions."""

    def parse(
        self,
        structure: EurLexDocumentStructure,
        *,
        language: LanguageCode,
    ) -> EurLexLegalPermissions:
        """Extract permissions from structured English content."""
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
            return EurLexLegalPermissions()

        permissions: list[
            EurLexLegalPermission
        ] = []

        for node in structure.nodes:
            if node.kind not in _ALLOWED_NODE_KINDS:
                continue
            if node.text is None:
                continue

            parsed = _parse_permission(
                node.text
            )
            if parsed is None:
                continue

            kind, subject, action = parsed
            permissions.append(
                EurLexLegalPermission(
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

        return normalize_legal_permissions(
            tuple(permissions)
        )


def _parse_permission(
    text: str,
) -> tuple[
    EurLexLegalPermissionKind,
    str,
    str,
] | None:
    if _NEGATIVE_PERMISSION_PATTERN.search(
        text
    ):
        return None

    for kind, pattern in _PERMISSION_PATTERNS:
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
