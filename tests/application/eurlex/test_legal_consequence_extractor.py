"""Tests for explicit EUR-Lex legal consequence extraction."""

from decimal import Decimal

import pytest

from eke.application.eurlex.compliance_rules import (
    EurLexComplianceRule,
    EurLexComplianceRuleKind,
    EurLexComplianceRules,
)
from eke.application.eurlex.legal_consequence_extractor import (
    EurLexLegalConsequenceExtractor,
)
from eke.application.eurlex.legal_consequences import (
    EurLexLegalConsequenceKind,
    EurLexLegalConsequenceModality,
)
from eke.application.eurlex.quantitative_thresholds import (
    EurLexQuantitativeComparator,
    EurLexQuantitativeThreshold,
    EurLexQuantitativeThresholds,
    EurLexQuantitativeUnitKind,
)
from eke.application.eurlex.rule_qualifiers import (
    EurLexRuleQualifier,
    EurLexRuleQualifierKind,
    EurLexRuleQualifierMarker,
    EurLexRuleQualifiers,
)
from eke.application.eurlex.temporal_constraints import (
    EurLexTemporalConstraint,
    EurLexTemporalConstraintKind,
    EurLexTemporalConstraints,
    EurLexTemporalRelation,
    EurLexTemporalUnit,
)
from eke.domain.localization import LanguageCode


def _rule(
    *,
    rule_id: str = "rule-1",
    requirement_id: str = "requirement-1",
    source_node_id: str = "point-1",
    source_text: str,
) -> EurLexComplianceRule:
    return EurLexComplianceRule(
        rule_id=rule_id,
        kind=(
            EurLexComplianceRuleKind
            .REQUIREMENT
        ),
        subject="institution",
        action="apply the consequence",
        source_requirement_id=requirement_id,
        source_node_id=source_node_id,
        source_text=source_text,
        language=LanguageCode("en"),
    )


def _qualifier(
    *,
    qualifier_id: str = "qualifier-1",
    rule_id: str = "rule-1",
    requirement_id: str = "requirement-1",
    source_node_id: str = "point-1",
    text: str,
    source_text: str,
) -> EurLexRuleQualifier:
    return EurLexRuleQualifier(
        qualifier_id=qualifier_id,
        kind=EurLexRuleQualifierKind.CONDITION,
        marker=EurLexRuleQualifierMarker.IF,
        text=text,
        source_rule_id=rule_id,
        source_requirement_id=requirement_id,
        source_node_id=source_node_id,
        source_text=source_text,
    )


def _threshold(
    *,
    threshold_id: str = "threshold-1",
    rule_id: str = "rule-1",
    requirement_id: str = "requirement-1",
    source_node_id: str = "point-1",
    text: str = "at least EUR 5 000",
    source_text: str = (
        "The person shall be subject to a fine "
        "of at least EUR 5 000."
    ),
    source_qualifier_id: str | None = None,
) -> EurLexQuantitativeThreshold:
    return EurLexQuantitativeThreshold(
        threshold_id=threshold_id,
        comparator=(
            EurLexQuantitativeComparator
            .GREATER_THAN_OR_EQUAL_TO
        ),
        text=text,
        source_rule_id=rule_id,
        source_requirement_id=requirement_id,
        source_node_id=source_node_id,
        source_text=source_text,
        value=Decimal("5000"),
        unit_text="EUR",
        unit_kind=(
            EurLexQuantitativeUnitKind.CURRENCY
        ),
        currency_code="EUR",
        source_qualifier_id=source_qualifier_id,
    )


def _temporal_constraint(
    *,
    constraint_id: str = "temporal-1",
    rule_id: str = "rule-1",
    requirement_id: str = "requirement-1",
    source_node_id: str = "point-1",
    text: str = "within 30 days",
    source_text: str = (
        "The person shall be subject to a fine "
        "within 30 days."
    ),
    source_qualifier_id: str | None = None,
) -> EurLexTemporalConstraint:
    return EurLexTemporalConstraint(
        constraint_id=constraint_id,
        kind=(
            EurLexTemporalConstraintKind
            .RELATIVE_OFFSET
        ),
        relation=EurLexTemporalRelation.WITHIN,
        text=text,
        source_rule_id=rule_id,
        source_requirement_id=requirement_id,
        source_node_id=source_node_id,
        source_text=source_text,
        quantity=30,
        unit=EurLexTemporalUnit.DAY,
        source_qualifier_id=source_qualifier_id,
    )


