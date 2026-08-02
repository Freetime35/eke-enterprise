"""Source-backed EUR-Lex requirements graph."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from eke.application.eurlex.document_structure import (
    EurLexDocumentNodeKind,
)
from eke.domain.localization import LanguageCode


def _required_text(
    value: str,
    *,
    name: str,
) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")

    normalized = " ".join(value.split())
    if not normalized:
        raise ValueError(
            f"{name} must not be empty"
        )

    return normalized


def _optional_text(
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


class EurLexRequirementKind(StrEnum):
    """Canonical requirement node kinds."""

    OBLIGATION = "OBLIGATION"
    PERMISSION = "PERMISSION"
    PROHIBITION = "PROHIBITION"


class EurLexRequirementEdgeKind(StrEnum):
    """Canonical graph edge kinds."""

    LOCATED_IN = "LOCATED_IN"
    REFERENCES = "REFERENCES"
    DEFINES_SUBJECT = "DEFINES_SUBJECT"
    SAME_SUBJECT = "SAME_SUBJECT"


@dataclass(frozen=True, slots=True)
class EurLexRequirementNode:
    """Represent one obligation, permission or prohibition."""

    requirement_id: str
    kind: EurLexRequirementKind
    subject: str
    action: str
    source_node_id: str
    source_text: str
    language: LanguageCode
    article_node_id: str | None = None
    paragraph_node_id: str | None = None

    def __post_init__(self) -> None:
        for name in (
            "requirement_id",
            "subject",
            "action",
            "source_node_id",
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

        for name in (
            "article_node_id",
            "paragraph_node_id",
        ):
            object.__setattr__(
                self,
                name,
                _optional_text(
                    getattr(self, name),
                    name=name,
                ),
            )

        if not isinstance(
            self.kind,
            EurLexRequirementKind,
        ):
            raise TypeError(
                "kind must be an "
                "EurLexRequirementKind"
            )

        if not isinstance(
            self.language,
            LanguageCode,
        ):
            raise TypeError(
                "language must be a LanguageCode"
            )

    @property
    def normalized_subject(self) -> str:
        """Return a conservative subject lookup key."""
        return self.subject.casefold()


@dataclass(frozen=True, slots=True)
class EurLexDefinitionNode:
    """Represent one legal definition inside the graph."""

    definition_id: str
    term: str
    definition: str
    source_node_id: str
    article_node_id: str | None = None

    def __post_init__(self) -> None:
        for name in (
            "definition_id",
            "term",
            "definition",
            "source_node_id",
        ):
            object.__setattr__(
                self,
                name,
                _required_text(
                    getattr(self, name),
                    name=name,
                ),
            )

        object.__setattr__(
            self,
            "article_node_id",
            _optional_text(
                self.article_node_id,
                name="article_node_id",
            ),
        )

    @property
    def normalized_term(self) -> str:
        """Return a conservative term lookup key."""
        return self.term.casefold()


@dataclass(frozen=True, slots=True)
class EurLexRequirementDocumentNode:
    """Represent one structural document node in the graph."""

    node_id: str
    kind: EurLexDocumentNodeKind

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "node_id",
            _required_text(
                self.node_id,
                name="node_id",
            ),
        )

        if not isinstance(
            self.kind,
            EurLexDocumentNodeKind,
        ):
            raise TypeError(
                "kind must be an "
                "EurLexDocumentNodeKind"
            )


@dataclass(frozen=True, slots=True)
class EurLexRequirementEdge:
    """Represent one typed graph relation."""

    edge_id: str
    kind: EurLexRequirementEdgeKind
    source_id: str
    target_id: str
    evidence_node_id: str | None = None

    def __post_init__(self) -> None:
        for name in (
            "edge_id",
            "source_id",
            "target_id",
        ):
            object.__setattr__(
                self,
                name,
                _required_text(
                    getattr(self, name),
                    name=name,
                ),
            )

        object.__setattr__(
            self,
            "evidence_node_id",
            _optional_text(
                self.evidence_node_id,
                name="evidence_node_id",
            ),
        )

        if not isinstance(
            self.kind,
            EurLexRequirementEdgeKind,
        ):
            raise TypeError(
                "kind must be an "
                "EurLexRequirementEdgeKind"
            )

        if (
            self.kind
            is EurLexRequirementEdgeKind
            .SAME_SUBJECT
            and self.source_id == self.target_id
        ):
            raise ValueError(
                "SAME_SUBJECT edges must not loop"
            )


@dataclass(frozen=True, slots=True)
class EurLexRequirementsGraph:
    """Contain a closed source-backed requirements graph."""

    requirements: tuple[
        EurLexRequirementNode,
        ...,
    ] = ()
    definitions: tuple[
        EurLexDefinitionNode,
        ...,
    ] = ()
    document_nodes: tuple[
        EurLexRequirementDocumentNode,
        ...,
    ] = ()
    edges: tuple[
        EurLexRequirementEdge,
        ...,
    ] = ()

    def __post_init__(self) -> None:
        for name, expected_type in (
            ("requirements", EurLexRequirementNode),
            ("definitions", EurLexDefinitionNode),
            (
                "document_nodes",
                EurLexRequirementDocumentNode,
            ),
            ("edges", EurLexRequirementEdge),
        ):
            values = getattr(self, name)
            if not isinstance(values, tuple):
                raise TypeError(
                    f"{name} must be a tuple"
                )
            if any(
                not isinstance(
                    value,
                    expected_type,
                )
                for value in values
            ):
                raise TypeError(
                    f"{name} contains invalid values"
                )

        node_ids = (
            tuple(
                node.requirement_id
                for node in self.requirements
            )
            + tuple(
                node.definition_id
                for node in self.definitions
            )
            + tuple(
                node.node_id
                for node in self.document_nodes
            )
        )
        if len(node_ids) != len(set(node_ids)):
            raise ValueError(
                "graph node identifiers must be unique"
            )

        edge_ids = tuple(
            edge.edge_id for edge in self.edges
        )
        if len(edge_ids) != len(set(edge_ids)):
            raise ValueError(
                "edge identifiers must be unique"
            )

        known_node_ids = set(node_ids)
        for edge in self.edges:
            if (
                edge.source_id not in known_node_ids
                or edge.target_id
                not in known_node_ids
            ):
                raise ValueError(
                    "edges must reference existing "
                    "graph nodes"
                )

    def requirement_by_id(
        self,
        requirement_id: str,
    ) -> EurLexRequirementNode | None:
        """Return one requirement by identifier."""
        normalized = _required_text(
            requirement_id,
            name="requirement_id",
        )

        return next(
            (
                requirement
                for requirement in self.requirements
                if requirement.requirement_id
                == normalized
            ),
            None,
        )

    def requirements_for_subject(
        self,
        subject: str,
    ) -> tuple[EurLexRequirementNode, ...]:
        """Return requirements with an exact subject match."""
        normalized = _required_text(
            subject,
            name="subject",
        ).casefold()

        return tuple(
            requirement
            for requirement in self.requirements
            if requirement.normalized_subject
            == normalized
        )

    def outgoing_edges(
        self,
        node_id: str,
    ) -> tuple[EurLexRequirementEdge, ...]:
        """Return edges emitted by one graph node."""
        normalized = _required_text(
            node_id,
            name="node_id",
        )

        return tuple(
            edge
            for edge in self.edges
            if edge.source_id == normalized
        )

    def incoming_edges(
        self,
        node_id: str,
    ) -> tuple[EurLexRequirementEdge, ...]:
        """Return edges targeting one graph node."""
        normalized = _required_text(
            node_id,
            name="node_id",
        )

        return tuple(
            edge
            for edge in self.edges
            if edge.target_id == normalized
        )

    def referenced_nodes(
        self,
        requirement_id: str,
    ) -> tuple[
        EurLexRequirementDocumentNode,
        ...,
    ]:
        """Return document nodes referenced by a requirement."""
        target_ids = {
            edge.target_id
            for edge in self.outgoing_edges(
                requirement_id
            )
            if edge.kind
            is EurLexRequirementEdgeKind
            .REFERENCES
        }

        return tuple(
            node
            for node in self.document_nodes
            if node.node_id in target_ids
        )

    def definitions_for_requirement(
        self,
        requirement_id: str,
    ) -> tuple[EurLexDefinitionNode, ...]:
        """Return definitions linked to a requirement subject."""
        target_ids = {
            edge.target_id
            for edge in self.outgoing_edges(
                requirement_id
            )
            if edge.kind
            is EurLexRequirementEdgeKind
            .DEFINES_SUBJECT
        }

        return tuple(
            definition
            for definition in self.definitions
            if definition.definition_id
            in target_ids
        )
