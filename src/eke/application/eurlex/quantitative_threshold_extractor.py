"""Extract explicit quantitative thresholds from EUR-Lex rules."""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from hashlib import sha256

from eke.application.eurlex.compliance_rules import (
    EurLexComplianceRule,
    EurLexComplianceRules,
)
from eke.application.eurlex.quantitative_thresholds import (
    EurLexQuantitativeComparator,
    EurLexQuantitativeThreshold,
    EurLexQuantitativeThresholds,
    EurLexQuantitativeUnitKind,
    normalize_quantitative_thresholds,
)
from eke.application.eurlex.rule_qualifiers import (
    EurLexRuleQualifier,
    EurLexRuleQualifiers,
)

_CURRENCY_CODES = {
    "EUR",
    "USD",
    "GBP",
    "CHF",
    "JPY",
}

_MULTIPLIER_BY_TEXT: dict[str, Decimal] = {
    "thousand": Decimal("1000"),
    "million": Decimal("1000000"),
    "billion": Decimal("1000000000"),
}

_COUNT_UNITS = {
    "employee",
    "employees",
    "person",
    "persons",
    "worker",
    "workers",
    "undertaking",
    "undertakings",
    "entity",
    "entities",
    "unit",
    "units",
    "transaction",
    "transactions",
    "account",
    "accounts",
}

_MASS_UNITS = {
    "g",
    "gram",
    "grams",
    "kg",
    "kilogram",
    "kilograms",
    "t",
    "tonne",
    "tonnes",
}

_LENGTH_UNITS = {
    "mm",
    "millimetre",
    "millimetres",
    "cm",
    "centimetre",
    "centimetres",
    "m",
    "metre",
    "metres",
    "km",
    "kilometre",
    "kilometres",
}

_AREA_UNITS = {
    "m2",
    "m²",
    "square metre",
    "square metres",
    "km2",
    "km²",
    "square kilometre",
    "square kilometres",
}

_VOLUME_UNITS = {
    "ml",
    "millilitre",
    "millilitres",
    "l",
    "litre",
    "litres",
    "m3",
    "m³",
    "cubic metre",
    "cubic metres",
}

_ENERGY_UNITS = {
    "wh",
    "kwh",
    "mwh",
    "gj",
    "terajoule",
    "terajoules",
}

_TIME_UNITS = {
    "second",
    "seconds",
    "minute",
    "minutes",
    "hour",
    "hours",
    "day",
    "days",
    "week",
    "weeks",
    "month",
    "months",
    "year",
    "years",
}

_NUMBER_PATTERN = (
    r"(?:"
    r"\d{1,3}(?:[ ,]\d{3})+(?:[.,]\d+)?"
    r"|"
    r"\d+(?:[.,]\d+)?"
    r")"
)

_MULTIPLIER_PATTERN = (
    r"(?:thousand|million|billion)"
)

_CURRENCY_PATTERN = (
    r"(?:EUR|USD|GBP|CHF|JPY)"
)

_UNIT_PATTERN = (
    r"(?:"
    r"%"
    r"|square\s+kilometres?"
    r"|km2|km²"
    r"|square\s+metres?"
    r"|m2|m²"
    r"|cubic\s+metres?"
    r"|m3|m³"
    r"|millimetres?"
    r"|mm"
    r"|centimetres?"
    r"|cm"
    r"|kilometres?"
    r"|km"
    r"|metres?"
    r"|m"
    r"|millilitres?"
    r"|ml"
    r"|litres?"
    r"|l"
    r"|kilograms?"
    r"|kg"
    r"|grams?"
    r"|g"
    r"|tonnes?"
    r"|t"
    r"|terajoules?"
    r"|wh|kwh|mwh|gj"
    r"|employees?"
    r"|persons?"
    r"|workers?"
    r"|undertakings?"
    r"|entities?"
    r"|units?"
    r"|transactions?"
    r"|accounts?"
    r"|seconds?"
    r"|minutes?"
    r"|hours?"
    r"|days?"
    r"|weeks?"
    r"|months?"
    r"|years?"
    r")"
)

_VALUE_WITH_UNIT_PATTERN = (
    rf"""
    (?:
        (?P<currency>{_CURRENCY_PATTERN})
        \s*
    )?
    (?P<value>{_NUMBER_PATTERN})
    (?:
        \s+
        (?P<multiplier>{_MULTIPLIER_PATTERN})
    )?
    (?:
        \s*
        (?P<unit>{_UNIT_PATTERN})
    )?
    """
)


@dataclass(frozen=True, slots=True)
class _ParsedQuantity:
    """Represent one parsed numeric value and its unit."""

    value: Decimal
    unit_text: str | None
    unit_kind: EurLexQuantitativeUnitKind
    currency_code: str | None