def _extract(
    *,
    rule_text: str,
    qualifiers: EurLexRuleQualifiers | None = None,
    thresholds: EurLexQuantitativeThresholds | None = None,
    temporal_constraints: EurLexTemporalConstraints | None = None,
):
    return EurLexLegalConsequenceExtractor().extract(
        rules=EurLexComplianceRules(
            rules=(
                _rule(source_text=rule_text),
            )
        ),
        qualifiers=(
            qualifiers
            if qualifiers is not None
            else EurLexRuleQualifiers()
        ),
        thresholds=(
            thresholds
            if thresholds is not None
            else EurLexQuantitativeThresholds()
        ),
        temporal_constraints=(
            temporal_constraints
            if temporal_constraints is not None
            else EurLexTemporalConstraints()
        ),
    )


@pytest.mark.parametrize(
    (
        "text",
        "expected_kind",
        "expected_modality",
    ),
    (
        (
            "The person shall be subject to a fine.",
            EurLexLegalConsequenceKind.FINE,
            EurLexLegalConsequenceModality.MANDATORY,
        ),
        (
            "The undertaking may be liable to "
            "an administrative penalty.",
            (
                EurLexLegalConsequenceKind
                .ADMINISTRATIVE_PENALTY
            ),
            EurLexLegalConsequenceModality.PERMITTED,
        ),
        (
            "The person could be subject to "
            "a criminal penalty.",
            (
                EurLexLegalConsequenceKind
                .CRIMINAL_PENALTY
            ),
            EurLexLegalConsequenceModality.POSSIBLE,
        ),
        (
            "The authority must impose a fine.",
            EurLexLegalConsequenceKind.FINE,
            EurLexLegalConsequenceModality.MANDATORY,
        ),
        (
            "Member States shall impose penalties.",
            (
                EurLexLegalConsequenceKind
                .ADMINISTRATIVE_PENALTY
            ),
            EurLexLegalConsequenceModality.MANDATORY,
        ),
    ),
)
def test_extracts_penalty_formulations(
    text: str,
    expected_kind: EurLexLegalConsequenceKind,
    expected_modality: EurLexLegalConsequenceModality,
) -> None:
    consequences = _extract(
        rule_text=text
    )

    assert len(consequences.consequences) == 1
    consequence = consequences.consequences[0]
    assert consequence.kind is expected_kind
    assert consequence.modality is expected_modality


@pytest.mark.parametrize(
    (
        "text",
        "expected_kind",
        "expected_action",
    ),
    (
        (
            "The authorisation shall be suspended.",
            EurLexLegalConsequenceKind.SUSPENSION,
            "suspended",
        ),
        (
            "The licence shall be revoked.",
            EurLexLegalConsequenceKind.REVOCATION,
            "revoked",
        ),
        (
            "The authorisation may be withdrawn.",
            EurLexLegalConsequenceKind.WITHDRAWAL,
            "withdrawn",
        ),
        (
            "The application shall be rejected.",
            EurLexLegalConsequenceKind.REJECTION,
            "rejected",
        ),
        (
            "The amount shall be recovered.",
            EurLexLegalConsequenceKind.RECOVERY,
            "recovered",
        ),
        (
            "The licence can be invalidated.",
            EurLexLegalConsequenceKind.INVALIDATION,
            "invalidated",
        ),
    ),
)
def test_extracts_passive_legal_consequences(
    text: str,
    expected_kind: EurLexLegalConsequenceKind,
    expected_action: str,
) -> None:
    consequences = _extract(
        rule_text=text
    )

    assert len(consequences.consequences) == 1
    consequence = consequences.consequences[0]
    assert consequence.kind is expected_kind
    assert expected_action in consequence.action_text


