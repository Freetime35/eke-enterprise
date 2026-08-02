"""Extract explicit legal consequences from EUR-Lex rules."""

from __future__ import annotations

import re
from dataclasses import dataclass
from hashlib import sha256

from eke.application.eurlex.compliance_rules import (
    EurLexComplianceRule,
    EurLexComplianceRules,
)
from eke.application.eurlex.legal_consequences import (
    EurLexLegalConsequence,
    EurLexLegalConsequenceKind,
    EurLexLegalConsequenceModality,
    EurLexLegalConsequences,
    normalize_legal_consequences,
)
from eke.application.eurlex.quantitative_thresholds import (
    EurLexQuantitativeThresholds,
)
from eke.application.eurlex.rule_qualifiers import (
    EurLexRuleQualifier,
    EurLexRuleQualifiers,
)
from eke.application.eurlex.temporal_constraints import (
    EurLexTemporalConstraints,
)


@dataclass(frozen=True, slots=True)
class _ConsequenceMatch:
    """Represent one parsed explicit consequence."""

    start: int
    end: int
    text: str
    action_text: str
    kind: EurLexLegalConsequenceKind
    modality: EurLexLegalConsequenceModality
    subject_text: str | None = None


_MANDATORY_MODALITY_PATTERN = (
    r"(?:shall|must)"
)

_PERMITTED_MODALITY_PATTERN = (
    r"(?:may)"
)

_POSSIBLE_MODALITY_PATTERN = (
    r"(?:can|could)"
)

_SUBJECT_PATTERN = (
    r"(?P<subject>"
    r"(?:the\s+)?"
    r"(?:"
    r"person"
    r"|persons"
    r"|undertaking"
    r"|undertakings"
    r"|institution"
    r"|institutions"
    r"|operator"
    r"|operators"
    r"|applicant"
    r"|applicants"
    r"|holder"
    r"|holders"
    r"|licensee"
    r"|licensees"
    r"|Member\s+State"
    r"|Member\s+States"
    r"|competent\s+authority"
    r"|competent\s+authorities"
    r"|authority"
    r"|authorities"
    r"|application"
    r"|applications"
    r"|authorisation"
    r"|authorisations"
    r"|authorization"
    r"|authorizations"
    r"|licence"
    r"|licences"
    r"|license"
    r"|licenses"
    r"|amount"
    r"|amounts"
    r")"
    r")"
)

_ACTION_TAIL_PATTERN = (
    r"(?P<tail>"
    r"[^,.;:]*"
    r")"
)

_SUBJECT_TO_PATTERN = re.compile(
    rf"""
    \b
    {_SUBJECT_PATTERN}
    \s+
    (?P<modal>{_MANDATORY_MODALITY_PATTERN}
        |{_PERMITTED_MODALITY_PATTERN}
        |{_POSSIBLE_MODALITY_PATTERN})
    \s+
    be
    \s+
    (?:
        subject\s+to
        |
        liable\s+to
    )
    \s+
    (?P<consequence>
        an?\s+administrative\s+penalt(?:y|ies)
        |
        an?\s+criminal\s+penalt(?:y|ies)
        |
        an?\s+fine
        |
        fines
        |
        penalties
        |
        a\s+penalty
    )
    {_ACTION_TAIL_PATTERN}
    """,
    re.IGNORECASE | re.VERBOSE,
)

_IMPOSE_PATTERN = re.compile(
    rf"""
    \b
    {_SUBJECT_PATTERN}
    \s+
    (?P<modal>{_MANDATORY_MODALITY_PATTERN}
        |{_PERMITTED_MODALITY_PATTERN}
        |{_POSSIBLE_MODALITY_PATTERN})
    \s+
    impose
    \s+
    (?P<consequence>
        an?\s+administrative\s+penalt(?:y|ies)
        |
        an?\s+criminal\s+penalt(?:y|ies)
        |
        an?\s+fine
        |
        fines
        |
        penalties
        |
        a\s+penalty
    )
    {_ACTION_TAIL_PATTERN}
    """,
    re.IGNORECASE | re.VERBOSE,
)

