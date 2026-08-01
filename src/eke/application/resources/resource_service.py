"""Application service for Resource use cases.

This module orchestrates ResourceRepository operations without exposing
infrastructure concerns to callers.
"""

from __future__ import annotations

from eke.application.resources.exceptions import (
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
)
from eke.domain.identity import BusinessIdentifier, ResourceUUID
from eke.domain.repositories import ResourceRepository
from eke.domain.resources import Resource


class ResourceService:
    """Coordinate application use cases for Resource aggregates."""

    def __init__(self, repository: ResourceRepository) -> None:
        if not isinstance(repository, ResourceRepository):
            raise TypeError(
                "repository must satisfy ResourceRepository"
            )

        self._repository = repository

    def create(self, resource: Resource) -> None:
        """Create a new Resource aggregate.

        Raises:
            TypeError: If resource is not a Resource.
            ResourceAlreadyExistsError: If the identity already exists.
        """
        self._validate_resource(resource)

        if self._repository.exists(resource.resource_uuid):
            raise ResourceAlreadyExistsError(
                f"resource already exists: {resource.resource_uuid}"
            )

        existing = self._find_existing_identifier(resource)
        if existing is not None:
            raise ResourceAlreadyExistsError(
                "resource already exists for business identifier: "
                f"{existing}"
            )

        self._repository.save(resource)

    def get(self, resource_uuid: ResourceUUID) -> Resource:
        """Return a Resource by internal identity.

        Raises:
            TypeError: If resource_uuid is invalid.
            ResourceNotFoundError: If no Resource exists.
        """
        self._validate_resource_uuid(resource_uuid)

        resource = self._repository.get(resource_uuid)
        if resource is None:
            raise ResourceNotFoundError(
                f"resource not found: {resource_uuid}"
            )

        return resource

    def find_by_identifier(
        self,
        identifier: BusinessIdentifier,
    ) -> Resource:
        """Return a Resource by business identifier.

        Raises:
            TypeError: If identifier is invalid.
            ResourceNotFoundError: If no Resource exists.
        """
        self._validate_identifier(identifier)

        resource = self._repository.get_by_identifier(identifier)
        if resource is None:
            raise ResourceNotFoundError(
                "resource not found for business identifier: "
                f"{identifier}"
            )

        return resource

    def update(self, resource: Resource) -> None:
        """Replace an existing Resource aggregate.

        Raises:
            TypeError: If resource is invalid.
            ResourceNotFoundError: If the identity does not exist.
            ResourceAlreadyExistsError: If a business identifier belongs
                to another Resource.
        """
        self._validate_resource(resource)

        if not self._repository.exists(resource.resource_uuid):
            raise ResourceNotFoundError(
                f"resource not found: {resource.resource_uuid}"
            )

        for identifier in resource.identifiers:
            existing = self._repository.get_by_identifier(identifier)
            if (
                existing is not None
                and existing.resource_uuid != resource.resource_uuid
            ):
                raise ResourceAlreadyExistsError(
                    "business identifier belongs to another resource: "
                    f"{identifier}"
                )

        self._repository.save(resource)

    def delete(self, resource_uuid: ResourceUUID) -> None:
        """Delete an existing Resource aggregate.

        Raises:
            TypeError: If resource_uuid is invalid.
            ResourceNotFoundError: If no Resource exists.
        """
        self._validate_resource_uuid(resource_uuid)

        if not self._repository.delete(resource_uuid):
            raise ResourceNotFoundError(
                f"resource not found: {resource_uuid}"
            )

    def exists(self, resource_uuid: ResourceUUID) -> bool:
        """Return whether a Resource exists."""
        self._validate_resource_uuid(resource_uuid)
        return self._repository.exists(resource_uuid)

    def _find_existing_identifier(
        self,
        resource: Resource,
    ) -> BusinessIdentifier | None:
        for identifier in resource.identifiers:
            if self._repository.get_by_identifier(identifier) is not None:
                return identifier

        return None

    @staticmethod
    def _validate_resource(resource: Resource) -> None:
        if not isinstance(resource, Resource):
            raise TypeError("resource must be a Resource")

    @staticmethod
    def _validate_resource_uuid(
        resource_uuid: ResourceUUID,
    ) -> None:
        if not isinstance(resource_uuid, ResourceUUID):
            raise TypeError(
                "resource_uuid must be a ResourceUUID"
            )

    @staticmethod
    def _validate_identifier(
        identifier: BusinessIdentifier,
    ) -> None:
        if not isinstance(identifier, BusinessIdentifier):
            raise TypeError(
                "identifier must be a BusinessIdentifier"
            )