@dataclass(frozen=True, slots=True)
class _ThresholdMatch:
    """Represent one parsed quantitative threshold."""

    start: int
    end: int
    text: str
    comparator: EurLexQuantitativeComparator
    value: Decimal
    upper_value: Decimal | None = None
    unit_text: str | None = None
    unit_kind: EurLexQuantitativeUnitKind = (
        EurLexQuantitativeUnitKind.OTHER
    )
    currency_code: str | None = None


_BETWEEN_PATTERN = re.compile(
    rf"""
    between
    \s+
    {_VALUE_WITH_UNIT_PATTERN}
    \s+
    and
    \s+
    (?:
        (?P<upper_currency>{_CURRENCY_PATTERN})
        \s*
    )?
    (?P<upper_value>{_NUMBER_PATTERN})
    (?:
        \s+
        (?P<upper_multiplier>{_MULTIPLIER_PATTERN})
    )?
    (?:
        \s*
        (?P<upper_unit>{_UNIT_PATTERN})
    )?
    """,
    re.IGNORECASE | re.VERBOSE,
)

_FROM_TO_PATTERN = re.compile(
    rf"""
    from
    \s+
    {_VALUE_WITH_UNIT_PATTERN}
    \s+
    to
    \s+
    (?:
        (?P<upper_currency>{_CURRENCY_PATTERN})
        \s*
    )?
    (?P<upper_value>{_NUMBER_PATTERN})
    (?:
        \s+
        (?P<upper_multiplier>{_MULTIPLIER_PATTERN})
    )?
    (?:
        \s*
        (?P<upper_unit>{_UNIT_PATTERN})
    )?
    """,
    re.IGNORECASE | re.VERBOSE,
)

