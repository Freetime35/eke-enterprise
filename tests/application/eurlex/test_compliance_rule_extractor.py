"""Tests for compliance-rule extraction from requirements graphs."""

from eke.application.eurlex import (
    EurLexComplianceRuleExtractor,
    EurLexComplianceRuleKind,
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


def test_extracts_one_rule_per_requirement() -> None:
    obligation = EurLexRequirementNode(
        requirement_id="requirement-1",
        kind=EurLexRequirementKind.OBLIGATION,
        subject="credit institution",
        action="submit a report",
        source_node_id="point-1",
        source_text=(
            "Credit institution shall submit "
            "a report under Article 12."
        ),
        language=LanguageCode("en"),
        article_node_id="article-20",
        paragraph_node_id="paragraph-1",
    )
    permission = EurLexRequirementNode(
        requirement_id="requirement-2",
        kind=EurLexRequirementKind.PERMISSION,
        subject="credit institution",
        action="request an extension",
        source_node_id="point-2",
        source_text=(
            "Credit institution may request "
            "an extension."
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
    article_12 = (
        EurLexRequirementDocumentNode(
            node_id="article-12",
            kind=EurLexDocumentNodeKind.ARTICLE,
        )
    )
    article_20 = (
        EurLexRequirementDocumentNode(
            node_id="article-20",
            kind=EurLexDocumentNodeKind.ARTICLE,
        )
    )
    paragraph_1 = (
        EurLexRequirementDocumentNode(
            node_id="paragraph-1",
            kind=(
                EurLexDocumentNodeKind
                .PARAGRAPH
            ),
        )
    )
    graph = EurLexRequirementsGraph(
        requirements=(
            obligation,
            permission,
        ),
        definitions=(definition,),
        document_nodes=(
            article_12,
            article_20,
            paragraph_1,
        ),
        edges=(
            EurLexRequirementEdge(
                edge_id="edge-1",
                kind=(
                    EurLexRequirementEdgeKind
                    .REFERENCES
                ),
                source_id="requirement-1",
                target_id="article-12",
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
            EurLexRequirementEdge(
                edge_id="edge-3",
                kind=(
                    EurLexRequirementEdgeKind
                    .DEFINES_SUBJECT
                ),
                source_id="requirement-2",
                target_id="definition-1",
            ),
        ),
    )

    rules = (
        EurLexComplianceRuleExtractor()
        .extract(graph)
    )

    assert len(rules.rules) == 2

    first = rules.rules[0]
    assert first.kind is (
        EurLexComplianceRuleKind
        .REQUIREMENT
    )
    assert first.source_requirement_id == (
        "requirement-1"
    )
    assert first.referenced_node_ids == (
        "article-12",
    )
    assert first.definition_ids == (
        "definition-1",
    )

    second = rules.rules[1]
    assert second.kind is (
        EurLexComplianceRuleKind.PERMISSION
    )


def test_extractor_is_deterministic() -> None:
    graph = EurLexRequirementsGraph()
    extractor = EurLexComplianceRuleExtractor()

    first = extractor.extract(graph)
    second = extractor.extract(graph)

    assert first == second
