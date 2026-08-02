"""Deterministic legal actors derived from explicit legal subjects."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from eke.domain.localization import LanguageCode


def _normalize_required_text(
    value: str,
    *,
    name: str,
) -> str:
    if not isinstance(value, str):
        raise TypeError(
            f"{name} must be a string"
        )

    normalized = " ".join(value.split())
    if not normalized:
        raise ValueError(
            f"{name} must not be empty"
        )

    return normalized


def _normalize_optional_text(
    value: str | None,
    *,
    name: str,
) -> str | None:
    if value is None:
        return None

    if not isinstance(value, str):
        raise TypeError(
            f"{name} must be a string or None"
        )

    normalized = " ".join(value.split())
    return normalized or None


class EurLexLegalActorKind(StrEnum):
    """Canonical kinds of explicit legal actors."""

    EU_INSTITUTION = "EU_INSTITUTION"
    MEMBER_STATE = "MEMBER_STATE"
    COMPETENT_AUTHORITY = "COMPETENT_AUTHORITY"
    REGULATED_ENTITY = "REGULATED_ENTITY"
    NATURAL_PERSON = "NATURAL_PERSON"
    LEGAL_PERSON = "LEGAL_PERSON"
    APPLICANT = "APPLICANT"
    OPERATOR = "OPERATOR"
    GENERIC_ACTOR = "GENERIC_ACTOR"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class EurLexLegalActor:
    """Represent one normalized legal actor."""

    actor_id: str
    canonical_name: str
    source_label: str
    kind: EurLexLegalActorKind
    language: LanguageCode
    definition_id: str | None = None

    def __post_init__(self) -> None:
        for name in (
            "actor_id",
            "canonical_name",
            "source_label",
        ):
            object.__setattr__(
                self,
                name,
                _normalize_required_text(
                    getattr(self, name),
                    name=name,
                ),
            )

        object.__setattr__(
            self,
            "definition_id",
            _normalize_optional_text(
                self.definition_id,
                name="definition_id",
            ),
        )

        if not isinstance(
            self.kind,
            EurLexLegalActorKind,
        ):
            raise TypeError(
                "kind must be an "
                "EurLexLegalActorKind"
            )

        if not isinstance(
            self.language,
            LanguageCode,
        ):
            raise TypeError(
                "language must be a LanguageCode"
            )

    @property
    def normalized_name(self) -> str:
        """Return a case-insensitive actor lookup key."""
        return self.canonical_name.casefold()


@dataclass(frozen=True, slots=True)
class EurLexLegalActorMention:
    """Represent one requirement-level mention of an actor."""

    mention_id: str
    actor_id: str
    source_requirement_id: str
    source_node_id: str
    source_text: str

    def __post_init__(self) -> None:
        for name in (
            "mention_id",
            "actor_id",
            "source_requirement_id",
            "source_node_id",
            "source_text",
        ):
            object.__setattr__(
                self,
                name,
                _normalize_required_text(
                    getattr(self, name),
                    name=name,
                ),
            )


@dataclass(frozen=True, slots=True)
class EurLexLegalActors:
    """Contain legal actors and their requirement mentions."""

    actors: tuple[
        EurLexLegalActor,
        ...,
    ] = ()
    mentions: tuple[
        EurLexLegalActorMention,
        ...,
    ] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.actors, tuple):
            raise TypeError(
                "actors must be a tuple"
            )
        if not isinstance(self.mentions, tuple):
            raise TypeError(
                "mentions must be a tuple"
            )

        if any(
            not isinstance(
                actor,
                EurLexLegalActor,
            )
            for actor in self.actors
        ):
            raise TypeError(
                "actors must contain "
                "EurLexLegalActor values"
            )

        if any(
            not isinstance(
                mention,
                EurLexLegalActorMention,
            )
            for mention in self.mentions
        ):
            raise TypeError(
                "mentions must contain "
                "EurLexLegalActorMention values"
            )

        actor_ids = tuple(
            actor.actor_id
            for actor in self.actors
        )
        if len(actor_ids) != len(
            set(actor_ids)
        ):
            raise ValueError(
                "actor identifiers must be unique"
            )

        mention_ids = tuple(
            mention.mention_id
            for mention in self.mentions
        )
        if len(mention_ids) != len(
            set(mention_ids)
        ):
            raise ValueError(
                "mention identifiers must be unique"
            )

        known_actor_ids = set(actor_ids)
        if any(
            mention.actor_id
            not in known_actor_ids
            for mention in self.mentions
        ):
            raise ValueError(
                "mentions must reference "
                "existing actors"
            )

    def actor_by_id(
        self,
        actor_id: str,
    ) -> EurLexLegalActor | None:
        """Return one actor by identifier."""
        normalized = _normalize_required_text(
            actor_id,
            name="actor_id",
        )

        return next(
            (
                actor
                for actor in self.actors
                if actor.actor_id == normalized
            ),
            None,
        )

    def actor_by_name(
        self,
        canonical_name: str,
    ) -> EurLexLegalActor | None:
        """Return one actor by exact normalized name."""
        normalized = _normalize_required_text(
            canonical_name,
            name="canonical_name",
        ).casefold()

        return next(
            (
                actor
                for actor in self.actors
                if actor.normalized_name
                == normalized
            ),
            None,
        )

    def actors_by_kind(
        self,
        kind: EurLexLegalActorKind,
    ) -> tuple[EurLexLegalActor, ...]:
        """Return actors of one kind."""
        if not isinstance(
            kind,
            EurLexLegalActorKind,
        ):
            raise TypeError(
                "kind must be an "
                "EurLexLegalActorKind"
            )

        return tuple(
            actor
            for actor in self.actors
            if actor.kind is kind
        )

    def mentions_for_actor(
        self,
        actor_id: str,
    ) -> tuple[EurLexLegalActorMention, ...]:
        """Return mentions of one actor."""
        normalized = _normalize_required_text(
            actor_id,
            name="actor_id",
        )

        return tuple(
            mention
            for mention in self.mentions
            if mention.actor_id == normalized
        )

    def actors_for_requirement(
        self,
        source_requirement_id: str,
    ) -> tuple[EurLexLegalActor, ...]:
        """Return actors mentioned by one requirement."""
        normalized = _normalize_required_text(
            source_requirement_id,
            name="source_requirement_id",
        )
        actor_ids = {
            mention.actor_id
            for mention in self.mentions
            if mention.source_requirement_id
            == normalized
        }

        return tuple(
            actor
            for actor in self.actors
            if actor.actor_id in actor_ids
        )