_COMPARATOR_PATTERNS: tuple[
    tuple[
        EurLexQuantitativeComparator,
        re.Pattern[str],
    ],
    ...,
] = (
    (
        EurLexQuantitativeComparator
        .GREATER_THAN_OR_EQUAL_TO,
        re.compile(
            rf"""
            (?:
                at\s+least
                |
                not\s+less\s+than
                |
                no\s+less\s+than
            )
            \s+
            {_VALUE_WITH_UNIT_PATTERN}
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
    (
        EurLexQuantitativeComparator
        .LESS_THAN_OR_EQUAL_TO,
        re.compile(
            rf"""
            (?:
                at\s+most
                |
                not\s+exceeding
                |
                no\s+more\s+than
            )
            \s+
            {_VALUE_WITH_UNIT_PATTERN}
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
    (
        EurLexQuantitativeComparator.GREATER_THAN,
        re.compile(
            rf"""
            \b
            (?:
                more\s+than
                |
                greater\s+than
                |
                exceed
                |
                exceeds
                |
                exceeded
                |
                exceeding
            )
            \s+
            {_VALUE_WITH_UNIT_PATTERN}
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
    (
        EurLexQuantitativeComparator.LESS_THAN,
        re.compile(
            rf"""
            \b
            (?:
                less\s+than
                |
                fewer\s+than
                |
                below
            )
            \s+
            {_VALUE_WITH_UNIT_PATTERN}
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
    (
        EurLexQuantitativeComparator.NOT_EQUAL_TO,
        re.compile(
            rf"""
            \b
            (?:
                not\s+equal\s+to
                |
                different\s+from
            )
            \s+
            {_VALUE_WITH_UNIT_PATTERN}
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
    (
        EurLexQuantitativeComparator.EQUAL_TO,
        re.compile(
            rf"""
            \b
            (?:
                equal\s+to
                |
                exactly
            )
            \s+
            {_VALUE_WITH_UNIT_PATTERN}
            """,
            re.IGNORECASE | re.VERBOSE,
        ),
    ),
)


class EurLexQuantitativeThresholdExtractor:
    """Extract explicit quantitative thresholds from rules."""

    def extract(
        self,
        *,
        rules: EurLexComplianceRules,
        qualifiers: EurLexRuleQualifiers,
    ) -> EurLexQuantitativeThresholds:
        """Extract source-backed quantitative thresholds."""
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

        thresholds: list[
            EurLexQuantitativeThreshold
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

                thresholds.append(
                    _threshold_from_rule_match(
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
                thresholds.append(
                    _threshold_from_qualifier_match(
                        rule=rule,
                        qualifier=qualifier,
                        parsed=parsed,
                    )
                )

        return normalize_quantitative_thresholds(
            tuple(thresholds)
        )


def _extract_matches(
    text: str,
) -> tuple[_ThresholdMatch, ...]:
    if not isinstance(text, str):
        raise TypeError(
            "text must be a string"
        )

    matches: list[_ThresholdMatch] = []

    for pattern in (
        _BETWEEN_PATTERN,
        _FROM_TO_PATTERN,
    ):
        for match in pattern.finditer(text):
            lower = _parsed_quantity_from_match(
                match
            )
            upper = _parse_upper_quantity(
                match,
                lower=lower,
            )

            if upper.value < lower.value:
                raise ValueError(
                    "upper threshold value must be "
                    "greater than or equal to lower "
                    "threshold value"
                )

            matches.append(
                _ThresholdMatch(
                    start=match.start(),
                    end=match.end(),
                    text=_normalize_match_text(
                        match.group(0)
                    ),
                    comparator=(
                        EurLexQuantitativeComparator
                        .BETWEEN
                    ),
                    value=lower.value,
                    upper_value=upper.value,
                    unit_text=lower.unit_text,
                    unit_kind=lower.unit_kind,
                    currency_code=(
                        lower.currency_code
                    ),
                )
            )

    for comparator, pattern in (
        _COMPARATOR_PATTERNS
    ):
        for match in pattern.finditer(text):
            parsed = _parsed_quantity_from_match(
                match
            )

            matches.append(
                _ThresholdMatch(
                    start=match.start(),
                    end=match.end(),
                    text=_normalize_match_text(
                        match.group(0)
                    ),
                    comparator=comparator,
                    value=parsed.value,
                    unit_text=parsed.unit_text,
                    unit_kind=parsed.unit_kind,
                    currency_code=(
                        parsed.currency_code
                    ),
                )
            )

    return _remove_overlapping_matches(
        tuple(matches)
    )


def _parsed_quantity_from_match(
    match: re.Match[str],
) -> _ParsedQuantity:
    currency = match.groupdict().get(
        "currency"
    )
    multiplier = match.groupdict().get(
        "multiplier"
    )
    unit = match.groupdict().get(
        "unit"
    )

    value = _parse_decimal(
        match.group("value")
    )
    value = _apply_multiplier(
        value,
        multiplier,
    )

    normalized_currency = (
        currency.upper()
        if currency is not None
        else None
    )
    normalized_unit = (
        _normalize_match_text(unit)
        if unit is not None
        else None
    )

    unit_kind = _classify_unit(
        unit_text=normalized_unit,
        currency_code=normalized_currency,
    )

    return _ParsedQuantity(
        value=value,
        unit_text=normalized_unit,
        unit_kind=unit_kind,
        currency_code=normalized_currency,
    )


def _parse_upper_quantity(
    match: re.Match[str],
    *,
    lower: _ParsedQuantity,
) -> _ParsedQuantity:
    currency = match.groupdict().get(
        "upper_currency"
    )
    multiplier = match.groupdict().get(
        "upper_multiplier"
    )
    unit = match.groupdict().get(
        "upper_unit"
    )

    value = _parse_decimal(
        match.group("upper_value")
    )
    value = _apply_multiplier(
        value,
        multiplier,
    )

    normalized_currency = (
        currency.upper()
        if currency is not None
        else lower.currency_code
    )
    normalized_unit = (
        _normalize_match_text(unit)
        if unit is not None
        else lower.unit_text
    )
    unit_kind = _classify_unit(
        unit_text=normalized_unit,
        currency_code=normalized_currency,
    )

    if (
        lower.currency_code is not None
        and normalized_currency
        != lower.currency_code
    ):
        raise ValueError(
            "range bounds must use the same currency"
        )

    if (
        lower.unit_text is not None
        and normalized_unit is not None
        and normalized_unit.casefold()
        != lower.unit_text.casefold()
    ):
        raise ValueError(
            "range bounds must use the same unit"
        )

    return _ParsedQuantity(
        value=value,
        unit_text=normalized_unit,
        unit_kind=unit_kind,
        currency_code=normalized_currency,
    )


def _remove_overlapping_matches(
    matches: tuple[_ThresholdMatch, ...],
) -> tuple[_ThresholdMatch, ...]:
    ordered = sorted(
        matches,
        key=lambda match: (
            match.start,
            -(match.end - match.start),
            match.comparator.value,
        ),
    )

    accepted: list[_ThresholdMatch] = []

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
                match.comparator.value,
            ),
        )
    )


def _matches_overlap(
    left: _ThresholdMatch,
    right: _ThresholdMatch,
) -> bool:
    return (
        left.start < right.end
        and right.start < left.end
    )


def _threshold_from_rule_match(
    *,
    rule: EurLexComplianceRule,
    parsed: _ThresholdMatch,
) -> EurLexQuantitativeThreshold:
    return EurLexQuantitativeThreshold(
        threshold_id=_stable_threshold_id(
            source_rule_id=rule.rule_id,
            source_qualifier_id=None,
            parsed=parsed,
        ),
        comparator=parsed.comparator,
        text=parsed.text,
        source_rule_id=rule.rule_id,
        source_requirement_id=(
            rule.source_requirement_id
        ),
        source_node_id=rule.source_node_id,
        source_text=rule.source_text,
        value=parsed.value,
        upper_value=parsed.upper_value,
        unit_text=parsed.unit_text,
        unit_kind=parsed.unit_kind,
        currency_code=parsed.currency_code,
    )


def _threshold_from_qualifier_match(
    *,
    rule: EurLexComplianceRule,
    qualifier: EurLexRuleQualifier,
    parsed: _ThresholdMatch,
) -> EurLexQuantitativeThreshold:
    return EurLexQuantitativeThreshold(
        threshold_id=_stable_threshold_id(
            source_rule_id=rule.rule_id,
            source_qualifier_id=(
                qualifier.qualifier_id
            ),
            parsed=parsed,
        ),
        comparator=parsed.comparator,
        text=parsed.text,
        source_rule_id=rule.rule_id,
        source_requirement_id=(
            rule.source_requirement_id
        ),
        source_node_id=(
            qualifier.source_node_id
        ),
        source_text=qualifier.source_text,
        value=parsed.value,
        upper_value=parsed.upper_value,
        unit_text=parsed.unit_text,
        unit_kind=parsed.unit_kind,
        currency_code=parsed.currency_code,
        source_qualifier_id=(
            qualifier.qualifier_id
        ),
    )


def _stable_threshold_id(
    *,
    source_rule_id: str,
    source_qualifier_id: str | None,
    parsed: _ThresholdMatch,
) -> str:
    digest = sha256(
        "\x1f".join(
            (
                source_rule_id,
                source_qualifier_id or "",
                parsed.comparator.value,
                str(parsed.start),
                parsed.text.casefold(),
            )
        ).encode("utf-8")
    ).hexdigest()[:16]

    return f"quantitative-threshold-{digest}"


def _parse_decimal(
    value: str,
) -> Decimal:
    normalized = value.strip()

    if (
        "," in normalized
        and "." not in normalized
    ):
        if re.fullmatch(
            r"\d{1,3}(?:,\d{3})+",
            normalized,
        ):
            normalized = normalized.replace(
                ",",
                "",
            )
        else:
            normalized = normalized.replace(
                ",",
                ".",
            )

    normalized = normalized.replace(
        " ",
        "",
    )

    try:
        parsed = Decimal(normalized)
    except InvalidOperation as exc:
        raise ValueError(
            "unsupported quantitative value"
        ) from exc

    if not parsed.is_finite():
        raise ValueError(
            "quantitative value must be finite"
        )

    if parsed < Decimal("0"):
        raise ValueError(
            "quantitative value must not be negative"
        )

    return parsed


def _apply_multiplier(
    value: Decimal,
    multiplier: str | None,
) -> Decimal:
    if multiplier is None:
        return value

    normalized = multiplier.casefold()

    try:
        factor = _MULTIPLIER_BY_TEXT[
            normalized
        ]
    except KeyError as exc:
        raise ValueError(
            "unsupported quantitative multiplier"
        ) from exc

    return value * factor


def _classify_unit(
    *,
    unit_text: str | None,
    currency_code: str | None,
) -> EurLexQuantitativeUnitKind:
    if currency_code is not None:
        if currency_code not in _CURRENCY_CODES:
            raise ValueError(
                "unsupported currency code"
            )
        return EurLexQuantitativeUnitKind.CURRENCY

    if unit_text is None:
        return EurLexQuantitativeUnitKind.OTHER

    normalized = unit_text.casefold()

    if normalized == "%":
        return EurLexQuantitativeUnitKind.PERCENT
    if normalized in _COUNT_UNITS:
        return EurLexQuantitativeUnitKind.COUNT
    if normalized in _MASS_UNITS:
        return EurLexQuantitativeUnitKind.MASS
    if normalized in _LENGTH_UNITS:
        return EurLexQuantitativeUnitKind.LENGTH
    if normalized in _AREA_UNITS:
        return EurLexQuantitativeUnitKind.AREA
    if normalized in _VOLUME_UNITS:
        return EurLexQuantitativeUnitKind.VOLUME
    if normalized in _ENERGY_UNITS:
        return EurLexQuantitativeUnitKind.ENERGY
    if normalized in _TIME_UNITS:
        return EurLexQuantitativeUnitKind.TIME

    return EurLexQuantitativeUnitKind.OTHER


def _normalize_match_text(
    value: str,
) -> str:
    return " ".join(value.split())