def test_extracts_cease_to_be_valid() -> None:
    consequences = _extract(
        rule_text=(
            "The authorisation shall cease "
            "to be valid."
        )
    )

    assert len(consequences.consequences) == 1
    consequence = consequences.consequences[0]
    assert consequence.kind is (
        EurLexLegalConsequenceKind.INVALIDATION
    )
    assert consequence.modality is (
        EurLexLegalConsequenceModality.MANDATORY
    )
    assert consequence.action_text == (
        "cease to be valid"
    )


def test_extracts_rules_on_penalties() -> None:
    consequences = _extract(
        rule_text=(
            "Member States shall lay down "
            "rules on penalties applicable "
            "to infringements."
        )
    )

    assert len(consequences.consequences) == 1
    consequence = consequences.consequences[0]
    assert consequence.kind is (
        EurLexLegalConsequenceKind
        .ADMINISTRATIVE_PENALTY
    )
    assert consequence.modality is (
        EurLexLegalConsequenceModality.MANDATORY
    )
    assert "lay down" in consequence.action_text


def test_preserves_subject_action_and_source_text() -> None:
    text = (
        "The applicant shall be subject to "
        "a fine of at least EUR 5 000."
    )
    consequences = _extract(
        rule_text=text
    )

    consequence = consequences.consequences[0]
    assert consequence.subject_text == (
        "The applicant"
    )
    assert "a fine" in consequence.action_text
    assert consequence.source_rule_id == "rule-1"
    assert consequence.source_requirement_id == (
        "requirement-1"
    )
    assert consequence.source_node_id == "point-1"
    assert consequence.source_text == text


def test_links_quantitative_threshold_in_same_text() -> None:
    text = (
        "The person shall be subject to a fine "
        "of at least EUR 5 000."
    )
    thresholds = EurLexQuantitativeThresholds(
        thresholds=(
            _threshold(
                text="at least EUR 5 000",
                source_text=text,
            ),
        )
    )

    consequences = _extract(
        rule_text=text,
        thresholds=thresholds,
    )

    assert consequences.consequences[
        0
    ].quantitative_threshold_ids == (
        "threshold-1",
    )


def test_links_temporal_constraint_in_same_text() -> None:
    text = (
        "The person shall be subject to a fine "
        "within 30 days."
    )
    temporal_constraints = (
        EurLexTemporalConstraints(
            constraints=(
                _temporal_constraint(
                    text="within 30 days",
                    source_text=text,
                ),
            )
        )
    )

    consequences = _extract(
        rule_text=text,
        temporal_constraints=(
            temporal_constraints
        ),
    )

    assert consequences.consequences[
        0
    ].temporal_constraint_ids == (
        "temporal-1",
    )


def test_does_not_link_threshold_outside_consequence_text() -> None:
    text = (
        "The person shall maintain at least "
        "EUR 5 000. The licence shall be revoked."
    )
    thresholds = EurLexQuantitativeThresholds(
        thresholds=(
            _threshold(
                text="at least EUR 5 000",
                source_text=text,
            ),
        )
    )

    consequences = _extract(
        rule_text=text,
        thresholds=thresholds,
    )

    assert len(consequences.consequences) == 1
    assert (
        consequences.consequences[
            0
        ].quantitative_threshold_ids
        == ()
    )


def test_does_not_link_temporal_constraint_outside_text() -> None:
    text = (
        "The person shall report within 30 days. "
        "The licence shall be revoked."
    )
    temporal_constraints = (
        EurLexTemporalConstraints(
            constraints=(
                _temporal_constraint(
                    text="within 30 days",
                    source_text=text,
                ),
            )
        )
    )

    consequences = _extract(
        rule_text=text,
        temporal_constraints=(
            temporal_constraints
        ),
    )

    assert len(consequences.consequences) == 1
    assert (
        consequences.consequences[
            0
        ].temporal_constraint_ids
        == ()
    )