_PASSIVE_ACTION_PATTERN = re.compile(
    rf"""
    \b
    {_SUBJECT_PATTERN}
    \s+
    (?P<modal>{_MANDATORY_MODALITY_PATTERN}
        |{_PERMITTED_MODALITY_PATTERN}
        |{_POSSIBLE_MODALITY_PATTERN})
    \s+
    be
    \s+
    (?P<action>
        suspended
        |
        revoked
        |
        withdrawn
        |
        rejected
        |
        recovered
        |
        invalidated
    )
    {_ACTION_TAIL_PATTERN}
    """,
    re.IGNORECASE | re.VERBOSE,
)

_CEASE_VALID_PATTERN = re.compile(
    rf"""
    \b
    {_SUBJECT_PATTERN}
    \s+
    (?P<modal>{_MANDATORY_MODALITY_PATTERN}
        |{_PERMITTED_MODALITY_PATTERN}
        |{_POSSIBLE_MODALITY_PATTERN})
    \s+
    cease
    \s+
    to
    \s+
    be
    \s+
    valid
    {_ACTION_TAIL_PATTERN}
    """,
    re.IGNORECASE | re.VERBOSE,
)

_EFFECTIVE_PENALTIES_PATTERN = re.compile(
    rf"""
    \b
    {_SUBJECT_PATTERN}
    \s+
    (?P<modal>{_MANDATORY_MODALITY_PATTERN}
        |{_PERMITTED_MODALITY_PATTERN}
        |{_POSSIBLE_MODALITY_PATTERN})
    \s+
    (?P<action>
        lay\s+down
        |
        provide\s+for
        |
        establish
        |
        adopt
    )
    \s+
    (?P<consequence>
        penalties
        |
        rules\s+on\s+penalties
    )
    {_ACTION_TAIL_PATTERN}
    """,
    re.IGNORECASE | re.VERBOSE,
)


class EurLexLegalConsequenceExtractor:
    """Extract explicit legal consequences from rules."""

    def extract(
        self,
        *,
        rules: EurLexComplianceRules,
        qualifiers: EurLexRuleQualifiers,
        thresholds: EurLexQuantitativeThresholds,
        temporal_constraints: EurLexTemporalConstraints,
    ) -> EurLexLegalConsequences:
        """Extract source-backed legal consequences."""
        if not isinstance(
            rules,
            EurLexComplianceRules,
        ):
            raise TypeError(
                "rules must be an "
                "EurLexComplianceRules"
            )

        if not isinstance(
            qualifiers,
            EurLexRuleQualifiers,
        ):
            raise TypeError(
                "qualifiers must be an "
                "EurLexRuleQualifiers"
            )

        if not isinstance(
            thresholds,
            EurLexQuantitativeThresholds,
        ):
            raise TypeError(
                "thresholds must be an "
                "EurLexQuantitativeThresholds"
            )

        if not isinstance(
            temporal_constraints,
            EurLexTemporalConstraints,
        ):
            raise TypeError(
                "temporal_constraints must be an "
                "EurLexTemporalConstraints"
            )

        rules_by_id = {
            rule.rule_id: rule
            for rule in rules.rules
        }

        _validate_qualifiers(
            qualifiers=qualifiers,
            rules_by_id=rules_by_id,
        )
        _validate_thresholds(
            thresholds=thresholds,
            rules_by_id=rules_by_id,
        )
        _validate_temporal_constraints(
            temporal_constraints=temporal_constraints,
            rules_by_id=rules_by_id,
        )

        qualifier_texts_by_rule: dict[
            str,
            tuple[str, ...],
        ] = {}

        for qualifier in qualifiers.qualifiers:
            existing = qualifier_texts_by_rule.get(
                qualifier.source_rule_id,
                (),
            )
            qualifier_texts_by_rule[
                qualifier.source_rule_id
            ] = (
                *existing,
                qualifier.text.casefold(),
            )

        consequences: list[
            EurLexLegalConsequence
        ] = []

        for rule in rules.rules:
            qualifier_texts = (
                qualifier_texts_by_rule.get(
                    rule.rule_id,
                    (),
                )
            )

            for parsed in _extract_matches(
                rule.source_text
            ):
                if any(
                    parsed.text.casefold()
                    in qualifier_text
                    for qualifier_text
                    in qualifier_texts
                ):
                    continue

                consequences.append(
                    _consequence_from_rule_match(
                        rule=rule,
                        parsed=parsed,
                        thresholds=thresholds,
                        temporal_constraints=(
                            temporal_constraints
                        ),
                    )
                )

        for qualifier in qualifiers.qualifiers:
            rule = rules_by_id[
                qualifier.source_rule_id
            ]

            for parsed in _extract_matches(
                qualifier.text
            ):
                consequences.append(
                    _consequence_from_qualifier_match(
                        rule=rule,
                        qualifier=qualifier,
                        parsed=parsed,
                        thresholds=thresholds,
                        temporal_constraints=(
                            temporal_constraints
                        ),
                    )
                )

        return normalize_legal_consequences(
            tuple(consequences)
        )


