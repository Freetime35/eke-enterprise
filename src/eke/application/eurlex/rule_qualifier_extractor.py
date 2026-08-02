"""Extract explicit conditions and exceptions from compliance rules."""

from __future__ import annotations

import re
from hashlib import sha256

from eke.application.eurlex.compliance_rules import (
    EurLexComplianceRules,
)
from eke.application.eurlex.requirements_graph import (
    EurLexRequirementsGraph,
)
from eke.application.eurlex.rule_qualifiers import (
    EurLexRuleQualifier,
    EurLexRuleQualifierKind,
    EurLexRuleQualifierMarker,
    EurLexRuleQualifiers,
)

_LEADING_PATTERNS: tuple[
    tuple[
        EurLexRuleQualifierKind,
        EurLexRuleQualifierMarker,
        re.Pattern[str],
    ],
    ...,
] = (
    (
        EurLexRuleQualifierKind.EXCEPTION,
        EurLexRuleQualifierMarker.EXCEPT_WHERE,
        re.compile(
            r"^\s*except\s+where\s+(?P<text>.+?),\s+.+$",
            re.IGNORECASE,
        ),
    ),
    (
        EurLexRuleQualifierKind.EXCEPTION,
        EurLexRuleQualifierMarker.EXCEPT_IF,
        re.compile(
            r"^\s*except\s+if\s+(?P<text>.+?),\s+.+$",
            re.IGNORECASE,
        ),
    ),
    (
        EurLexRuleQualifierKind.EXCEPTION,
        EurLexRuleQualifierMarker.SAVE_WHERE,
        re.compile(
            r"^\s*save\s+where\s+(?P<text>.+?),\s+.+$",
            re.IGNORECASE,
        ),
    ),
    (
        EurLexRuleQualifierKind.EXCEPTION,
        EurLexRuleQualifierMarker.UNLESS,
        re.compile(
            r"^\s*unless\s+(?P<text>.+?),\s+.+$",
            re.IGNORECASE,
        ),
    ),
    (
        EurLexRuleQualifierKind.CONDITION,
        EurLexRuleQualifierMarker.PROVIDED_THAT,
        re.compile(
            r"^\s*provided\s+that\s+(?P<text>.+?),\s+.+$",
            re.IGNORECASE,
        ),
    ),
    (
        EurLexRuleQualifierKind.CONDITION,
        EurLexRuleQualifierMarker.SUBJECT_TO,
        re.compile(
            r"^\s*subject\s+to\s+(?P<text>.+?),\s+.+$",
            re.IGNORECASE,
        ),
    ),
    (
        EurLexRuleQualifierKind.CONDITION,
        EurLexRuleQualifierMarker.IF,
        re.compile(
            r"^\s*if\s+(?P<text>.+?),\s+.+$",
            re.IGNORECASE,
        ),
    ),
    (
        EurLexRuleQualifierKind.CONDITION,
        EurLexRuleQualifierMarker.WHERE,
        re.compile(
            r"^\s*where\s+(?P<text>.+?),\s+.+$",
            re.IGNORECASE,
        ),
    ),
    (
        EurLexRuleQualifierKind.CONDITION,
        EurLexRuleQualifierMarker.WHEN,
        re.compile(
            r"^\s*when\s+(?P<text>.+?),\s+.+$",
            re.IGNORECASE,
        ),
    ),
)