def test_prefers_qualifier_provenance_over_rule_duplicate() -> None:
    source_text = (
        "If the applicant may be subject to "
        "a fine, the authority shall notify it."
    )
    qualifier = _qualifier(
        text=(
            "the applicant may be subject to "
            "a fine"
        ),
        source_text=source_text,
    )

    consequences = _extract(
        rule_text=source_text,
        qualifiers=EurLexRuleQualifiers(
            qualifiers=(qualifier,)
        ),
    )

    assert len(consequences.consequences) == 1
    consequence = consequences.consequences[0]
    assert consequence.source_qualifier_id == (
        "qualifier-1"
    )
    assert consequence.source_rule_id == "rule-1"


def test_preserves_distinct_rule_and_qualifier_consequences() -> None:
    source_text = (
        "If the applicant may be subject to a fine, "
        "the licence shall be revoked."
    )
    qualifier = _qualifier(
        text=(
            "the applicant may be subject to a fine"
        ),
        source_text=source_text,
    )

    consequences = _extract(
        rule_text=source_text,
        qualifiers=EurLexRuleQualifiers(
            qualifiers=(qualifier,)
        ),
    )

    assert len(consequences.consequences) == 2
    assert consequences.consequences[0].kind is (
        EurLexLegalConsequenceKind.REVOCATION
    )
    assert (
        consequences.consequences[
            0
        ].source_qualifier_id
        is None
    )
    assert consequences.consequences[1].kind is (
        EurLexLegalConsequenceKind.FINE
    )
    assert consequences.consequences[
        1
    ].source_qualifier_id == "qualifier-1"


def test_links_qualifier_threshold_and_temporal_constraint() -> None:
    source_text = (
        "If the applicant may be subject to a fine "
        "of at least EUR 5 000 within 30 days, "
        "the authority shall notify it."
    )
    qualifier = _qualifier(
        text=(
            "the applicant may be subject to a fine "
            "of at least EUR 5 000 within 30 days"
        ),
        source_text=source_text,
    )
    thresholds = EurLexQuantitativeThresholds(
        thresholds=(
            _threshold(
                text="at least EUR 5 000",
                source_text=source_text,
                source_qualifier_id="qualifier-1",
            ),
        )
    )
    temporal_constraints = EurLexTemporalConstraints(
        constraints=(
            _temporal_constraint(
                text="within 30 days",
                source_text=source_text,
                source_qualifier_id="qualifier-1",
            ),
        )
    )

    consequences = _extract(
        rule_text=source_text,
        qualifiers=EurLexRuleQualifiers(
            qualifiers=(qualifier,)
        ),
        thresholds=thresholds,
        temporal_constraints=(
            temporal_constraints
        ),
    )

    consequence = consequences.consequences[0]
    assert consequence.source_qualifier_id == (
        "qualifier-1"
    )
    assert consequence.quantitative_threshold_ids == (
        "threshold-1",
    )
    assert consequence.temporal_constraint_ids == (
        "temporal-1",
    )


def test_returns_empty_when_no_explicit_consequence() -> None:
    consequences = _extract(
        rule_text=(
            "The institution shall maintain "
            "appropriate records."
        )
    )

    assert consequences.consequences == ()


def test_ignores_non_modal_penalty_reference() -> None:
    consequences = _extract(
        rule_text=(
            "The report describes penalties "
            "used in other jurisdictions."
        )
    )

    assert consequences.consequences == ()


def test_rejects_qualifier_for_missing_rule() -> None:
    qualifier = _qualifier(
        rule_id="missing-rule",
        text=(
            "the applicant may be subject "
            "to a fine"
        ),
        source_text=(
            "If the applicant may be subject "
            "to a fine, it shall report."
        ),
    )

    with pytest.raises(
        ValueError,
        match="existing rules",
    ):
        EurLexLegalConsequenceExtractor().extract(
            rules=EurLexComplianceRules(),
            qualifiers=EurLexRuleQualifiers(
                qualifiers=(qualifier,)
            ),
            thresholds=(
                EurLexQuantitativeThresholds()
            ),
            temporal_constraints=(
                EurLexTemporalConstraints()
            ),
        )


