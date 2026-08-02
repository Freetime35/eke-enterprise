"""Tests for EUR-Lex legal actors."""

import pytest

from eke.application.eurlex import (
    EurLexLegalActor,
    EurLexLegalActorKind,
    EurLexLegalActorMention,
    EurLexLegalActors,
)
from eke.domain.localization import LanguageCode


def test_actor_and_mention_normalize_values() -> None:
    actor = EurLexLegalActor(
        actor_id=" actor-1 ",
        canonical_name=" credit   institution ",
        source_label=" credit institution ",
        kind=(
            EurLexLegalActorKind
            .REGULATED_ENTITY
        ),
        language=LanguageCode("en"),
        definition_id=" definition-1 ",
    )
    mention = EurLexLegalActorMention(
        mention_id=" mention-1 ",
        actor_id=" actor-1 ",
        source_requirement_id=(
            " requirement-1 "
        ),
        source_node_id=" point-1 ",
        source_text=(
            "Credit institution shall report."
        ),
    )
    actors = EurLexLegalActors(
        actors=(actor,),
        mentions=(mention,),
    )

    assert actor.canonical_name == (
        "credit institution"
    )
    assert actor.definition_id == (
        "definition-1"
    )
    assert actors.actor_by_name(
        "Credit Institution"
    ) == actor
    assert actors.mentions_for_actor(
        "actor-1"
    ) == (mention,)


def test_container_queries_actor_kind_and_requirement() -> None:
    actor = EurLexLegalActor(
        actor_id="actor-1",
        canonical_name="Member State",
        source_label="Member State",
        kind=(
            EurLexLegalActorKind.MEMBER_STATE
        ),
        language=LanguageCode("en"),
    )
    mention = EurLexLegalActorMention(
        mention_id="mention-1",
        actor_id="actor-1",
        source_requirement_id="requirement-1",
        source_node_id="point-1",
        source_text=(
            "Member State shall notify "
            "the Commission."
        ),
    )
    actors = EurLexLegalActors(
        actors=(actor,),
        mentions=(mention,),
    )

    assert actors.actor_by_id(
        "actor-1"
    ) == actor
    assert actors.actors_by_kind(
        EurLexLegalActorKind.MEMBER_STATE
    ) == (actor,)
    assert actors.actors_for_requirement(
        "requirement-1"
    ) == (actor,)


def test_rejects_mentions_for_unknown_actor() -> None:
    with pytest.raises(
        ValueError,
        match="existing actors",
    ):
        EurLexLegalActors(
            mentions=(
                EurLexLegalActorMention(
                    mention_id="mention-1",
                    actor_id="actor-1",
                    source_requirement_id=(
                        "requirement-1"
                    ),
                    source_node_id="point-1",
                    source_text=(
                        "Institution shall report."
                    ),
                ),
            )
        )
