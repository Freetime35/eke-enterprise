"""Tests for EUR-Lex requirements graphs."""

import pytest

from eke.application.eurlex import (
    EurLexDefinitionNode,
    EurLexDocumentNodeKind,
    EurLexRequirementDocumentNode,
    EurLexRequirementEdge,
    EurLexRequirementEdgeKind,
    EurLexRequirementKind,
    EurLexRequirementNode,
    EurLexRequirementsGraph,
)
from eke.domain.localization import LanguageCode


def test_graph_queries_requirements_and_links() -> None:
    requirement = EurLexRequirementNode(
        requirement_id="requirement-1",
        kind=EurLexRequirementKind.OBLIGATION,
        subject="credit institution",
        action="submit a report",
        source_node_id="point-1",
        source_text=(
            "Credit institution shall submit "
            "a report."
        ),
        language=LanguageCode("en"),
        article_node_id="article-20",
    )
    definition = EurLexDefinitionNode(
        definition_id="definition-1",
        term="credit institution",
        definition="an undertaking",
        source_node_id="definition-point-1",
    )
    article = EurLexRequirementDocumentNode(
        node_id="article-20",
        kind=EurLexDocumentNodeKind.ARTICLE,
    )
    graph = EurLexRequirementsGraph(
        requirements=(requirement,),
        definitions=(definition,),
        document_nodes=(article,),
        edges=(
            EurLexRequirementEdge(
                edge_id="edge-1",
                kind=(
                    EurLexRequirementEdgeKind
                    .LOCATED_IN
                ),
                source_id="requirement-1",
                target_id="article-20",
            ),
            EurLexRequirementEdge(
                edge_id="edge-2",
                kind=(
                    EurLexRequirementEdgeKind
                    .DEFINES_SUBJECT
                ),
                source_id="requirement-1",
                target_id="definition-1",
            ),
        ),
    )

    assert graph.requirement_by_id(
        "requirement-1"
    ) == requirement
    assert graph.requirements_for_subject(
        "Credit Institution"
    ) == (requirement,)
    assert graph.definitions_for_requirement(
        "requirement-1"
    ) == (definition,)


def test_rejects_edges_to_missing_nodes() -> None:
    with pytest.raises(
        ValueError,
        match="existing graph nodes",
    ):
        EurLexRequirementsGraph(
            edges=(
                EurLexRequirementEdge(
                    edge_id="edge-1",
                    kind=(
                        EurLexRequirementEdgeKind
                        .REFERENCES
                    ),
                    source_id="missing-1",
                    target_id="missing-2",
                ),
            )
        )


def test_rejects_same_subject_self_loop() -> None:
    with pytest.raises(
        ValueError,
        match="must not loop",
    ):
        EurLexRequirementEdge(
            edge_id="edge-1",
            kind=(
                EurLexRequirementEdgeKind
                .SAME_SUBJECT
            ),
            source_id="requirement-1",
            target_id="requirement-1",
        )
