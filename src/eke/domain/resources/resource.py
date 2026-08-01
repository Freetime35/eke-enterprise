"""Resource aggregate root.

This module defines the canonical Resource aggregate root used by
EKE Enterprise.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from eke.domain.identity import (
    BusinessIdentifier,
    IdentifierScheme,
    ResourceUUID,
    ResourceVersionUUID,
)
from eke.domain.localization import LanguageCode
from eke.domain.relationships import (
    RelationshipType,
    ResourceRelationship,
)
from eke.domain.resources.resource_status import ResourceStatus
from eke.domain.resources.resource_title import ResourceTitle
from eke.domain.resources.resource_type import ResourceType
from eke.domain.resources.resource_version import ResourceVersion


@dataclass(frozen=True, slots=True)
class Resource:
    """Represent a canonical resource managed by EKE Enterprise.

    A Resource owns one immutable internal identifier, one or more
    external business identifiers, a canonical type and lifecycle
    status, optional title and version collections, and directed
    relationships that originate from the resource.

    Attributes:
        resource_uuid: Immutable internal resource identity.
        identifiers: External business identifiers assigned to the resource.
        resource_type: Canonical legal or documentary type.
        status: Canonical lifecycle status.
        titles: Localized temporal titles owned by the resource.
        versions: Canonical versions owned by the resource.
        relationships: Directed relationships originating from the resource.
    """

    resource_uuid: ResourceUUID
    identifiers: tuple[BusinessIdentifier, ...]
    resource_type: ResourceType = ResourceType.OTHER
    status: ResourceStatus = ResourceStatus.UNKNOWN
    titles: tuple[ResourceTitle, ...] = ()
    versions: tuple[ResourceVersion, ...] = ()
    relationships: tuple[ResourceRelationship, ...] = ()

    def __post_init__(self) -> None:
        """Validate aggregate invariants."""
        if not isinstance(self.resource_uuid, ResourceUUID):
            raise TypeError("resource_uuid must be a ResourceUUID")

        self._validate_identifiers()
        self._validate_resource_type_and_status()
        self._validate_titles()
        self._validate_versions()
        self._validate_relationships()

    def _validate_identifiers(self) -> None:
        if not isinstance(self.identifiers, tuple):
            raise TypeError("identifiers must be a tuple")

        if not self.identifiers:
            raise ValueError(
                "a resource must have at least one business identifier"
            )

        if not all(
            isinstance(identifier, BusinessIdentifier)
            for identifier in self.identifiers
        ):
            raise TypeError(
                "identifiers must contain only BusinessIdentifier instances"
            )

        if len(set(self.identifiers)) != len(self.identifiers):
            raise ValueError("business identifiers must be unique")

        schemes = tuple(
            identifier.scheme for identifier in self.identifiers
        )
        if len(set(schemes)) != len(schemes):
            raise ValueError(
                "a resource must not contain multiple identifiers "
                "for the same scheme"
            )

    def _validate_resource_type_and_status(self) -> None:
        if not isinstance(self.resource_type, ResourceType):
            raise TypeError("resource_type must be a ResourceType")

        if not isinstance(self.status, ResourceStatus):
            raise TypeError("status must be a ResourceStatus")

    def _validate_titles(self) -> None:
        if not isinstance(self.titles, tuple):
            raise TypeError("titles must be a tuple")

        if not all(
            isinstance(title, ResourceTitle) for title in self.titles
        ):
            raise TypeError(
                "titles must contain only ResourceTitle instances"
            )

        if len(set(self.titles)) != len(self.titles):
            raise ValueError("resource titles must be unique")

        for index, title in enumerate(self.titles):
            for other in self.titles[index + 1 :]:
                if title.overlaps(other):
                    raise ValueError(
                        "resource titles in the same language "
                        "must not have overlapping validity periods"
                    )

    def _validate_versions(self) -> None:
        if not isinstance(self.versions, tuple):
            raise TypeError("versions must be a tuple")

        if not all(
            isinstance(version, ResourceVersion)
            for version in self.versions
        ):
            raise TypeError(
                "versions must contain only ResourceVersion instances"
            )

        version_ids = tuple(
            version.version_uuid for version in self.versions
        )
        if len(set(version_ids)) != len(version_ids):
            raise ValueError("resource version identities must be unique")

        if not all(
            version.belongs_to(self.resource_uuid)
            for version in self.versions
        ):
            raise ValueError(
                "all resource versions must belong to the resource"
            )

        known_version_ids = set(version_ids)
        for version in self.versions:
            previous = version.previous_version_uuid
            if (
                previous is not None
                and previous not in known_version_ids
            ):
                raise ValueError(
                    "previous resource version must belong to "
                    "the same aggregate"
                )

    def _validate_relationships(self) -> None:
        if not isinstance(self.relationships, tuple):
            raise TypeError("relationships must be a tuple")

        if not all(
            isinstance(relationship, ResourceRelationship)
            for relationship in self.relationships
        ):
            raise TypeError(
                "relationships must contain only "
                "ResourceRelationship instances"
            )

        if len(set(self.relationships)) != len(self.relationships):
            raise ValueError("resource relationships must be unique")

        if not all(
            relationship.originates_from(self.resource_uuid)
            for relationship in self.relationships
        ):
            raise ValueError(
                "all resource relationships must originate "
                "from the resource"
            )

    def has_identifier(self, identifier: BusinessIdentifier) -> bool:
        """Return whether the resource owns the given identifier."""
        if not isinstance(identifier, BusinessIdentifier):
            raise TypeError(
                "identifier must be a BusinessIdentifier"
            )

        return identifier in self.identifiers

    def find_identifier(
        self,
        scheme: IdentifierScheme,
    ) -> BusinessIdentifier | None:
        """Find the business identifier assigned under a scheme."""
        if not isinstance(scheme, IdentifierScheme):
            raise TypeError("scheme must be an IdentifierScheme")

        return next(
            (
                identifier
                for identifier in self.identifiers
                if identifier.scheme is scheme
            ),
            None,
        )

    def has_identifier_scheme(
        self,
        scheme: IdentifierScheme,
    ) -> bool:
        """Return whether the resource has an identifier for a scheme."""
        return self.find_identifier(scheme) is not None

    def titles_for_language(
        self,
        language: LanguageCode,
    ) -> tuple[ResourceTitle, ...]:
        """Return all titles for a language in aggregate order."""
        if not isinstance(language, LanguageCode):
            raise TypeError("language must be a LanguageCode")

        return tuple(
            title
            for title in self.titles
            if title.has_language(language)
        )

    def title_valid_on(
        self,
        language: LanguageCode,
        value: date,
    ) -> ResourceTitle | None:
        """Return the title valid for a language on a date."""
        if not isinstance(language, LanguageCode):
            raise TypeError("language must be a LanguageCode")

        if not isinstance(value, date):
            raise TypeError("value must be a date")

        return next(
            (
                title
                for title in self.titles
                if title.has_language(language)
                and title.is_valid_on(value)
            ),
            None,
        )

    def has_version(
        self,
        version_uuid: ResourceVersionUUID,
    ) -> bool:
        """Return whether the aggregate owns a version identity."""
        return self.find_version(version_uuid) is not None

    def find_version(
        self,
        version_uuid: ResourceVersionUUID,
    ) -> ResourceVersion | None:
        """Find a version by its internal identity."""
        if not isinstance(version_uuid, ResourceVersionUUID):
            raise TypeError(
                "version_uuid must be a ResourceVersionUUID"
            )

        return next(
            (
                version
                for version in self.versions
                if version.version_uuid == version_uuid
            ),
            None,
        )

    def versions_valid_on(
        self,
        value: date,
    ) -> tuple[ResourceVersion, ...]:
        """Return all versions valid on a date."""
        if not isinstance(value, date):
            raise TypeError("value must be a date")

        return tuple(
            version
            for version in self.versions
            if version.is_valid_on(value)
        )

    def relationships_of_type(
        self,
        relationship_type: RelationshipType,
    ) -> tuple[ResourceRelationship, ...]:
        """Return relationships matching a canonical type."""
        if not isinstance(relationship_type, RelationshipType):
            raise TypeError(
                "relationship_type must be a RelationshipType"
            )

        return tuple(
            relationship
            for relationship in self.relationships
            if relationship.relationship_type is relationship_type
        )

    def relationships_to(
        self,
        target: ResourceUUID,
    ) -> tuple[ResourceRelationship, ...]:
        """Return relationships pointing to a target resource."""
        if not isinstance(target, ResourceUUID):
            raise TypeError("target must be a ResourceUUID")

        return tuple(
            relationship
            for relationship in self.relationships
            if relationship.points_to(target)
        )

    def active_relationships_on(
        self,
        value: date,
    ) -> tuple[ResourceRelationship, ...]:
        """Return relationships active on a date."""
        if not isinstance(value, date):
            raise TypeError("value must be a date")

        return tuple(
            relationship
            for relationship in self.relationships
            if relationship.is_active_on(value)
        )
