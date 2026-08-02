"""Tests for legal actor extraction from rules and graph."""

from eke.application.eurlex import (
    EurLexComplianceRule,
    EurLexComplianceRuleKind,
    EurLexComplianceRules,
    EurLexLegalActorExtractor,
    EurLexLegalActorKind,
    EurLexRequirementKind,
    EurLexRequirementNode,
    EurLexRequirementsGraph,
)
from eke.domain.localization import LanguageCode


def test_extracts_and_reuses_explicit_actors() -> None:
    first_requirement = EurLexRequirementNode(
        requirement_id="requirement-1",
        kind=EurLexRequirementKind.OBLIGATION,
        subject="Member State",
        action="notify the Commission",
        source_node_id="point-1",
        source_text=(
            "Member State shall notify "
            "the Commission."
        ),
        language=LanguageCode("en"),
    )
    second_requirement = EurLexRequirementNode(
        requirement_id="requirement-2",
        kind=EurLexRequirementKind.PERMISSION,
        subject="Member State",
        action="request assistance",
        source_node_id="point-2",
        source_text=(
            "Member State may request "
            "assistance."
        ),
        language=LanguageCode("en"),
    )
    graph = EurLexRequirementsGraph(
        requirements=(
            first_requirement,
            second_requirement,
        )
    )
    rules = EurLexComplianceRules(
        rules=(
            EurLexComplianceRule(
                rule_id="rule-1",
                kind=(
                    EurLexComplianceRuleKind
                    .REQUIREMENT
                ),
                subject="Member State",
                action="notify the Commission",
                source_requirement_id=(
                    "requirement-1"
                ),
                source_node_id="point-1",
                source_text=(
                    "Member State shall notify "
                    "the Commission."
                ),
                language=LanguageCode("en"),
            ),
            EurLexComplianceRule(
                rule_id="rule-2",
                kind=(
                    EurLexComplianceRuleKind
                    .PERMISSION
                ),
                subject="Member State",
                action="request assistance",
                source_requirement_id=(
                    "requirement-2"
                ),
                source_node_id="point-2",
                source_text=(
                    "Member State may request "
                    "assistance."
                ),
                language=LanguageCode("en"),
            ),
        )
    )

    actors = EurLexLegalActorExtractor().extract(
        graph=graph,
        rules=rules,
    )

    assert len(actors.actors) == 1
    assert len(actors.mentions) == 2
    assert actors.actors[0].kind is (
        EurLexLegalActorKind.MEMBER_STATE
    )


def test_definition_link_classifies_regulated_entity() -> None:
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
    )
    graph = EurLexRequirementsGraph(
        requirements=(requirement,)
    )
    rules = EurLexComplianceRules(
        rules=(
            EurLexComplianceRule(
                rule_id="rule-1",
                kind=(
                    EurLexComplianceRuleKind
                    .REQUIREMENT
                ),
                subject="credit institution",
                action="submit a report",
                source_requirement_id=(
                    "requirement-1"
                ),
                source_node_id="point-1",
                source_text=(
                    "Credit institution shall "
                    "submit a report."
                ),
                language=LanguageCode("en"),
                definition_ids=(
                    "definition-1",
                ),
            ),
        )
    )

    actors = EurLexLegalActorExtractor().extract(
        graph=graph,
        rules=rules,
    )

    actor = actors.actors[0]
    assert actor.kind is (
        EurLexLegalActorKind
        .REGULATED_ENTITY
    )
    assert actor.definition_id == (
        "definition-1"
    )


def test_unknown_explicit_subject_is_generic_actor() -> None:
    requirement = EurLexRequirementNode(
        requirement_id="requirement-1",
        kind=EurLexRequirementKind.OBLIGATION,
        subject="reporting body",
        action="retain records",
        source_node_id="point-1",
        source_text=(
            "Reporting body shall retain records."
        ),
        language=LanguageCode("en"),
    )
    graph = EurLexRequirementsGraph(
        requirements=(requirement,)
    )
    rules = EurLexComplianceRules(
        rules=(
            EurLexComplianceRule(
                rule_id="rule-1",
                kind=(
                    EurLexComplianceRuleKind
                    .REQUIREMENT
                ),
                subject="reporting body",
                action="retain records",
                source_requirement_id=(
                    "requirement-1"
                ),
                source_node_id="point-1",
                source_text=(
                    "Reporting body shall retain "
                    "records."
                ),
                language=LanguageCode("en"),
            ),
        )
    )

    actors = EurLexLegalActorExtractor().extract(
        graph=graph,
        rules=rules,
    )

    assert actors.actors[0].kind is (
        EurLexLegalActorKind.GENERIC_ACTOR
    )
