"""Application service for Resource version use cases."""

from __future__ import annotations

from collections.abc import Callable

from eke.application.resources.exceptions import (
    ResourceNotFoundError,
    ResourceVersionAlreadyExistsError,
    ResourceVersionConflictError,
    ResourceVersionNotFoundError,
)
from eke.application.unit_of_work import UnitOfWork
from eke.domain.identity import ResourceUUID, ResourceVersionUUID
from eke.domain.resources import Resource, ResourceVersion


class ResourceVersionService:
    """Coordinate version operations on Resource aggregates."""

    def __init__(
        self,
        unit_of_work_factory: Callable[[], UnitOfWork],
    ) -> None:
        if not callable(unit_of_work_factory):
            raise TypeError("unit_of_work_factory must be callable")
        self._unit_of_work_factory = unit_of_work_factory

    def list(
        self,
        resource_uuid: ResourceUUID,
    ) -> tuple[ResourceVersion, ...]:
        """Return all versions of a Resource."""
        resource = self._get_resource(resource_uuid)
        return resource.versions

    def get(
        self,
        resource_uuid: ResourceUUID,
        version_uuid: ResourceVersionUUID,
    ) -> ResourceVersion:
        """Return one ResourceVersion."""
        resource = self._get_resource(resource_uuid)
        version = _find_version(resource, version_uuid)
        if version is None:
            raise ResourceVersionNotFoundError(
                f"resource version not found: {version_uuid}"
            )
        return version

    def add(
        self,
        resource_uuid: ResourceUUID,
        version: ResourceVersion,
    ) -> ResourceVersion:
        """Add a version to an existing Resource."""
        self._validate_resource_uuid(resource_uuid)
        if not isinstance(version, ResourceVersion):
            raise TypeError("version must be a ResourceVersion")
        if version.resource_uuid != resource_uuid:
            raise ResourceVersionConflictError(
                "resource version belongs to another resource"
            )

        with self._unit_of_work_factory() as uow:
            resource = uow.resources.get(resource_uuid)
            if resource is None:
                raise ResourceNotFoundError(
                    f"resource not found: {resource_uuid}"
                )

            if _find_version(resource, version.version_uuid) is not None:
                raise ResourceVersionAlreadyExistsError(
                    "resource version already exists"
                )

            if version.previous_version_uuid is not None:
                previous = _find_version(
                    resource,
                    version.previous_version_uuid,
                )
                if previous is None:
                    raise ResourceVersionConflictError(
                        "previous resource version does not exist"
                    )

            updated = _replace_versions(
                resource,
                (*resource.versions, version),
            )
            uow.resources.save(updated)
            uow.commit()
            return version

    def remove(
        self,
        resource_uuid: ResourceUUID,
        version_uuid: ResourceVersionUUID,
    ) -> None:
        """Remove a version that has no successor."""
        self._validate_resource_uuid(resource_uuid)
        self._validate_version_uuid(version_uuid)

        with self._unit_of_work_factory() as uow:
            resource = uow.resources.get(resource_uuid)
            if resource is None:
                raise ResourceNotFoundError(
                    f"resource not found: {resource_uuid}"
                )

            if _find_version(resource, version_uuid) is None:
                raise ResourceVersionNotFoundError(
                    f"resource version not found: {version_uuid}"
                )

            if any(
                version.previous_version_uuid == version_uuid
                for version in resource.versions
            ):
                raise ResourceVersionConflictError(
                    "resource version is referenced by a successor"
                )

            remaining = tuple(
                version
                for version in resource.versions
                if version.version_uuid != version_uuid
            )
            uow.resources.save(
                _replace_versions(resource, remaining)
            )
            uow.commit()

    def _get_resource(
        self,
        resource_uuid: ResourceUUID,
    ) -> Resource:
        self._validate_resource_uuid(resource_uuid)
        with self._unit_of_work_factory() as uow:
            resource = uow.resources.get(resource_uuid)
            if resource is None:
                raise ResourceNotFoundError(
                    f"resource not found: {resource_uuid}"
                )
            return resource

    @staticmethod
    def _validate_resource_uuid(
        resource_uuid: ResourceUUID,
    ) -> None:
        if not isinstance(resource_uuid, ResourceUUID):
            raise TypeError("resource_uuid must be a ResourceUUID")

    @staticmethod
    def _validate_version_uuid(
        version_uuid: ResourceVersionUUID,
    ) -> None:
        if not isinstance(version_uuid, ResourceVersionUUID):
            raise TypeError(
                "version_uuid must be a ResourceVersionUUID"
            )


def _find_version(
    resource: Resource,
    version_uuid: ResourceVersionUUID,
) -> ResourceVersion | None:
    return next(
        (
            version
            for version in resource.versions
            if version.version_uuid == version_uuid
        ),
        None,
    )


def _replace_versions(
    resource: Resource,
    versions: tuple[ResourceVersion, ...],
) -> Resource:
    return Resource(
        resource_uuid=resource.resource_uuid,
        identifiers=resource.identifiers,
        resource_type=resource.resource_type,
        status=resource.status,
        titles=resource.titles,
        versions=versions,
        relationships=resource.relationships,
        provenance_records=resource.provenance_records,
        classifications=resource.classifications,
    )
