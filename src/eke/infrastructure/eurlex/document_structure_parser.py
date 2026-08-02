"""Parse structured EUR-Lex XML or XHTML documents."""

from __future__ import annotations

from dataclasses import replace
from xml.etree import ElementTree

from eke.application.eurlex.document_structure import (
    EurLexDocumentNode,
    EurLexDocumentNodeKind,
    EurLexDocumentStructure,
)


class EurLexDocumentStructureParseError(ValueError):
    """Raised when structured document content is malformed."""


_STRUCTURAL_KINDS: dict[str, EurLexDocumentNodeKind] = {
    "PREAMBLE": EurLexDocumentNodeKind.PREAMBLE,
    "RECITAL": EurLexDocumentNodeKind.RECITAL,
    "PART": EurLexDocumentNodeKind.PART,
    "TITLE": EurLexDocumentNodeKind.TITLE,
    "CHAPTER": EurLexDocumentNodeKind.CHAPTER,
    "SECTION": EurLexDocumentNodeKind.SECTION,
    "ARTICLE": EurLexDocumentNodeKind.ARTICLE,
    "PARAGRAPH": EurLexDocumentNodeKind.PARAGRAPH,
    "SUBPARAGRAPH": EurLexDocumentNodeKind.SUBPARAGRAPH,
    "POINT": EurLexDocumentNodeKind.POINT,
    "INDENT": EurLexDocumentNodeKind.INDENT,
    "ANNEX": EurLexDocumentNodeKind.ANNEX,
    "APPENDIX": EurLexDocumentNodeKind.APPENDIX,
    "TABLE": EurLexDocumentNodeKind.TABLE,
    "FORMULA": EurLexDocumentNodeKind.FORMULA,
    "MATH": EurLexDocumentNodeKind.FORMULA,
    "FOOTNOTE": EurLexDocumentNodeKind.FOOTNOTE,
    "NOTE": EurLexDocumentNodeKind.FOOTNOTE,
    "IMAGE": EurLexDocumentNodeKind.VISUAL,
    "FIGURE": EurLexDocumentNodeKind.VISUAL,
    "GRAPHIC": EurLexDocumentNodeKind.VISUAL,
}

_ORDINAL_NAMES = frozenset(
    {
        "NUMBER",
        "NUM",
        "ORDINAL",
        "LABEL",
    }
)
_HEADING_NAMES = frozenset(
    {
        "HEADING",
        "TITLE",
        "TI",
        "CAPTION",
    }
)
_TEXT_NAMES = frozenset(
    {
        "TEXT",
        "CONTENT",
        "P",
        "PARA",
    }
)
_EMBEDDED_KINDS = frozenset(
    {
        EurLexDocumentNodeKind.TABLE,
        EurLexDocumentNodeKind.FORMULA,
        EurLexDocumentNodeKind.FOOTNOTE,
        EurLexDocumentNodeKind.VISUAL,
    }
)


class XmlEurLexDocumentStructureParser:
    """Parse source order and hierarchy from XML or XHTML."""

    def parse(
        self,
        content: bytes,
    ) -> EurLexDocumentStructure:
        """Parse one structured document."""
        if not isinstance(content, bytes):
            raise TypeError("content must be bytes")
        if not content.strip():
            raise EurLexDocumentStructureParseError(
                "content must not be empty"
            )

        try:
            root = ElementTree.fromstring(content)
        except ElementTree.ParseError as exc:
            raise EurLexDocumentStructureParseError(
                "content must be valid XML or XHTML"
            ) from exc

        nodes: list[EurLexDocumentNode] = []
        self._walk(
            root,
            parent_id=None,
            nodes=nodes,
        )

        nodes = self._attach_embedded_content(
            nodes
        )
        return EurLexDocumentStructure(
            nodes=tuple(nodes)
        )

    def _walk(
        self,
        element: ElementTree.Element,
        *,
        parent_id: str | None,
        nodes: list[EurLexDocumentNode],
    ) -> None:
        local_name = _local_name(element.tag)
        kind = _STRUCTURAL_KINDS.get(
            local_name,
        )

        current_parent = parent_id
        if kind is not None:
            position = len(nodes)
            node_id = _node_identifier(
                element,
                kind=kind,
                position=position,
            )
            node = EurLexDocumentNode(
                node_id=node_id,
                kind=kind,
                ordinal=_first_child_text(
                    element,
                    _ORDINAL_NAMES,
                ),
                heading=_first_child_text(
                    element,
                    _HEADING_NAMES,
                ),
                text=_direct_text(element),
                parent_id=parent_id,
                source_element=local_name,
                position=position,
            )
            nodes.append(node)
            current_parent = node_id

        for child in element:
            self._walk(
                child,
                parent_id=current_parent,
                nodes=nodes,
            )

    @staticmethod
    def _attach_embedded_content(
        nodes: list[EurLexDocumentNode],
    ) -> list[EurLexDocumentNode]:
        embedded_by_parent: dict[
            str,
            list[str],
        ] = {}

        for node in nodes:
            if (
                node.kind in _EMBEDDED_KINDS
                and node.parent_id is not None
            ):
                embedded_by_parent.setdefault(
                    node.parent_id,
                    [],
                ).append(node.node_id)

        return [
            replace(
                node,
                embedded_content_ids=tuple(
                    embedded_by_parent.get(
                        node.node_id,
                        (),
                    )
                ),
            )
            for node in nodes
        ]


def _local_name(tag: str) -> str:
    return tag.rsplit("}", maxsplit=1)[-1].upper()


def _node_identifier(
    element: ElementTree.Element,
    *,
    kind: EurLexDocumentNodeKind,
    position: int,
) -> str:
    for name in (
        "id",
        "ID",
        "{http://www.w3.org/XML/1998/namespace}id",
    ):
        value = element.attrib.get(name)
        if value is not None and value.strip():
            return value.strip()

    return (
        f"{kind.value.casefold().replace('_', '-')}"
        f"-{position + 1}"
    )


def _first_child_text(
    element: ElementTree.Element,
    names: frozenset[str],
) -> str | None:
    for child in element:
        if _local_name(child.tag) not in names:
            continue
        value = _all_text(child)
        if value is not None:
            return value

    return None


def _direct_text(
    element: ElementTree.Element,
) -> str | None:
    parts: list[str] = []

    if element.text is not None:
        parts.append(element.text)

    for child in element:
        child_name = _local_name(child.tag)
        if (
            child_name not in _ORDINAL_NAMES
            and child_name not in _HEADING_NAMES
            and child_name not in _STRUCTURAL_KINDS
        ):
            child_text = _all_text(child)
            if child_text is not None:
                parts.append(child_text)

        if child.tail is not None:
            parts.append(child.tail)

    normalized = " ".join(
        " ".join(parts).split()
    )
    return normalized or None


def _all_text(
    element: ElementTree.Element,
) -> str | None:
    normalized = " ".join(
        " ".join(element.itertext()).split()
    )
    return normalized or None
