"""Build source-backed EUR-Lex requirements graphs."""

from __future__ import annotations

from hashlib import sha256
from itertools import combinations

from eke.application.eurlex.document_structure import (
    EurLexDocumentNodeKind,
)
from eke.application.eurlex.internal_references import (
    EurLexInternalReferences,
)
from eke.application.eurlex.legal_definitions import (
    EurLexLegalDefinitions,
)
from eke.application.eurlex.legal_obligations import (
    EurLexLegalObligations,
)
from eke.application.eurlex.legal_permissions import (
    EurLexLegalPermissions,
)
from eke.application.eurlex.legal_prohibitions import (
    EurLexLegalProhibitions,
)
from eke.application.eurlex.requirements_graph import (
    EurLexDefinitionNode,
    EurLexRequirementDocumentNode,
    EurLexRequirementEdge,
    EurLexRequirementEdgeKind,
    EurLexRequirementKind,
    EurLexRequirementNode,
    EurLexRequirementsGraph,
)


class EurLexRequirementsGraphBuilder:
    """Assemble normalized legal extractions into a graph."""

    def build(
        self,
        *,
        obligations: EurLexLegalObligations,
        permissions: EurLexLegalPermissions,
        prohibitions: EurLexLegalProhibitions,
        definitions: EurLexLegalDefinitions,
        internal_references: EurLexInternalReferences,
    ) -> EurLexRequirementsGraph:
        """Build a closed deterministic requirements graph."""
        for name, value, expected_type in (
            (
                "obligations",
                obligations,
                EurLexLegalObligations,
            ),
            (
                "permissions",
                permissions,
                EurLexLegalPermissions,
            ),
            (
                "prohibitions",
                prohibitions,
                EurLexLegalProhibitions,
            ),
            (
                "definitions",
                definitions,
                EurLexLegalDefinitions,
            ),
            (
                "internal_references",
                internal_references,
                EurLexInternalReferences,
            ),
        ):
            if not isinstance(
                value,
                expected_type,
            ):
                raise TypeError(
                    f"{name} has an invalid type"
                )

        requirement_nodes = (
            self._requirement_nodes(
                obligations=obligations,
                permissions=permissions,
                prohibitions=prohibitions,
            )
        )
        definition_nodes = (
            self._definition_nodes(
                definitions
            )
        )
        document_nodes = (
            self._document_nodes(
                requirement_nodes,
                internal_references,
            )
        )
        edges = self._edges(
            requirements=requirement_nodes,
            definitions=definition_nodes,
            document_nodes=document_nodes,
            internal_references=(
                internal_references
            ),
        )

        return EurLexRequirementsGraph(
            requirements=requirement_nodes,
            definitions=definition_nodes,
            document_nodes=document_nodes,
            edges=edges,
        )

    @staticmethod
    def _requirement_nodes(
        *,
        obligations: EurLexLegalObligations,
        permissions: EurLexLegalPermissions,
        prohibitions: EurLexLegalProhibitions,
    ) -> tuple[EurLexRequirementNode, ...]:
        nodes: list[
            EurLexRequirementNode
        ] = []

        for index, obligation in enumerate(
            obligations.obligations
        ):
            nodes.append(
                EurLexRequirementNode(
                    requirement_id=_stable_id(
                        "requirement",
                        "obligation",
                        obligation.source_node_id,
                        str(index),
                    ),
                    kind=(
                        EurLexRequirementKind
                        .OBLIGATION
                    ),
                    subject=obligation.subject,
                    action=obligation.action,
                    source_node_id=(
                        obligation.source_node_id
                    ),
                    source_text=(
                        obligation.source_text
                    ),
                    language=obligation.language,
                    article_node_id=(
                        obligation.article_node_id
                    ),
                    paragraph_node_id=(
                        obligation
                        .paragraph_node_id
                    ),
                )
            )

        for index, permission in enumerate(
            permissions.permissions
        ):
            nodes.append(
                EurLexRequirementNode(
                    requirement_id=_stable_id(
                        "requirement",
                        "permission",
                        permission.source_node_id,
                        str(index),
                    ),
                    kind=(
                        EurLexRequirementKind
                        .PERMISSION
                    ),
                    subject=permission.subject,
                    action=permission.action,
                    source_node_id=(
                        permission.source_node_id
                    ),
                    source_text=(
                        permission.source_text
                    ),
                    language=permission.language,
                    article_node_id=(
                        permission.article_node_id
                    ),
                    paragraph_node_id=(
                        permission
                        .paragraph_node_id
                    ),
                )
            )

        for index, prohibition in enumerate(
            prohibitions.prohibitions
        ):
            nodes.append(
                EurLexRequirementNode(
                    requirement_id=_stable_id(
                        "requirement",
                        "prohibition",
                        prohibition.source_node_id,
                        str(index),
                    ),
                    kind=(
                        EurLexRequirementKind
                        .PROHIBITION
                    ),
                    subject=prohibition.subject,
                    action=prohibition.action,
                    source_node_id=(
                        prohibition.source_node_id
                    ),
                    source_text=(
                        prohibition.source_text
                    ),
                    language=prohibition.language,
                    article_node_id=(
                        prohibition.article_node_id
                    ),
                    paragraph_node_id=(
                        prohibition
                        .paragraph_node_id
                    ),
                )
            )

        return tuple(nodes)

    @staticmethod
    def _definition_nodes(
        definitions: EurLexLegalDefinitions,
    ) -> tuple[EurLexDefinitionNode, ...]:
        return tuple(
            EurLexDefinitionNode(
                definition_id=_stable_id(
                    "definition",
                    definition.source_node_id,
                    str(index),
                ),
                term=definition.term,
                definition=definition.definition,
                source_node_id=(
                    definition.source_node_id
                ),
                article_node_id=(
                    definition.article_node_id
                ),
            )
            for index, definition
            in enumerate(
                definitions.definitions
            )
        )

    @staticmethod
    def _document_nodes(
        requirements: tuple[
            EurLexRequirementNode,
            ...,
        ],
        internal_references: (
            EurLexInternalReferences
        ),
    ) -> tuple[
        EurLexRequirementDocumentNode,
        ...,
    ]:
        kinds_by_id: dict[
            str,
            EurLexDocumentNodeKind,
        ] = {}

        for requirement in requirements:
            if (
                requirement.article_node_id
                is not None
            ):
                kinds_by_id.setdefault(
                    requirement.article_node_id,
                    EurLexDocumentNodeKind.ARTICLE,
                )
            if (
                requirement.paragraph_node_id
                is not None
            ):
                kinds_by_id.setdefault(
                    requirement
                    .paragraph_node_id,
                    EurLexDocumentNodeKind
                    .PARAGRAPH,
                )

        for reference in (
            internal_references.references
        ):
            if (
                reference.target_node_id
                is not None
            ):
                kinds_by_id.setdefault(
                    reference.target_node_id,
                    _document_kind(
                        reference.kind.value
                    ),
                )

        return tuple(
            EurLexRequirementDocumentNode(
                node_id=node_id,
                kind=kind,
            )
            for node_id, kind
            in sorted(kinds_by_id.items())
        )

    @staticmethod
    def _edges(
        *,
        requirements: tuple[
            EurLexRequirementNode,
            ...,
        ],
        definitions: tuple[
            EurLexDefinitionNode,
            ...,
        ],
        document_nodes: tuple[
            EurLexRequirementDocumentNode,
            ...,
        ],
        internal_references: (
            EurLexInternalReferences
        ),
    ) -> tuple[EurLexRequirementEdge, ...]:
        edges: list[
            EurLexRequirementEdge
        ] = []

        document_ids = {
            node.node_id
            for node in document_nodes
        }

        for requirement in requirements:
            for target_id in (
                requirement.paragraph_node_id,
                requirement.article_node_id,
            ):
                if (
                    target_id is None
                    or target_id
                    not in document_ids
                ):
                    continue

                edges.append(
                    _edge(
                        kind=(
                            EurLexRequirementEdgeKind
                            .LOCATED_IN
                        ),
                        source_id=(
                            requirement
                            .requirement_id
                        ),
                        target_id=target_id,
                        evidence_node_id=(
                            requirement
                            .source_node_id
                        ),
                    )
                )

            for reference in (
                internal_references
                .references_from_node(
                    requirement.source_node_id
                )
            ):
                if (
                    reference.target_node_id
                    is None
                    or reference.target_node_id
                    not in document_ids
                ):
                    continue

                edges.append(
                    _edge(
                        kind=(
                            EurLexRequirementEdgeKind
                            .REFERENCES
                        ),
                        source_id=(
                            requirement
                            .requirement_id
                        ),
                        target_id=(
                            reference
                            .target_node_id
                        ),
                        evidence_node_id=(
                            reference.source_node_id
                        ),
                    )
                )

            for definition in definitions:
                if (
                    requirement
                    .normalized_subject
                    != definition
                    .normalized_term
                ):
                    continue

                edges.append(
                    _edge(
                        kind=(
                            EurLexRequirementEdgeKind
                            .DEFINES_SUBJECT
                        ),
                        source_id=(
                            requirement
                            .requirement_id
                        ),
                        target_id=(
                            definition
                            .definition_id
                        ),
                        evidence_node_id=(
                            definition
                            .source_node_id
                        ),
                    )
                )

        for left, right in combinations(
            requirements,
            2,
        ):
            if (
                left.normalized_subject
                != right.normalized_subject
            ):
                continue

            source, target = sorted(
                (
                    left.requirement_id,
                    right.requirement_id,
                )
            )
            edges.append(
                _edge(
                    kind=(
                        EurLexRequirementEdgeKind
                        .SAME_SUBJECT
                    ),
                    source_id=source,
                    target_id=target,
                )
            )

        return tuple(
            dict.fromkeys(edges)
        )


def _document_kind(
    value: str,
) -> EurLexDocumentNodeKind:
    try:
        return EurLexDocumentNodeKind(value)
    except ValueError:
        return EurLexDocumentNodeKind.UNKNOWN


def _stable_id(
    prefix: str,
    *parts: str,
) -> str:
    digest = sha256(
        "\x1f".join(parts).encode(
            "utf-8"
        )
    ).hexdigest()[:16]
    return f"{prefix}-{digest}"


def _edge(
    *,
    kind: EurLexRequirementEdgeKind,
    source_id: str,
    target_id: str,
    evidence_node_id: str | None = None,
) -> EurLexRequirementEdge:
    return EurLexRequirementEdge(
        edge_id=_stable_id(
            "edge",
            kind.value,
            source_id,
            target_id,
            evidence_node_id or "",
        ),
        kind=kind,
        source_id=source_id,
        target_id=target_id,
        evidence_node_id=evidence_node_id,
    )