def test_rejects_qualifier_requirement_mismatch() -> None:
    rule = _rule(
        source_text=(
            "The person shall be subject "
            "to a fine."
        )
    )
    qualifier = _qualifier(
        requirement_id="requirement-2",
        text=(
            "the person shall be subject "
            "to a fine"
        ),
        source_text=rule.source_text,
    )

    with pytest.raises(
        ValueError,
        match="requirement must match",
    ):
        EurLexLegalConsequenceExtractor().extract(
            rules=EurLexComplianceRules(
                rules=(rule,)
            ),
            qualifiers=EurLexRuleQualifiers(
                qualifiers=(qualifier,)
            ),
            thresholds=(
                EurLexQuantitativeThresholds()
            ),
            temporal_constraints=(
                EurLexTemporalConstraints()
            ),
        )


def test_rejects_threshold_for_missing_rule() -> None:
    threshold = _threshold(
        rule_id="missing-rule",
    )

    with pytest.raises(
        ValueError,
        match="thresholds must reference",
    ):
        EurLexLegalConsequenceExtractor().extract(
            rules=EurLexComplianceRules(),
            qualifiers=EurLexRuleQualifiers(),
            thresholds=(
                EurLexQuantitativeThresholds(
                    thresholds=(threshold,)
                )
            ),
            temporal_constraints=(
                EurLexTemporalConstraints()
            ),
        )


def test_rejects_threshold_requirement_mismatch() -> None:
    rule = _rule(
        source_text=(
            "The person shall be subject "
            "to a fine."
        )
    )
    threshold = _threshold(
        requirement_id="requirement-2",
    )

    with pytest.raises(
        ValueError,
        match="threshold requirement must match",
    ):
        EurLexLegalConsequenceExtractor().extract(
            rules=EurLexComplianceRules(
                rules=(rule,)
            ),
            qualifiers=EurLexRuleQualifiers(),
            thresholds=(
                EurLexQuantitativeThresholds(
                    thresholds=(threshold,)
                )
            ),
            temporal_constraints=(
                EurLexTemporalConstraints()
            ),
        )


def test_rejects_temporal_constraint_for_missing_rule() -> None:
    constraint = _temporal_constraint(
        rule_id="missing-rule",
    )

    with pytest.raises(
        ValueError,
        match="temporal constraints must reference",
    ):
        EurLexLegalConsequenceExtractor().extract(
            rules=EurLexComplianceRules(),
            qualifiers=EurLexRuleQualifiers(),
            thresholds=(
                EurLexQuantitativeThresholds()
            ),
            temporal_constraints=(
                EurLexTemporalConstraints(
                    constraints=(constraint,)
                )
            ),
        )


def test_rejects_temporal_requirement_mismatch() -> None:
    rule = _rule(
        source_text=(
            "The person shall be subject "
            "to a fine."
        )
    )
    constraint = _temporal_constraint(
        requirement_id="requirement-2",
    )

    with pytest.raises(
        ValueError,
        match=(
            "temporal constraint requirement "
            "must match"
        ),
    ):
        EurLexLegalConsequenceExtractor().extract(
            rules=EurLexComplianceRules(
                rules=(rule,)
            ),
            qualifiers=EurLexRuleQualifiers(),
            thresholds=(
                EurLexQuantitativeThresholds()
            ),
            temporal_constraints=(
                EurLexTemporalConstraints(
                    constraints=(constraint,)
                )
            ),
        )


def test_extractor_is_deterministic() -> None:
    text = (
        "The applicant shall be subject "
        "to a fine."
    )
    extractor = EurLexLegalConsequenceExtractor()
    kwargs = dict(
        rules=EurLexComplianceRules(
            rules=(
                _rule(source_text=text),
            )
        ),
        qualifiers=EurLexRuleQualifiers(),
        thresholds=EurLexQuantitativeThresholds(),
        temporal_constraints=(
            EurLexTemporalConstraints()
        ),
    )

    first = extractor.extract(**kwargs)
    second = extractor.extract(**kwargs)

    assert first == second
    assert (
        first.consequences[0].consequence_id
        == second.consequences[0].consequence_id
    )
