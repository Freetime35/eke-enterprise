from __future__ import annotations

from collections.abc import Callable

from eke.application.resources.exceptions import (
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
)
from eke.application.unit_of_work import UnitOfWork
from eke.domain.identity import BusinessIdentifier, ResourceUUID
from eke.domain.resources import Resource


class ResourceService:
    """Coordinate transactional application use cases for Resources."""

    def __init__(self, unit_of_work_factory: Callable[[], UnitOfWork]) -> None:
        if not callable(unit_of_work_factory):
            raise TypeError("unit_of_work_factory must be callable")
        self._unit_of_work_factory = unit_of_work_factory

    def create(self, resource: Resource) -> None:
        self._validate_resource(resource)

        with self._unit_of_work_factory() as uow:
            if uow.resources.exists(resource.resource_uuid):
                raise ResourceAlreadyExistsError(
                    f"resource already exists: {resource.resource_uuid}"
                )

            for identifier in resource.identifiers:
                if uow.resources.get_by_identifier(identifier) is not None:
                    raise ResourceAlreadyExistsError(
                        "resource already exists for business identifier: "
                        f"{identifier}"
                    )

            uow.resources.save(resource)
            uow.commit()

    def get(self, resource_uuid: ResourceUUID) -> Resource:
        self._validate_resource_uuid(resource_uuid)

        with self._unit_of_work_factory() as uow:
            resource = uow.resources.get(resource_uuid)
            if resource is None:
                raise ResourceNotFoundError(
                    f"resource not found: {resource_uuid}"
                )
            return resource

    def find_by_identifier(
        self,
        identifier: BusinessIdentifier,
    ) -> Resource:
        self._validate_identifier(identifier)

        with self._unit_of_work_factory() as uow:
            resource = uow.resources.get_by_identifier(identifier)
            if resource is None:
                raise ResourceNotFoundError(
                    "resource not found for business identifier: "
                    f"{identifier}"
                )
            return resource

    def update(self, resource: Resource) -> None:
        self._validate_resource(resource)

        with self._unit_of_work_factory() as uow:
            if not uow.resources.exists(resource.resource_uuid):
                raise ResourceNotFoundError(
                    f"resource not found: {resource.resource_uuid}"
                )

            for identifier in resource.identifiers:
                existing = uow.resources.get_by_identifier(identifier)
                if (
                    existing is not None
                    and existing.resource_uuid != resource.resource_uuid
                ):
                    raise ResourceAlreadyExistsError(
                        "business identifier belongs to another resource: "
                        f"{identifier}"
                    )

            uow.resources.save(resource)
            uow.commit()

    def delete(self, resource_uuid: ResourceUUID) -> None:
        self._validate_resource_uuid(resource_uuid)

        with self._unit_of_work_factory() as uow:
            if not uow.resources.delete(resource_uuid):
                raise ResourceNotFoundError(
                    f"resource not found: {resource_uuid}"
                )
            uow.commit()

    def exists(self, resource_uuid: ResourceUUID) -> bool:
        self._validate_resource_uuid(resource_uuid)
        with self._unit_of_work_factory() as uow:
            return uow.resources.exists(resource_uuid)

    @staticmethod
    def _validate_resource(resource: Resource) -> None:
        if not isinstance(resource, Resource):
            raise TypeError("resource must be a Resource")

    @staticmethod
    def _validate_resource_uuid(resource_uuid: ResourceUUID) -> None:
        if not isinstance(resource_uuid, ResourceUUID):
            raise TypeError("resource_uuid must be a ResourceUUID")

    @staticmethod
    def _validate_identifier(identifier: BusinessIdentifier) -> None:
        if not isinstance(identifier, BusinessIdentifier):
            raise TypeError("identifier must be a BusinessIdentifier")
