"""Tests for deterministic requirements graph construction."""

from eke.application.eurlex import (
    EurLexInternalReference,
    EurLexInternalReferenceKind,
    EurLexInternalReferences,
    EurLexLegalDefinition,
    EurLexLegalDefinitions,
    EurLexLegalObligation,
    EurLexLegalObligationKind,
    EurLexLegalObligations,
    EurLexLegalPermission,
    EurLexLegalPermissionKind,
    EurLexLegalPermissions,
    EurLexLegalProhibition,
    EurLexLegalProhibitionKind,
    EurLexLegalProhibitions,
    EurLexRequirementEdgeKind,
    EurLexRequirementsGraphBuilder,
)
from eke.domain.localization import LanguageCode


def test_builder_creates_only_source_backed_links() -> None:
    obligations = EurLexLegalObligations(
        obligations=(
            EurLexLegalObligation(
                subject="credit institution",
                action="submit a report",
                kind=(
                    EurLexLegalObligationKind.SHALL
                ),
                source_node_id="point-1",
                source_text=(
                    "Credit institution shall submit "
                    "a report under Article 12."
                ),
                language=LanguageCode("en"),
                article_node_id="article-20",
                paragraph_node_id="paragraph-1",
            ),
        )
    )
    permissions = EurLexLegalPermissions(
        permissions=(
            EurLexLegalPermission(
                subject="credit institution",
                action="request an extension",
                kind=(
                    EurLexLegalPermissionKind.MAY
                ),
                source_node_id="point-2",
                source_text=(
                    "Credit institution may request "
                    "an extension."
                ),
                language=LanguageCode("en"),
                article_node_id="article-20",
                paragraph_node_id="paragraph-1",
            ),
        )
    )
    prohibitions = EurLexLegalProhibitions(
        prohibitions=(
            EurLexLegalProhibition(
                subject="credit institution",
                action="alter the records",
                kind=(
                    EurLexLegalProhibitionKind
                    .SHALL_NOT
                ),
                source_node_id="point-3",
                source_text=(
                    "Credit institution shall not "
                    "alter the records."
                ),
                language=LanguageCode("en"),
                article_node_id="article-20",
            ),
        )
    )
    definitions = EurLexLegalDefinitions(
        definitions=(
            EurLexLegalDefinition(
                term="credit institution",
                definition="an undertaking",
                source_node_id=(
                    "definition-point-1"
                ),
                source_text=(
                    '"credit institution" means '
                    "an undertaking"
                ),
                language=LanguageCode("en"),
                article_node_id="article-4",
            ),
        )
    )
    references = EurLexInternalReferences(
        references=(
            EurLexInternalReference(
                kind=(
                    EurLexInternalReferenceKind
                    .ARTICLE
                ),
                source_node_id="point-1",
                source_text=(
                    "Credit institution shall submit "
                    "a report under Article 12."
                ),
                reference_text="Article 12",
                target_ordinal="12",
                target_node_id="article-12",
                article_node_id="article-20",
                paragraph_node_id="paragraph-1",
                language=LanguageCode("en"),
            ),
            EurLexInternalReference(
                kind=(
                    EurLexInternalReferenceKind
                    .ANNEX
                ),
                source_node_id="point-2",
                source_text="See Annex II.",
                reference_text="Annex II",
                target_ordinal="II",
                language=LanguageCode("en"),
            ),
        )
    )

    graph = EurLexRequirementsGraphBuilder().build(
        obligations=obligations,
        permissions=permissions,
        prohibitions=prohibitions,
        definitions=definitions,
        internal_references=references,
    )

    assert len(graph.requirements) == 3
    assert len(graph.definitions) == 1

    obligation = graph.requirements[0]
    assert graph.referenced_nodes(
        obligation.requirement_id
    )[0].node_id == "article-12"

    assert len(
        graph.definitions_for_requirement(
            obligation.requirement_id
        )
    ) == 1

    same_subject_edges = tuple(
        edge
        for edge in graph.edges
        if edge.kind
        is EurLexRequirementEdgeKind
        .SAME_SUBJECT
    )
    assert len(same_subject_edges) == 3

    reference_edges = tuple(
        edge
        for edge in graph.edges
        if edge.kind
        is EurLexRequirementEdgeKind
        .REFERENCES
    )
    assert len(reference_edges) == 1


def test_builder_is_deterministic() -> None:
    builder = EurLexRequirementsGraphBuilder()

    first = builder.build(
        obligations=EurLexLegalObligations(),
        permissions=EurLexLegalPermissions(),
        prohibitions=EurLexLegalProhibitions(),
        definitions=EurLexLegalDefinitions(),
        internal_references=(
            EurLexInternalReferences()
        ),
    )
    second = builder.build(
        obligations=EurLexLegalObligations(),
        permissions=EurLexLegalPermissions(),
        prohibitions=EurLexLegalProhibitions(),
        definitions=EurLexLegalDefinitions(),
        internal_references=(
            EurLexInternalReferences()
        ),
    )

    assert first == second
