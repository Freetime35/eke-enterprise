"""Tests for condition and exception extraction from rules."""

from eke.application.eurlex import (
    EurLexComplianceRule,
    EurLexComplianceRuleKind,
    EurLexComplianceRules,
    EurLexRequirementKind,
    EurLexRequirementNode,
    EurLexRequirementsGraph,
    EurLexRuleQualifierExtractor,
    EurLexRuleQualifierKind,
    EurLexRuleQualifierMarker,
)
from eke.domain.localization import LanguageCode


def _rule(
    *,
    rule_id: str,
    requirement_id: str,
    source_node_id: str,
    source_text: str,
    referenced_node_ids: tuple[str, ...] = (),
) -> EurLexComplianceRule:
    return EurLexComplianceRule(
        rule_id=rule_id,
        kind=(
            EurLexComplianceRuleKind
            .REQUIREMENT
        ),
        subject="institution",
        action="notify the authority",
        source_requirement_id=requirement_id,
        source_node_id=source_node_id,
        source_text=source_text,
        language=LanguageCode("en"),
        referenced_node_ids=(
            referenced_node_ids
        ),
    )


def test_extracts_explicit_leading_and_trailing_qualifiers() -> None:
    requirements = tuple(
        EurLexRequirementNode(
            requirement_id=(
                f"requirement-{index}"
            ),
            kind=EurLexRequirementKind.OBLIGATION,
            subject="institution",
            action="notify the authority",
            source_node_id=f"point-{index}",
            source_text=source_text,
            language=LanguageCode("en"),
        )
        for index, source_text in enumerate(
            (
                "If the threshold is exceeded, "
                "the institution shall notify.",
                "Unless otherwise provided, "
                "the institution shall notify.",
                "The institution shall notify, "
                "where Article 12 applies.",
                "The institution shall notify.",
            ),
            start=1,
        )
    )
    graph = EurLexRequirementsGraph(
        requirements=requirements
    )
    rules = EurLexComplianceRules(
        rules=(
            _rule(
                rule_id="rule-1",
                requirement_id="requirement-1",
                source_node_id="point-1",
                source_text=(
                    "If the threshold is exceeded, "
                    "the institution shall notify."
                ),
            ),
            _rule(
                rule_id="rule-2",
                requirement_id="requirement-2",
                source_node_id="point-2",
                source_text=(
                    "Unless otherwise provided, "
                    "the institution shall notify."
                ),
            ),
            _rule(
                rule_id="rule-3",
                requirement_id="requirement-3",
                source_node_id="point-3",
                source_text=(
                    "The institution shall notify, "
                    "where Article 12 applies."
                ),
                referenced_node_ids=(
                    "article-12",
                ),
            ),
            _rule(
                rule_id="rule-4",
                requirement_id="requirement-4",
                source_node_id="point-4",
                source_text=(
                    "The institution shall notify."
                ),
            ),
        )
    )

    qualifiers = (
        EurLexRuleQualifierExtractor()
        .extract(
            graph=graph,
            rules=rules,
        )
    )

    assert len(qualifiers.qualifiers) == 3

    first = qualifiers.qualifiers[0]
    assert first.kind is (
        EurLexRuleQualifierKind.CONDITION
    )
    assert first.marker is (
        EurLexRuleQualifierMarker.IF
    )
    assert first.text == (
        "the threshold is exceeded"
    )

    second = qualifiers.qualifiers[1]
    assert second.kind is (
        EurLexRuleQualifierKind.EXCEPTION
    )
    assert second.marker is (
        EurLexRuleQualifierMarker.UNLESS
    )

    third = qualifiers.qualifiers[2]
    assert third.marker is (
        EurLexRuleQualifierMarker.WHERE
    )
    assert third.referenced_node_ids == (
        "article-12",
    )


def test_extractor_is_deterministic() -> None:
    graph = EurLexRequirementsGraph()
    rules = EurLexComplianceRules()
    extractor = EurLexRuleQualifierExtractor()

    first = extractor.extract(
        graph=graph,
        rules=rules,
    )
    second = extractor.extract(
        graph=graph,
        rules=rules,
    )

    assert first == second