def _extract_matches(
    text: str,
) -> tuple[_ConsequenceMatch, ...]:
    if not isinstance(text, str):
        raise TypeError(
            "text must be a string"
        )

    matches: list[_ConsequenceMatch] = []

    for pattern in (
        _SUBJECT_TO_PATTERN,
        _IMPOSE_PATTERN,
        _EFFECTIVE_PENALTIES_PATTERN,
    ):
        for match in pattern.finditer(text):
            consequence_text = (
                match.groupdict().get(
                    "consequence"
                )
                or ""
            )
            tail = (
                match.groupdict().get("tail")
                or ""
            )
            action = (
                match.groupdict().get("action")
                or consequence_text
            )
            matches.append(
                _ConsequenceMatch(
                    start=match.start(),
                    end=match.end(),
                    text=_normalize_match_text(
                        match.group(0)
                    ),
                    action_text=(
                        _normalize_match_text(
                            f"{action} {tail}"
                        )
                    ),
                    kind=_classify_penalty_kind(
                        consequence_text
                    ),
                    modality=_parse_modality(
                        match.group("modal")
                    ),
                    subject_text=(
                        _normalize_match_text(
                            match.group("subject")
                        )
                    ),
                )
            )

    for match in _PASSIVE_ACTION_PATTERN.finditer(
        text
    ):
        action = _normalize_match_text(
            match.group("action")
        )
        tail = (
            match.groupdict().get("tail")
            or ""
        )
        matches.append(
            _ConsequenceMatch(
                start=match.start(),
                end=match.end(),
                text=_normalize_match_text(
                    match.group(0)
                ),
                action_text=_normalize_match_text(
                    f"{action} {tail}"
                ),
                kind=_classify_passive_action(
                    action
                ),
                modality=_parse_modality(
                    match.group("modal")
                ),
                subject_text=(
                    _normalize_match_text(
                        match.group("subject")
                    )
                ),
            )
        )

    for match in _CEASE_VALID_PATTERN.finditer(
        text
    ):
        tail = (
            match.groupdict().get("tail")
            or ""
        )
        matches.append(
            _ConsequenceMatch(
                start=match.start(),
                end=match.end(),
                text=_normalize_match_text(
                    match.group(0)
                ),
                action_text=_normalize_match_text(
                    f"cease to be valid {tail}"
                ),
                kind=(
                    EurLexLegalConsequenceKind
                    .INVALIDATION
                ),
                modality=_parse_modality(
                    match.group("modal")
                ),
                subject_text=(
                    _normalize_match_text(
                        match.group("subject")
                    )
                ),
            )
        )

    return _remove_overlapping_matches(
        tuple(matches)
    )


def _remove_overlapping_matches(
    matches: tuple[_ConsequenceMatch, ...],
) -> tuple[_ConsequenceMatch, ...]:
    ordered = sorted(
        matches,
        key=lambda match: (
            match.start,
            -(match.end - match.start),
            match.kind.value,
        ),
    )

    accepted: list[_ConsequenceMatch] = []

    for candidate in ordered:
        if any(
            _matches_overlap(
                candidate,
                existing,
            )
            for existing in accepted
        ):
            continue

        accepted.append(candidate)

    return tuple(
        sorted(
            accepted,
            key=lambda match: (
                match.start,
                match.end,
                match.kind.value,
            ),
        )
    )


