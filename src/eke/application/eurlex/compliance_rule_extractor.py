"""Extract deterministic compliance rules from requirements graphs."""

from __future__ import annotations

from hashlib import sha256

from eke.application.eurlex.compliance_rules import (
    EurLexComplianceRule,
    EurLexComplianceRuleKind,
    EurLexComplianceRules,
)
from eke.application.eurlex.requirements_graph import (
    EurLexRequirementKind,
    EurLexRequirementsGraph,
)

_RULE_KIND_BY_REQUIREMENT_KIND: dict[
    EurLexRequirementKind,
    EurLexComplianceRuleKind,
] = {
    EurLexRequirementKind.OBLIGATION: (
        EurLexComplianceRuleKind.REQUIREMENT
    ),
    EurLexRequirementKind.PERMISSION: (
        EurLexComplianceRuleKind.PERMISSION
    ),
    EurLexRequirementKind.PROHIBITION: (
        EurLexComplianceRuleKind.PROHIBITION
    ),
}


class EurLexComplianceRuleExtractor:
    """Derive one compliance rule per graph requirement."""

    def extract(
        self,
        graph: EurLexRequirementsGraph,
    ) -> EurLexComplianceRules:
        """Extract rules without reinterpreting source text."""
        if not isinstance(
            graph,
            EurLexRequirementsGraph,
        ):
            raise TypeError(
                "graph must be an "
                "EurLexRequirementsGraph"
            )

        rules: list[
            EurLexComplianceRule
        ] = []

        for requirement in graph.requirements:
            referenced_node_ids = tuple(
                node.node_id
                for node in graph.referenced_nodes(
                    requirement.requirement_id
                )
            )
            definition_ids = tuple(
                definition.definition_id
                for definition
                in graph.definitions_for_requirement(
                    requirement.requirement_id
                )
            )

            rules.append(
                EurLexComplianceRule(
                    rule_id=_stable_rule_id(
                        requirement
                        .requirement_id
                    ),
                    kind=(
                        _RULE_KIND_BY_REQUIREMENT_KIND[
                            requirement.kind
                        ]
                    ),
                    subject=requirement.subject,
                    action=requirement.action,
                    source_requirement_id=(
                        requirement
                        .requirement_id
                    ),
                    source_node_id=(
                        requirement.source_node_id
                    ),
                    source_text=(
                        requirement.source_text
                    ),
                    language=requirement.language,
                    article_node_id=(
                        requirement
                        .article_node_id
                    ),
                    paragraph_node_id=(
                        requirement
                        .paragraph_node_id
                    ),
                    referenced_node_ids=(
                        referenced_node_ids
                    ),
                    definition_ids=definition_ids,
                )
            )

        return EurLexComplianceRules(
            rules=tuple(rules)
        )


def _stable_rule_id(
    source_requirement_id: str,
) -> str:
    digest = sha256(
        source_requirement_id.encode(
            "utf-8"
        )
    ).hexdigest()[:16]
    return f"rule-{digest}"
