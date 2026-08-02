"""Extract explicit temporal constraints from EUR-Lex rules."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from hashlib import sha256

from eke.application.eurlex.compliance_rules import (
    EurLexComplianceRule,
    EurLexComplianceRules,
)
from eke.application.eurlex.rule_qualifiers import (
    EurLexRuleQualifier,
    EurLexRuleQualifiers,
)
from eke.application.eurlex.temporal_constraints import (
    EurLexTemporalConstraint,
    EurLexTemporalConstraintKind,
    EurLexTemporalConstraints,
    EurLexTemporalRelation,
    EurLexTemporalUnit,
    normalize_temporal_constraints,
)

_MONTH_BY_NAME: dict[str, int] = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}

_NUMBER_BY_WORD: dict[str, int] = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
}

_UNIT_BY_TEXT: dict[str, EurLexTemporalUnit] = {
    "day": EurLexTemporalUnit.DAY,
    "days": EurLexTemporalUnit.DAY,
    "week": EurLexTemporalUnit.WEEK,
    "weeks": EurLexTemporalUnit.WEEK,
    "month": EurLexTemporalUnit.MONTH,
    "months": EurLexTemporalUnit.MONTH,
    "year": EurLexTemporalUnit.YEAR,
    "years": EurLexTemporalUnit.YEAR,
}

_NUMBER_PATTERN = (
    r"(?:"
    r"\d+"
    r"|one|two|three|four|five|six|seven|eight|nine"
    r"|ten|eleven|twelve|thirteen|fourteen|fifteen"
    r"|sixteen|seventeen|eighteen|nineteen"
    r"|twenty|thirty|forty|fifty|sixty|seventy"
    r"|eighty|ninety"
    r"|(?:twenty|thirty|forty|fifty|sixty|seventy|"
    r"eighty|ninety)[ -](?:one|two|three|four|five|"
    r"six|seven|eight|nine)"
    r")"
)

_UNIT_PATTERN = r"(?:days?|weeks?|months?|years?)"

_MONTH_PATTERN = (
    r"(?:"
    r"January|February|March|April|May|June|July|"
    r"August|September|October|November|December"
    r")"
)

_DATE_PATTERN = (
    rf"(?:"
    rf"\d{{4}}-\d{{2}}-\d{{2}}"
    rf"|"
    rf"\d{{1,2}}\s+{_MONTH_PATTERN}\s+\d{{4}}"
    rf")"
)

_ANCHOR_PATTERN = (
    r"(?:"
    r"the\s+)?"
    r"(?:"
    r"notification"
    r"|publication"
    r"|date\s+of\s+publication"
    r"|entry\s+into\s+force"
    r"|date\s+of\s+entry\s+into\s+force"
    r"|adoption"
    r"|date\s+of\s+adoption"
    r"|receipt"
    r"|date\s+of\s+receipt"
    r"|decision"
    r"|request"
    r"|application"
    r")"
)


@dataclass(frozen=True, slots=True)
class _TemporalMatch:
    """Represent one parsed temporal expression."""

    start: int
    end: int
    text: str
    kind: EurLexTemporalConstraintKind
    relation: EurLexTemporalRelation
    absolute_date: date | None = None
    quantity: int | None = None
    unit: EurLexTemporalUnit | None = None
    anchor_text: str | None = None


_QUANTIFIED_PATTERNS: tuple[
    tuple[
        EurLexTemporalConstraintKind,
        EurLexTemporalRelation,
        re.Pattern[str],
    ],
    ...,
] = (
    (
        EurLexTemporalConstraintKind.DURATION,
        EurLexTemporalRelation.FOR,
        re.compile(
            rf"""
            \b
            for\s+
            (?:a\s+period\s+of\s+)?
            (?P<quantity>{_NUMBER_PATTERN})
            \s+
            (?P<unit>{_UNIT_PATTERN})
            \b
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
    (
        EurLexTemporalConstraintKind.FREQUENCY,
        EurLexTemporalRelation.EVERY,
        re.compile(
            rf"""
            \b
            every\s+
            (?P<quantity>{_NUMBER_PATTERN})
            \s+
            (?P<unit>{_UNIT_PATTERN})
            \b
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
    (
        EurLexTemporalConstraintKind.RELATIVE_OFFSET,
        EurLexTemporalRelation.WITHIN,
        re.compile(
            rf"""
            \b
            within\s+
            (?P<quantity>{_NUMBER_PATTERN})
            \s+
            (?P<unit>{_UNIT_PATTERN})
            (?:
                \s+of\s+
                (?P<anchor>{_ANCHOR_PATTERN})
            )?
            \b
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
)

_ABSOLUTE_DATE_PATTERNS: tuple[
    tuple[
        EurLexTemporalConstraintKind,
        EurLexTemporalRelation,
        re.Pattern[str],
    ],
    ...,
] = (
    (
        EurLexTemporalConstraintKind.DEADLINE,
        EurLexTemporalRelation.NO_LATER_THAN,
        re.compile(
            rf"""
            \b
            no\s+later\s+than\s+
            (?P<date>{_DATE_PATTERN})
            \b
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
    (
        EurLexTemporalConstraintKind.START,
        EurLexTemporalRelation.NO_EARLIER_THAN,
        re.compile(
            rf"""
            \b
            no\s+earlier\s+than\s+
            (?P<date>{_DATE_PATTERN})
            \b
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
    (
        EurLexTemporalConstraintKind.DEADLINE,
        EurLexTemporalRelation.BEFORE,
        re.compile(
            rf"""
            \b
            before\s+
            (?P<date>{_DATE_PATTERN})
            \b
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
    (
        EurLexTemporalConstraintKind.START,
        EurLexTemporalRelation.AFTER,
        re.compile(
            rf"""
            \b
            after\s+
            (?P<date>{_DATE_PATTERN})
            \b
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
    (
        EurLexTemporalConstraintKind.START,
        EurLexTemporalRelation.FROM,
        re.compile(
            rf"""
            \b
            from\s+
            (?P<date>{_DATE_PATTERN})
            \b
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
    (
        EurLexTemporalConstraintKind.END,
        EurLexTemporalRelation.UNTIL,
        re.compile(
            rf"""
            \b
            until\s+
            (?P<date>{_DATE_PATTERN})
            \b
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
)

_ANCHORED_PATTERNS: tuple[
    tuple[
        EurLexTemporalConstraintKind,
        EurLexTemporalRelation,
        re.Pattern[str],
    ],
    ...,
] = (
    (
        EurLexTemporalConstraintKind.START,
        EurLexTemporalRelation.AFTER,
        re.compile(
            rf"""
            \b
            after\s+
            (?P<anchor>{_ANCHOR_PATTERN})
            \b
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
    (
        EurLexTemporalConstraintKind.DEADLINE,
        EurLexTemporalRelation.BEFORE,
        re.compile(
            rf"""
            \b
            before\s+
            (?P<anchor>{_ANCHOR_PATTERN})
            \b
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
    (
        EurLexTemporalConstraintKind.START,
        EurLexTemporalRelation.FROM,
        re.compile(
            rf"""
            \b
            from\s+
            (?P<anchor>{_ANCHOR_PATTERN})
            \b
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
    (
        EurLexTemporalConstraintKind.END,
        EurLexTemporalRelation.UNTIL,
        re.compile(
            rf"""
            \b
            until\s+
            (?P<anchor>{_ANCHOR_PATTERN})
            \b
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
)

_LEXICAL_FREQUENCY_PATTERNS: tuple[
    tuple[
        EurLexTemporalRelation,
        re.Pattern[str],
    ],
    ...,
] = (
    (
        EurLexTemporalRelation.ANNUALLY,
        re.compile(
            r"\bannually\b",
            re.IGNORECASE,
        ),
    ),
    (
        EurLexTemporalRelation.MONTHLY,
        re.compile(
            r"\bmonthly\b",
            re.IGNORECASE,
        ),
    ),
    (
        EurLexTemporalRelation.QUARTERLY,
        re.compile(
            r"\bquarterly\b",
            re.IGNORECASE,
        ),
    ),
)


class EurLexTemporalConstraintExtractor:
    """Extract explicit temporal constraints from rules."""

    def extract(
        self,
        *,
        rules: EurLexComplianceRules,
        qualifiers: EurLexRuleQualifiers,
    ) -> EurLexTemporalConstraints:
        """Extract source-backed temporal constraints."""
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

        rules_by_id = {
            rule.rule_id: rule
            for rule in rules.rules
        }

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

        constraints: list[
            EurLexTemporalConstraint
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

                constraints.append(
                    _constraint_from_rule_match(
                        rule=rule,
                        parsed=parsed,
                    )
                )

        for qualifier in qualifiers.qualifiers:
            rule = rules_by_id[
                qualifier.source_rule_id
            ]

            for parsed in _extract_matches(
                qualifier.text
            ):
                constraints.append(
                    _constraint_from_qualifier_match(
                        rule=rule,
                        qualifier=qualifier,
                        parsed=parsed,
                    )
                )

        return normalize_temporal_constraints(
            tuple(constraints)
        )


def _extract_matches(
    text: str,
) -> tuple[_TemporalMatch, ...]:
    if not isinstance(text, str):
        raise TypeError(
            "text must be a string"
        )

    matches: list[_TemporalMatch] = []

    for (
        kind,
        relation,
        pattern,
    ) in _QUANTIFIED_PATTERNS:
        for match in pattern.finditer(text):
            quantity = _parse_quantity(
                match.group("quantity")
            )
            unit = _parse_unit(
                match.group("unit")
            )
            anchor = match.groupdict().get(
                "anchor"
            )

            matches.append(
                _TemporalMatch(
                    start=match.start(),
                    end=match.end(),
                    text=_normalize_match_text(
                        match.group(0)
                    ),
                    kind=kind,
                    relation=relation,
                    quantity=quantity,
                    unit=unit,
                    anchor_text=(
                        _normalize_match_text(anchor)
                        if anchor is not None
                        else None
                    ),
                )
            )

    for (
        kind,
        relation,
        pattern,
    ) in _ABSOLUTE_DATE_PATTERNS:
        for match in pattern.finditer(text):
            matches.append(
                _TemporalMatch(
                    start=match.start(),
                    end=match.end(),
                    text=_normalize_match_text(
                        match.group(0)
                    ),
                    kind=kind,
                    relation=relation,
                    absolute_date=_parse_date(
                        match.group("date")
                    ),
                )
            )

    for (
        kind,
        relation,
        pattern,
    ) in _ANCHORED_PATTERNS:
        for match in pattern.finditer(text):
            matches.append(
                _TemporalMatch(
                    start=match.start(),
                    end=match.end(),
                    text=_normalize_match_text(
                        match.group(0)
                    ),
                    kind=kind,
                    relation=relation,
                    anchor_text=_normalize_match_text(
                        match.group("anchor")
                    ),
                )
            )

    for (
        relation,
        pattern,
    ) in _LEXICAL_FREQUENCY_PATTERNS:
        for match in pattern.finditer(text):
            matches.append(
                _TemporalMatch(
                    start=match.start(),
                    end=match.end(),
                    text=_normalize_match_text(
                        match.group(0)
                    ),
                    kind=(
                        EurLexTemporalConstraintKind
                        .FREQUENCY
                    ),
                    relation=relation,
                )
            )

    return _remove_overlapping_matches(
        tuple(matches)
    )


def _remove_overlapping_matches(
    matches: tuple[_TemporalMatch, ...],
) -> tuple[_TemporalMatch, ...]:
    ordered = sorted(
        matches,
        key=lambda match: (
            match.start,
            -(match.end - match.start),
            match.relation.value,
        ),
    )

    accepted: list[_TemporalMatch] = []

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
                match.relation.value,
            ),
        )
    )


def _matches_overlap(
    left: _TemporalMatch,
    right: _TemporalMatch,
) -> bool:
    return (
        left.start < right.end
        and right.start < left.end
    )


def _constraint_from_rule_match(
    *,
    rule: EurLexComplianceRule,
    parsed: _TemporalMatch,
) -> EurLexTemporalConstraint:
    return EurLexTemporalConstraint(
        constraint_id=_stable_constraint_id(
            source_rule_id=rule.rule_id,
            source_qualifier_id=None,
            parsed=parsed,
        ),
        kind=parsed.kind,
        relation=parsed.relation,
        text=parsed.text,
        source_rule_id=rule.rule_id,
        source_requirement_id=(
            rule.source_requirement_id
        ),
        source_node_id=rule.source_node_id,
        source_text=rule.source_text,
        absolute_date=parsed.absolute_date,
        quantity=parsed.quantity,
        unit=parsed.unit,
        anchor_text=parsed.anchor_text,
    )


def _constraint_from_qualifier_match(
    *,
    rule: EurLexComplianceRule,
    qualifier: EurLexRuleQualifier,
    parsed: _TemporalMatch,
) -> EurLexTemporalConstraint:
    return EurLexTemporalConstraint(
        constraint_id=_stable_constraint_id(
            source_rule_id=rule.rule_id,
            source_qualifier_id=(
                qualifier.qualifier_id
            ),
            parsed=parsed,
        ),
        kind=parsed.kind,
        relation=parsed.relation,
        text=parsed.text,
        source_rule_id=rule.rule_id,
        source_requirement_id=(
            rule.source_requirement_id
        ),
        source_node_id=(
            qualifier.source_node_id
        ),
        source_text=qualifier.source_text,
        absolute_date=parsed.absolute_date,
        quantity=parsed.quantity,
        unit=parsed.unit,
        anchor_text=parsed.anchor_text,
        source_qualifier_id=(
            qualifier.qualifier_id
        ),
    )


def _stable_constraint_id(
    *,
    source_rule_id: str,
    source_qualifier_id: str | None,
    parsed: _TemporalMatch,
) -> str:
    digest = sha256(
        "\x1f".join(
            (
                source_rule_id,
                source_qualifier_id or "",
                parsed.kind.value,
                parsed.relation.value,
                str(parsed.start),
                parsed.text.casefold(),
            )
        ).encode("utf-8")
    ).hexdigest()[:16]

    return f"temporal-constraint-{digest}"


def _parse_quantity(
    value: str,
) -> int:
    normalized = (
        value.strip()
        .casefold()
        .replace("-", " ")
    )

    if normalized.isdigit():
        quantity = int(normalized)
    else:
        parts = normalized.split()

        try:
            quantity = sum(
                _NUMBER_BY_WORD[part]
                for part in parts
            )
        except KeyError as exc:
            raise ValueError(
                "unsupported temporal quantity"
            ) from exc

    if quantity <= 0:
        raise ValueError(
            "temporal quantity must be positive"
        )

    return quantity


def _parse_unit(
    value: str,
) -> EurLexTemporalUnit:
    normalized = value.strip().casefold()

    try:
        return _UNIT_BY_TEXT[normalized]
    except KeyError as exc:
        raise ValueError(
            "unsupported temporal unit"
        ) from exc


def _parse_date(
    value: str,
) -> date:
    normalized = " ".join(
        value.split()
    )

    if re.fullmatch(
        r"\d{4}-\d{2}-\d{2}",
        normalized,
    ):
        try:
            return date.fromisoformat(normalized)
        except ValueError as exc:
            raise ValueError(
                "temporal expression contains "
                "an invalid ISO date"
            ) from exc

    match = re.fullmatch(
        rf"""
        (?P<day>\d{{1,2}})
        \s+
        (?P<month>{_MONTH_PATTERN})
        \s+
        (?P<year>\d{{4}})
        """,
        normalized,
        re.IGNORECASE | re.VERBOSE,
    )
    if match is None:
        raise ValueError(
            "unsupported temporal date"
        )

    month_name = (
        match.group("month").casefold()
    )

    try:
        return date(
            int(match.group("year")),
            _MONTH_BY_NAME[month_name],
            int(match.group("day")),
        )
    except ValueError as exc:
        raise ValueError(
            "temporal expression contains "
            "an invalid calendar date"
        ) from exc


def _normalize_match_text(
    value: str,
) -> str:
    return " ".join(value.split())