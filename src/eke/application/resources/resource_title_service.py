"""Application service for Resource title use cases."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date

from eke.application.resources.exceptions import (
    ResourceNotFoundError,
    ResourceTitleAlreadyExistsError,
    ResourceTitleNotFoundError,
)
from eke.application.unit_of_work import UnitOfWork
from eke.domain.identity import ResourceUUID
from eke.domain.localization import LanguageCode
from eke.domain.resources import Resource, ResourceTitle


class ResourceTitleService:
    """Coordinate title operations on Resource aggregates."""

    def __init__(self, unit_of_work_factory: Callable[[], UnitOfWork]) -> None:
        if not callable(unit_of_work_factory):
            raise TypeError("unit_of_work_factory must be callable")
        self._unit_of_work_factory = unit_of_work_factory

    def list(self, resource_uuid: ResourceUUID) -> tuple[ResourceTitle, ...]:
        self._validate_resource_uuid(resource_uuid)
        with self._unit_of_work_factory() as uow:
            resource = uow.resources.get(resource_uuid)
            if resource is None:
                raise ResourceNotFoundError(f"resource not found: {resource_uuid}")
            return resource.titles

    def add(self, resource_uuid: ResourceUUID, title: ResourceTitle) -> ResourceTitle:
        self._validate_resource_uuid(resource_uuid)
        if not isinstance(title, ResourceTitle):
            raise TypeError("title must be a ResourceTitle")

        with self._unit_of_work_factory() as uow:
            resource = uow.resources.get(resource_uuid)
            if resource is None:
                raise ResourceNotFoundError(f"resource not found: {resource_uuid}")
            if title in resource.titles:
                raise ResourceTitleAlreadyExistsError("resource title already exists")

            uow.resources.save(_replace_titles(resource, (*resource.titles, title)))
            uow.commit()
            return title

    def remove(
        self,
        resource_uuid: ResourceUUID,
        language: LanguageCode,
        valid_from: date | None,
        valid_to: date | None,
    ) -> None:
        self._validate_resource_uuid(resource_uuid)
        if not isinstance(language, LanguageCode):
            raise TypeError("language must be a LanguageCode")

        with self._unit_of_work_factory() as uow:
            resource = uow.resources.get(resource_uuid)
            if resource is None:
                raise ResourceNotFoundError(f"resource not found: {resource_uuid}")

            remaining = tuple(
                title
                for title in resource.titles
                if not (
                    title.text.language == language
                    and title.validity.valid_from == valid_from
                    and title.validity.valid_to == valid_to
                )
            )
            if len(remaining) == len(resource.titles):
                raise ResourceTitleNotFoundError("resource title not found")

            uow.resources.save(_replace_titles(resource, remaining))
            uow.commit()

    @staticmethod
    def _validate_resource_uuid(resource_uuid: ResourceUUID) -> None:
        if not isinstance(resource_uuid, ResourceUUID):
            raise TypeError("resource_uuid must be a ResourceUUID")


def _replace_titles(
    resource: Resource,
    titles: tuple[ResourceTitle, ...],
) -> Resource:
    return Resource(
        resource_uuid=resource.resource_uuid,
        identifiers=resource.identifiers,
        resource_type=resource.resource_type,
        status=resource.status,
        titles=titles,
        versions=resource.versions,
        relationships=resource.relationships,
        provenance_records=resource.provenance_records,
        classifications=resource.classifications,
    )
