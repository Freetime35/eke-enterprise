"""Extract legal actors from explicit requirement subjects."""

from __future__ import annotations

from hashlib import sha256

from eke.application.eurlex.compliance_rules import (
    EurLexComplianceRules,
)
from eke.application.eurlex.legal_actors import (
    EurLexLegalActor,
    EurLexLegalActorKind,
    EurLexLegalActorMention,
    EurLexLegalActors,
)
from eke.application.eurlex.requirements_graph import (
    EurLexRequirementsGraph,
)

_EXPLICIT_ACTOR_KINDS: dict[
    str,
    EurLexLegalActorKind,
] = {
    "european commission": (
        EurLexLegalActorKind.EU_INSTITUTION
    ),
    "the european commission": (
        EurLexLegalActorKind.EU_INSTITUTION
    ),
    "commission": (
        EurLexLegalActorKind.EU_INSTITUTION
    ),
    "the commission": (
        EurLexLegalActorKind.EU_INSTITUTION
    ),
    "member state": (
        EurLexLegalActorKind.MEMBER_STATE
    ),
    "member states": (
        EurLexLegalActorKind.MEMBER_STATE
    ),
    "competent authority": (
        EurLexLegalActorKind
        .COMPETENT_AUTHORITY
    ),
    "competent authorities": (
        EurLexLegalActorKind
        .COMPETENT_AUTHORITY
    ),
    "applicant": (
        EurLexLegalActorKind.APPLICANT
    ),
    "applicants": (
        EurLexLegalActorKind.APPLICANT
    ),
    "operator": (
        EurLexLegalActorKind.OPERATOR
    ),
    "operators": (
        EurLexLegalActorKind.OPERATOR
    ),
}


class EurLexLegalActorExtractor:
    """Derive actors and mentions from explicit rule subjects."""

    def extract(
        self,
        *,
        graph: EurLexRequirementsGraph,
        rules: EurLexComplianceRules,
    ) -> EurLexLegalActors:
        """Extract actors without synonym or pronoun resolution."""
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

        actors_by_key: dict[
            tuple[str, str | None],
            EurLexLegalActor,
        ] = {}
        mentions: list[
            EurLexLegalActorMention
        ] = []

        for rule in rules.rules:
            definition_ids = rule.definition_ids
            definition_id = (
                definition_ids[0]
                if len(definition_ids) == 1
                else None
            )

            canonical_name = (
                " ".join(
                    rule.subject.split()
                )
            )
            actor_key = (
                canonical_name.casefold(),
                definition_id,
            )

            actor = actors_by_key.get(
                actor_key
            )
            if actor is None:
                actor = EurLexLegalActor(
                    actor_id=_stable_id(
                        "actor",
                        actor_key[0],
                        definition_id or "",
                    ),
                    canonical_name=canonical_name,
                    source_label=rule.subject,
                    kind=_classify_actor(
                        canonical_name,
                        definition_id=(
                            definition_id
                        ),
                    ),
                    language=rule.language,
                    definition_id=definition_id,
                )
                actors_by_key[
                    actor_key
                ] = actor

            mentions.append(
                EurLexLegalActorMention(
                    mention_id=_stable_id(
                        "mention",
                        actor.actor_id,
                        rule.source_requirement_id,
                    ),
                    actor_id=actor.actor_id,
                    source_requirement_id=(
                        rule
                        .source_requirement_id
                    ),
                    source_node_id=(
                        rule.source_node_id
                    ),
                    source_text=rule.source_text,
                )
            )

        return EurLexLegalActors(
            actors=tuple(
                actors_by_key.values()
            ),
            mentions=tuple(mentions),
        )


def _classify_actor(
    canonical_name: str,
    *,
    definition_id: str | None,
) -> EurLexLegalActorKind:
    explicit_kind = _EXPLICIT_ACTOR_KINDS.get(
        canonical_name.casefold()
    )
    if explicit_kind is not None:
        return explicit_kind

    if definition_id is not None:
        return (
            EurLexLegalActorKind
            .REGULATED_ENTITY
        )

    return EurLexLegalActorKind.GENERIC_ACTOR


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
