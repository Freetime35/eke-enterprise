"""Transport-neutral EUR-Lex document structure."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class EurLexDocumentNodeKind(StrEnum):
    """Canonical kinds of structured document nodes."""

    PREAMBLE = "PREAMBLE"
    RECITAL = "RECITAL"
    PART = "PART"
    TITLE = "TITLE"
    CHAPTER = "CHAPTER"
    SECTION = "SECTION"
    ARTICLE = "ARTICLE"
    PARAGRAPH = "PARAGRAPH"
    SUBPARAGRAPH = "SUBPARAGRAPH"
    POINT = "POINT"
    INDENT = "INDENT"
    ANNEX = "ANNEX"
    APPENDIX = "APPENDIX"
    TABLE = "TABLE"
    FORMULA = "FORMULA"
    FOOTNOTE = "FOOTNOTE"
    VISUAL = "VISUAL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class EurLexDocumentNode:
    """Represent one source-backed structural node."""

    node_id: str
    kind: EurLexDocumentNodeKind
    source_element: str
    position: int
    ordinal: str | None = None
    heading: str | None = None
    text: str | None = None
    parent_id: str | None = None
    embedded_content_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.node_id, str):
            raise TypeError("node_id must be a string")
        node_id = self.node_id.strip()
        if not node_id:
            raise ValueError("node_id must not be empty")
        object.__setattr__(self, "node_id", node_id)

        if not isinstance(
            self.kind,
            EurLexDocumentNodeKind,
        ):
            raise TypeError(
                "kind must be an EurLexDocumentNodeKind"
            )

        if not isinstance(self.source_element, str):
            raise TypeError(
                "source_element must be a string"
            )
        source_element = self.source_element.strip()
        if not source_element:
            raise ValueError(
                "source_element must not be empty"
            )
        object.__setattr__(
            self,
            "source_element",
            source_element,
        )

        if not isinstance(self.position, int):
            raise TypeError("position must be an integer")
        if isinstance(self.position, bool):
            raise TypeError("position must be an integer")
        if self.position < 0:
            raise ValueError(
                "position must be zero or positive"
            )

        for name in (
            "ordinal",
            "heading",
            "text",
            "parent_id",
        ):
            value = getattr(self, name)
            if value is None:
                continue
            if not isinstance(value, str):
                raise TypeError(
                    f"{name} must be a string or None"
                )
            normalized = " ".join(value.split())
            object.__setattr__(
                self,
                name,
                normalized or None,
            )

        if self.parent_id == self.node_id:
            raise ValueError(
                "a node cannot be its own parent"
            )

        if any(
            not isinstance(content_id, str)
            or not content_id.strip()
            for content_id in self.embedded_content_ids
        ):
            raise TypeError(
                "embedded_content_ids must contain "
                "non-empty strings"
            )

        normalized_ids = tuple(
            dict.fromkeys(
                content_id.strip()
                for content_id
                in self.embedded_content_ids
            )
        )
        object.__setattr__(
            self,
            "embedded_content_ids",
            normalized_ids,
        )


@dataclass(frozen=True, slots=True)
class EurLexDocumentStructure:
    """Represent the ordered hierarchy of one legal document."""

    nodes: tuple[EurLexDocumentNode, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.nodes, tuple):
            raise TypeError("nodes must be a tuple")
        if any(
            not isinstance(node, EurLexDocumentNode)
            for node in self.nodes
        ):
            raise TypeError(
                "nodes must contain "
                "EurLexDocumentNode values"
            )

        node_ids = tuple(
            node.node_id for node in self.nodes
        )
        if len(node_ids) != len(set(node_ids)):
            raise ValueError(
                "node identifiers must be unique"
            )

        known_ids = set(node_ids)
        for node in self.nodes:
            if (
                node.parent_id is not None
                and node.parent_id not in known_ids
            ):
                raise ValueError(
                    "parent_id must reference an "
                    "existing node"
                )

        positions = tuple(
            node.position for node in self.nodes
        )
        if positions != tuple(sorted(positions)):
            raise ValueError(
                "nodes must be ordered by position"
            )

    def children_of(
        self,
        parent_id: str | None,
    ) -> tuple[EurLexDocumentNode, ...]:
        """Return direct children in source order."""
        if (
            parent_id is not None
            and not isinstance(parent_id, str)
        ):
            raise TypeError(
                "parent_id must be a string or None"
            )

        return tuple(
            node
            for node in self.nodes
            if node.parent_id == parent_id
        )

    def node_by_id(
        self,
        node_id: str,
    ) -> EurLexDocumentNode | None:
        """Return one node by identifier."""
        if not isinstance(node_id, str):
            raise TypeError("node_id must be a string")

        return next(
            (
                node
                for node in self.nodes
                if node.node_id == node_id
            ),
            None,
        )
