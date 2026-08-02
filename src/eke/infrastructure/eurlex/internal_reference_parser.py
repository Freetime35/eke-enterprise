"""Extract and conservatively resolve English internal references."""

from __future__ import annotations

import re

from eke.application.eurlex.document_structure import (
    EurLexDocumentNode,
    EurLexDocumentNodeKind,
    EurLexDocumentStructure,
)
from eke.application.eurlex.internal_references import (
    EurLexInternalReference,
    EurLexInternalReferenceKind,
    EurLexInternalReferences,
    normalize_internal_references,
)
from eke.domain.localization import LanguageCode

_REFERENCE_PATTERN = re.compile(
    r"""
    \b
    (?P<label>
        Articles?
        |
        paragraphs?
        |
        subparagraphs?
        |
        points?
        |
        Chapters?
        |
        Sections?
        |
        Parts?
        |
        Titles?
        |
        Annex(?:es)?
        |
        Appendices?
    )
    \s+
    (?P<ordinal>
        \(?[A-Za-z0-9IVXLCDM]+\)?
        (?:\([A-Za-z0-9]+\))*
        (?:\s+to\s+\(?[A-Za-z0-9IVXLCDM]+\)?)?
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)

_KIND_BY_LABEL: dict[
    str,
    EurLexInternalReferenceKind,
] = {
    "article": EurLexInternalReferenceKind.ARTICLE,
    "articles": EurLexInternalReferenceKind.ARTICLE,
    "paragraph": EurLexInternalReferenceKind.PARAGRAPH,
    "paragraphs": EurLexInternalReferenceKind.PARAGRAPH,
    "subparagraph": (
        EurLexInternalReferenceKind.SUBPARAGRAPH
    ),
    "subparagraphs": (
        EurLexInternalReferenceKind.SUBPARAGRAPH
    ),
    "point": EurLexInternalReferenceKind.POINT,
    "points": EurLexInternalReferenceKind.POINT,
    "chapter": EurLexInternalReferenceKind.CHAPTER,
    "chapters": EurLexInternalReferenceKind.CHAPTER,
    "section": EurLexInternalReferenceKind.SECTION,
    "sections": EurLexInternalReferenceKind.SECTION,
    "part": EurLexInternalReferenceKind.PART,
    "parts": EurLexInternalReferenceKind.PART,
    "title": EurLexInternalReferenceKind.TITLE,
    "titles": EurLexInternalReferenceKind.TITLE,
    "annex": EurLexInternalReferenceKind.ANNEX,
    "annexes": EurLexInternalReferenceKind.ANNEX,
    "appendix": EurLexInternalReferenceKind.APPENDIX,
    "appendices": EurLexInternalReferenceKind.APPENDIX,
}

_NODE_KIND_BY_REFERENCE_KIND: dict[
    EurLexInternalReferenceKind,
    EurLexDocumentNodeKind,
] = {
    EurLexInternalReferenceKind.ARTICLE: (
        EurLexDocumentNodeKind.ARTICLE
    ),
    EurLexInternalReferenceKind.PARAGRAPH: (
        EurLexDocumentNodeKind.PARAGRAPH
    ),
    EurLexInternalReferenceKind.SUBPARAGRAPH: (
        EurLexDocumentNodeKind.SUBPARAGRAPH
    ),
    EurLexInternalReferenceKind.POINT: (
        EurLexDocumentNodeKind.POINT
    ),
    EurLexInternalReferenceKind.CHAPTER: (
        EurLexDocumentNodeKind.CHAPTER
    ),
    EurLexInternalReferenceKind.SECTION: (
        EurLexDocumentNodeKind.SECTION
    ),
    EurLexInternalReferenceKind.PART: (
        EurLexDocumentNodeKind.PART
    ),
    EurLexInternalReferenceKind.TITLE: (
        EurLexDocumentNodeKind.TITLE
    ),
    EurLexInternalReferenceKind.ANNEX: (
        EurLexDocumentNodeKind.ANNEX
    ),
    EurLexInternalReferenceKind.APPENDIX: (
        EurLexDocumentNodeKind.APPENDIX
    ),
}

_ALLOWED_SOURCE_KINDS = frozenset(
    {
        EurLexDocumentNodeKind.PARAGRAPH,
        EurLexDocumentNodeKind.SUBPARAGRAPH,
        EurLexDocumentNodeKind.POINT,
        EurLexDocumentNodeKind.INDENT,
        EurLexDocumentNodeKind.RECITAL,
    }
)


class EurLexInternalReferenceParseError(
    ValueError
):
    """Raised when internal-reference extraction input is invalid."""


class EurLexInternalReferenceParser:
    """Extract explicit English internal references."""

    def parse(
        self,
        structure: EurLexDocumentStructure,
        *,
        language: LanguageCode,
    ) -> EurLexInternalReferences:
        """Extract and conservatively resolve references."""
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
            return EurLexInternalReferences()

        references: list[
            EurLexInternalReference
        ] = []

        for node in structure.nodes:
            if node.kind not in _ALLOWED_SOURCE_KINDS:
                continue
            if node.text is None:
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

            for match in _REFERENCE_PATTERN.finditer(
                node.text
            ):
                label = match.group(
                    "label"
                ).casefold()
                kind = _KIND_BY_LABEL.get(label)
                if kind is None:
                    continue

                ordinal = match.group(
                    "ordinal"
                )
                references.append(
                    EurLexInternalReference(
                        kind=kind,
                        source_node_id=node.node_id,
                        source_text=node.text,
                        reference_text=match.group(0),
                        target_ordinal=ordinal,
                        target_node_id=(
                            _resolve_target_node_id(
                                structure,
                                kind=kind,
                                ordinal=ordinal,
                            )
                        ),
                        article_node_id=(
                            article_node_id
                        ),
                        paragraph_node_id=(
                            paragraph_node_id
                        ),
                        language=language,
                    )
                )

        return normalize_internal_references(
            tuple(references)
        )


def _resolve_target_node_id(
    structure: EurLexDocumentStructure,
    *,
    kind: EurLexInternalReferenceKind,
    ordinal: str,
) -> str | None:
    if " to " in ordinal.casefold():
        return None

    node_kind = _NODE_KIND_BY_REFERENCE_KIND.get(
        kind
    )
    if node_kind is None:
        return None

    lookup_ordinal = _base_ordinal(
        ordinal
    )
    matches = tuple(
        node
        for node in structure.nodes
        if node.kind is node_kind
        and node.ordinal is not None
        and _ordinal_key(node.ordinal)
        == _ordinal_key(lookup_ordinal)
    )

    if len(matches) != 1:
        return None

    return matches[0].node_id


def _base_ordinal(
    ordinal: str,
) -> str:
    normalized = ordinal.strip()
    if normalized.startswith("("):
        return normalized

    index = normalized.find("(")
    if index == -1:
        return normalized

    return normalized[:index]


def _ordinal_key(
    ordinal: str,
) -> str:
    normalized = ordinal.strip().casefold()

    for prefix in (
        "article ",
        "paragraph ",
        "subparagraph ",
        "point ",
        "chapter ",
        "section ",
        "part ",
        "title ",
        "annex ",
        "appendix ",
    ):
        if normalized.startswith(prefix):
            normalized = normalized[
                len(prefix):
            ]
            break

    return normalized.strip(" .")


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
