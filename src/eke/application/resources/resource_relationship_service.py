"""Application service for Resource relationship use cases."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date

from eke.application.resources.exceptions import (
    ResourceNotFoundError,
    ResourceRelationshipAlreadyExistsError,
    ResourceRelationshipConflictError,
    ResourceRelationshipNotFoundError,
)
from eke.application.unit_of_work import UnitOfWork
from eke.domain.identity import ResourceUUID
from eke.domain.relationships import (
    RelationshipType,
    ResourceRelationship,
)
from eke.domain.resources import Resource


class ResourceRelationshipService:
    """Coordinate outgoing Resource relationship operations."""

    def __init__(
        self,
        unit_of_work_factory: Callable[[], UnitOfWork],
    ) -> None:
        if not callable(unit_of_work_factory):
            raise TypeError("unit_of_work_factory must be callable")
        self._unit_of_work_factory = unit_of_work_factory

    def list(
        self,
        source_uuid: ResourceUUID,
    ) -> tuple[ResourceRelationship, ...]:
        """Return outgoing relationships of a Resource."""
        self._validate_resource_uuid(source_uuid)

        with self._unit_of_work_factory() as uow:
            source = uow.resources.get(source_uuid)
            if source is None:
                raise ResourceNotFoundError(
                    f"resource not found: {source_uuid}"
                )
            return source.relationships

    def add(
        self,
        source_uuid: ResourceUUID,
        relationship: ResourceRelationship,
    ) -> ResourceRelationship:
        """Add an outgoing relationship to a Resource."""
        self._validate_resource_uuid(source_uuid)
        if not isinstance(relationship, ResourceRelationship):
            raise TypeError(
                "relationship must be a ResourceRelationship"
            )
        if relationship.source != source_uuid:
            raise ResourceRelationshipConflictError(
                "relationship source does not match the resource"
            )

        with self._unit_of_work_factory() as uow:
            source = uow.resources.get(source_uuid)
            if source is None:
                raise ResourceNotFoundError(
                    f"resource not found: {source_uuid}"
                )

            if (
                uow.resources.get(relationship.target)
                is None
            ):
                raise ResourceRelationshipConflictError(
                    "target resource does not exist"
                )

            if relationship in source.relationships:
                raise ResourceRelationshipAlreadyExistsError(
                    "resource relationship already exists"
                )

            updated = _replace_relationships(
                source,
                (*source.relationships, relationship),
            )
            uow.resources.save(updated)
            uow.commit()
            return relationship

    def remove(
        self,
        source_uuid: ResourceUUID,
        target_uuid: ResourceUUID,
        relationship_type: RelationshipType,
        valid_from: date | None,
        valid_to: date | None,
    ) -> None:
        """Remove one outgoing relationship."""
        self._validate_resource_uuid(source_uuid)
        self._validate_resource_uuid(target_uuid)
        if not isinstance(
            relationship_type,
            RelationshipType,
        ):
            raise TypeError(
                "relationship_type must be a RelationshipType"
            )

        with self._unit_of_work_factory() as uow:
            source = uow.resources.get(source_uuid)
            if source is None:
                raise ResourceNotFoundError(
                    f"resource not found: {source_uuid}"
                )

            remaining = tuple(
                relationship
                for relationship in source.relationships
                if not _matches(
                    relationship,
                    target_uuid,
                    relationship_type,
                    valid_from,
                    valid_to,
                )
            )
            if len(remaining) == len(source.relationships):
                raise ResourceRelationshipNotFoundError(
                    "resource relationship not found"
                )

            uow.resources.save(
                _replace_relationships(source, remaining)
            )
            uow.commit()

    @staticmethod
    def _validate_resource_uuid(
        resource_uuid: ResourceUUID,
    ) -> None:
        if not isinstance(resource_uuid, ResourceUUID):
            raise TypeError(
                "resource_uuid must be a ResourceUUID"
            )


def _matches(
    relationship: ResourceRelationship,
    target_uuid: ResourceUUID,
    relationship_type: RelationshipType,
    valid_from: date | None,
    valid_to: date | None,
) -> bool:
    return (
        relationship.target == target_uuid
        and relationship.relationship_type
        is relationship_type
        and relationship.validity.valid_from == valid_from
        and relationship.validity.valid_to == valid_to
    )


def _replace_relationships(
    resource: Resource,
    relationships: tuple[ResourceRelationship, ...],
) -> Resource:
    return Resource(
        resource_uuid=resource.resource_uuid,
        identifiers=resource.identifiers,
        resource_type=resource.resource_type,
        status=resource.status,
        titles=resource.titles,
        versions=resource.versions,
        relationships=relationships,
        provenance_records=resource.provenance_records,
        classifications=resource.classifications,
    )