def _matches_overlap(
    left: _ConsequenceMatch,
    right: _ConsequenceMatch,
) -> bool:
    return (
        left.start < right.end
        and right.start < left.end
    )


def _classify_penalty_kind(
    value: str,
) -> EurLexLegalConsequenceKind:
    normalized = value.casefold()

    if "administrative" in normalized:
        return (
            EurLexLegalConsequenceKind
            .ADMINISTRATIVE_PENALTY
        )
    if "criminal" in normalized:
        return (
            EurLexLegalConsequenceKind
            .CRIMINAL_PENALTY
        )
    if "fine" in normalized:
        return EurLexLegalConsequenceKind.FINE
    if "penalt" in normalized:
        return (
            EurLexLegalConsequenceKind
            .ADMINISTRATIVE_PENALTY
        )

    return EurLexLegalConsequenceKind.OTHER


def _classify_passive_action(
    value: str,
) -> EurLexLegalConsequenceKind:
    normalized = value.casefold()

    mapping = {
        "suspended": (
            EurLexLegalConsequenceKind.SUSPENSION
        ),
        "revoked": (
            EurLexLegalConsequenceKind.REVOCATION
        ),
        "withdrawn": (
            EurLexLegalConsequenceKind.WITHDRAWAL
        ),
        "rejected": (
            EurLexLegalConsequenceKind.REJECTION
        ),
        "recovered": (
            EurLexLegalConsequenceKind.RECOVERY
        ),
        "invalidated": (
            EurLexLegalConsequenceKind.INVALIDATION
        ),
    }

    return mapping.get(
        normalized,
        EurLexLegalConsequenceKind.OTHER,
    )


def _parse_modality(
    value: str,
) -> EurLexLegalConsequenceModality:
    normalized = value.casefold()

    if normalized in {"shall", "must"}:
        return (
            EurLexLegalConsequenceModality
            .MANDATORY
        )
    if normalized == "may":
        return (
            EurLexLegalConsequenceModality
            .PERMITTED
        )
    if normalized in {"can", "could"}:
        return (
            EurLexLegalConsequenceModality
            .POSSIBLE
        )

    raise ValueError(
        "unsupported legal consequence modality"
    )


def _consequence_from_rule_match(
    *,
    rule: EurLexComplianceRule,
    parsed: _ConsequenceMatch,
    thresholds: EurLexQuantitativeThresholds,
    temporal_constraints: EurLexTemporalConstraints,
) -> EurLexLegalConsequence:
    return EurLexLegalConsequence(
        consequence_id=_stable_consequence_id(
            source_rule_id=rule.rule_id,
            source_qualifier_id=None,
            parsed=parsed,
        ),
        kind=parsed.kind,
        modality=parsed.modality,
        text=parsed.text,
        action_text=parsed.action_text,
        subject_text=parsed.subject_text,
        source_rule_id=rule.rule_id,
        source_requirement_id=(
            rule.source_requirement_id
        ),
        source_node_id=rule.source_node_id,
        source_text=rule.source_text,
        quantitative_threshold_ids=(
            _threshold_ids_for_text(
                source_rule_id=rule.rule_id,
                source_qualifier_id=None,
                text=parsed.text,
                thresholds=thresholds,
            )
        ),
        temporal_constraint_ids=(
            _temporal_constraint_ids_for_text(
                source_rule_id=rule.rule_id,
                source_qualifier_id=None,
                text=parsed.text,
                temporal_constraints=(
                    temporal_constraints
                ),
            )
        ),
    )


