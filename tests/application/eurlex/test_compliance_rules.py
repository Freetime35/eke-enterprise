"""Tests for EUR-Lex compliance-rule values."""

import pytest

from eke.application.eurlex import (
    EurLexComplianceRule,
    EurLexComplianceRuleKind,
    EurLexComplianceRules,
)
from eke.domain.localization import LanguageCode


def test_rule_normalizes_provenance_and_links() -> None:
    rule = EurLexComplianceRule(
        rule_id=" rule-1 ",
        kind=(
            EurLexComplianceRuleKind
            .REQUIREMENT
        ),
        subject=" credit   institution ",
        action=" submit   a report ",
        source_requirement_id=(
            " requirement-1 "
        ),
        source_node_id=" point-1 ",
        source_text=(
            "Credit institution shall submit "
            "a report."
        ),
        language=LanguageCode("en"),
        article_node_id=" article-20 ",
        paragraph_node_id=" paragraph-1 ",
        referenced_node_ids=(
            " article-12 ",
            "article-12",
        ),
        definition_ids=(
            " definition-1 ",
        ),
    )

    assert rule.subject == (
        "credit institution"
    )
    assert rule.referenced_node_ids == (
        "article-12",
    )
    assert rule.definition_ids == (
        "definition-1",
    )


def test_container_queries_rules() -> None:
    rule = EurLexComplianceRule(
        rule_id="rule-1",
        kind=(
            EurLexComplianceRuleKind
            .PROHIBITION
        ),
        subject="credit institution",
        action="alter records",
        source_requirement_id="requirement-1",
        source_node_id="point-1",
        source_text=(
            "Credit institution shall not "
            "alter records."
        ),
        language=LanguageCode("en"),
        article_node_id="article-20",
    )
    rules = EurLexComplianceRules(
        rules=(rule,)
    )

    assert rules.rule_by_id(
        "rule-1"
    ) == rule
    assert rules.rules_for_subject(
        "Credit Institution"
    ) == (rule,)
    assert rules.rules_for_article(
        "article-20"
    ) == (rule,)
    assert rules.rules_by_kind(
        EurLexComplianceRuleKind
        .PROHIBITION
    ) == (rule,)


def test_rejects_duplicate_source_requirement() -> None:
    first = EurLexComplianceRule(
        rule_id="rule-1",
        kind=(
            EurLexComplianceRuleKind
            .REQUIREMENT
        ),
        subject="institution",
        action="report",
        source_requirement_id="requirement-1",
        source_node_id="point-1",
        source_text="Institution shall report.",
        language=LanguageCode("en"),
    )
    second = EurLexComplianceRule(
        rule_id="rule-2",
        kind=(
            EurLexComplianceRuleKind
            .REQUIREMENT
        ),
        subject="institution",
        action="report",
        source_requirement_id="requirement-1",
        source_node_id="point-1",
        source_text="Institution shall report.",
        language=LanguageCode("en"),
    )

    with pytest.raises(
        ValueError,
        match="at most one rule",
    ):
        EurLexComplianceRules(
            rules=(first, second)
        )
