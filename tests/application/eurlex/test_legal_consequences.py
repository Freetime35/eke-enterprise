"""Tests for legal consequence models."""

from eke.application.eurlex.legal_consequences import (
    EurLexLegalConsequence,
    EurLexLegalConsequenceKind,
    EurLexLegalConsequenceModality,
    EurLexLegalConsequences,
    normalize_legal_consequences,
)


def _sample(
    **kwargs: object,
) -> EurLexLegalConsequence:
    data: dict[str, object] = {
        "consequence_id": "lc-1",
        "kind": EurLexLegalConsequenceKind.FINE,
        "modality": (
            EurLexLegalConsequenceModality.MANDATORY
        ),
        "text": "shall be subject to a fine",
        "action_text": "fine",
        "source_rule_id": "rule-1",
        "source_requirement_id": "req-1",
        "source_node_id": "node-1",
        "source_text": "shall be subject to a fine",
    }
    data.update(kwargs)
    return EurLexLegalConsequence(**data)  # type: ignore[arg-type]


def test_create_consequence() -> None:
    consequence = _sample()

    assert consequence.kind is (
        EurLexLegalConsequenceKind.FINE
    )
    assert consequence.modality is (
        EurLexLegalConsequenceModality.MANDATORY
    )


def test_normalize_deduplicates() -> None:
    consequence = _sample()

    normalized = normalize_legal_consequences(
        (
            consequence,
            consequence,
        )
    )

    assert normalized.consequences == (
        consequence,
    )


def test_lookup_helpers() -> None:
    consequence = _sample(
        quantitative_threshold_ids=("qt-1",),
        temporal_constraint_ids=("tc-1",),
    )
    collection = EurLexLegalConsequences(
        consequences=(consequence,)
    )

    assert collection.consequence_by_id(
        "lc-1"
    ) == consequence
    assert collection.consequences_for_rule(
        "rule-1"
    ) == (consequence,)
    assert collection.consequences_by_kind(
        EurLexLegalConsequenceKind.FINE
    ) == (consequence,)
    assert collection.consequences_by_modality(
        EurLexLegalConsequenceModality.MANDATORY
    ) == (consequence,)
    assert collection.consequences_for_threshold(
        "qt-1"
    ) == (consequence,)
    assert (
        collection
        .consequences_for_temporal_constraint(
            "tc-1"
        )
        == (consequence,)
    )