def _consequence_from_qualifier_match(
    *,
    rule: EurLexComplianceRule,
    qualifier: EurLexRuleQualifier,
    parsed: _ConsequenceMatch,
    thresholds: EurLexQuantitativeThresholds,
    temporal_constraints: EurLexTemporalConstraints,
) -> EurLexLegalConsequence:
    return EurLexLegalConsequence(
        consequence_id=_stable_consequence_id(
            source_rule_id=rule.rule_id,
            source_qualifier_id=(
                qualifier.qualifier_id
            ),
            parsed=parsed,
        ),
        kind=parsed.kind,
        modality=parsed.modality,
        text=parsed.text,
        action_text=parsed.action_text,
        subject_text=parsed.subject_text,
        source_rule_id=rule.rule_id,
        source_requirement_id=(
            rule.source_requirement_id
        ),
        source_node_id=(
            qualifier.source_node_id
        ),
        source_text=qualifier.source_text,
        source_qualifier_id=(
            qualifier.qualifier_id
        ),
        quantitative_threshold_ids=(
            _threshold_ids_for_text(
                source_rule_id=rule.rule_id,
                source_qualifier_id=(
                    qualifier.qualifier_id
                ),
                text=parsed.text,
                thresholds=thresholds,
            )
        ),
        temporal_constraint_ids=(
            _temporal_constraint_ids_for_text(
                source_rule_id=rule.rule_id,
                source_qualifier_id=(
                    qualifier.qualifier_id
                ),
                text=parsed.text,
                temporal_constraints=(
                    temporal_constraints
                ),
            )
        ),
    )


def _threshold_ids_for_text(
    *,
    source_rule_id: str,
    source_qualifier_id: str | None,
    text: str,
    thresholds: EurLexQuantitativeThresholds,
) -> tuple[str, ...]:
    return tuple(
        threshold.threshold_id
        for threshold in thresholds.thresholds
        if (
            threshold.source_rule_id
            == source_rule_id
            and (
                threshold.source_qualifier_id
                == source_qualifier_id
            )
            and threshold.text.casefold()
            in text.casefold()
        )
    )


def _temporal_constraint_ids_for_text(
    *,
    source_rule_id: str,
    source_qualifier_id: str | None,
    text: str,
    temporal_constraints: EurLexTemporalConstraints,
) -> tuple[str, ...]:
    return tuple(
        constraint.constraint_id
        for constraint
        in temporal_constraints.constraints
        if (
            constraint.source_rule_id
            == source_rule_id
            and (
                constraint.source_qualifier_id
                == source_qualifier_id
            )
            and constraint.text.casefold()
            in text.casefold()
        )
    )


def _validate_qualifiers(
    *,
    qualifiers: EurLexRuleQualifiers,
    rules_by_id: dict[str, EurLexComplianceRule],
) -> None:
    for qualifier in qualifiers.qualifiers:
        rule = rules_by_id.get(
            qualifier.source_rule_id
        )
        if rule is None:
            raise ValueError(
                "qualifiers must reference "
                "existing rules"
            )

        if (
            qualifier.source_requirement_id
            != rule.source_requirement_id
        ):
            raise ValueError(
                "qualifier requirement must match "
                "its source rule"
            )


def _validate_thresholds(
    *,
    thresholds: EurLexQuantitativeThresholds,
    rules_by_id: dict[str, EurLexComplianceRule],
) -> None:
    for threshold in thresholds.thresholds:
        rule = rules_by_id.get(
            threshold.source_rule_id
        )
        if rule is None:
            raise ValueError(
                "thresholds must reference "
                "existing rules"
            )

        if (
            threshold.source_requirement_id
            != rule.source_requirement_id
        ):
            raise ValueError(
                "threshold requirement must match "
                "its source rule"
            )


def _validate_temporal_constraints(
    *,
    temporal_constraints: EurLexTemporalConstraints,
    rules_by_id: dict[str, EurLexComplianceRule],
) -> None:
    for constraint in (
        temporal_constraints.constraints
    ):
        rule = rules_by_id.get(
            constraint.source_rule_id
        )
        if rule is None:
            raise ValueError(
                "temporal constraints must reference "
                "existing rules"
            )

        if (
            constraint.source_requirement_id
            != rule.source_requirement_id
        ):
            raise ValueError(
                "temporal constraint requirement "
                "must match its source rule"
            )


def _stable_consequence_id(
    *,
    source_rule_id: str,
    source_qualifier_id: str | None,
    parsed: _ConsequenceMatch,
) -> str:
    digest = sha256(
        "\x1f".join(
            (
                source_rule_id,
                source_qualifier_id or "",
                parsed.kind.value,
                parsed.modality.value,
                str(parsed.start),
                parsed.text.casefold(),
            )
        ).encode("utf-8")
    ).hexdigest()[:16]

    return f"legal-consequence-{digest}"


def _normalize_match_text(
    value: str,
) -> str:
    return " ".join(value.split())