_TRAILING_PATTERNS: tuple[
    tuple[
        EurLexRuleQualifierKind,
        EurLexRuleQualifierMarker,
        re.Pattern[str],
    ],
    ...,
] = (
    (
        EurLexRuleQualifierKind.EXCEPTION,
        EurLexRuleQualifierMarker.EXCEPT_WHERE,
        re.compile(
            r"^.+?,\s*except\s+where\s+(?P<text>.+?)\s*[.;]?$",
            re.IGNORECASE,
        ),
    ),
    (
        EurLexRuleQualifierKind.EXCEPTION,
        EurLexRuleQualifierMarker.EXCEPT_IF,
        re.compile(
            r"^.+?,\s*except\s+if\s+(?P<text>.+?)\s*[.;]?$",
            re.IGNORECASE,
        ),
    ),
    (
        EurLexRuleQualifierKind.EXCEPTION,
        EurLexRuleQualifierMarker.SAVE_WHERE,
        re.compile(
            r"^.+?,\s*save\s+where\s+(?P<text>.+?)\s*[.;]?$",
            re.IGNORECASE,
        ),
    ),
    (
        EurLexRuleQualifierKind.EXCEPTION,
        EurLexRuleQualifierMarker.UNLESS,
        re.compile(
            r"^.+?,\s*unless\s+(?P<text>.+?)\s*[.;]?$",
            re.IGNORECASE,
        ),
    ),
    (
        EurLexRuleQualifierKind.CONDITION,
        EurLexRuleQualifierMarker.PROVIDED_THAT,
        re.compile(
            r"^.+?,\s*provided\s+that\s+(?P<text>.+?)\s*[.;]?$",
            re.IGNORECASE,
        ),
    ),
    (
        EurLexRuleQualifierKind.CONDITION,
        EurLexRuleQualifierMarker.IF,
        re.compile(
            r"^.+?,\s*if\s+(?P<text>.+?)\s*[.;]?$",
            re.IGNORECASE,
        ),
    ),
    (
        EurLexRuleQualifierKind.CONDITION,
        EurLexRuleQualifierMarker.WHERE,
        re.compile(
            r"^.+?,\s*where\s+(?P<text>.+?)\s*[.;]?$",
            re.IGNORECASE,
        ),
    ),
    (
        EurLexRuleQualifierKind.CONDITION,
        EurLexRuleQualifierMarker.WHEN,
        re.compile(
            r"^.+?,\s*when\s+(?P<text>.+?)\s*[.;]?$",
            re.IGNORECASE,
        ),
    ),
)


class EurLexRuleQualifierExtractor:
    """Extract explicit qualifiers from existing rules only."""

    def extract(
        self,
        *,
        graph: EurLexRequirementsGraph,
        rules: EurLexComplianceRules,
    ) -> EurLexRuleQualifiers:
        """Extract qualifiers without logical interpretation."""
        if not isinstance(
            graph,
            EurLexRequirementsGraph,
        ):
            raise TypeError(
                "graph must be an "
                "EurLexRequirementsGraph"
            )

        if not isinstance(
            rules,
            EurLexComplianceRules,
        ):
            raise TypeError(
                "rules must be an "
                "EurLexComplianceRules"
            )

        requirement_ids = {
            requirement.requirement_id
            for requirement in graph.requirements
        }
        if any(
            rule.source_requirement_id
            not in requirement_ids
            for rule in rules.rules
        ):
            raise ValueError(
                "rules must reference graph "
                "requirements"
            )

        qualifiers: list[
            EurLexRuleQualifier
        ] = []

        for rule in rules.rules:
            parsed = _parse_qualifier(
                rule.source_text
            )
            if parsed is None:
                continue

            kind, marker, text = parsed
            qualifiers.append(
                EurLexRuleQualifier(
                    qualifier_id=_stable_id(
                        "qualifier",
                        rule.rule_id,
                        kind.value,
                        marker.value,
                        text.casefold(),
                    ),
                    kind=kind,
                    marker=marker,
                    text=text,
                    source_rule_id=rule.rule_id,
                    source_requirement_id=(
                        rule
                        .source_requirement_id
                    ),
                    source_node_id=(
                        rule.source_node_id
                    ),
                    source_text=rule.source_text,
                    referenced_node_ids=(
                        rule.referenced_node_ids
                    ),
                )
            )

        return EurLexRuleQualifiers(
            qualifiers=tuple(qualifiers)
        )


def _parse_qualifier(
    source_text: str,
) -> tuple[
    EurLexRuleQualifierKind,
    EurLexRuleQualifierMarker,
    str,
] | None:
    for kind, marker, pattern in (
        _LEADING_PATTERNS
        + _TRAILING_PATTERNS
    ):
        match = pattern.fullmatch(
            source_text
        )
        if match is None:
            continue

        text = match.group(
            "text"
        ).strip(" ,;:.")
        if not text:
            return None

        return kind, marker, text

    return None


def _stable_id(
    prefix: str,
    *parts: str,
) -> str:
    digest = sha256(
        "\x1f".join(parts).encode(
            "utf-8"
        )
    ).hexdigest()[:16]
    return f"{prefix}-{digest}"
