"""Application service for Resource classification use cases."""

from __future__ import annotations

from collections.abc import Callable

from eke.application.resources.exceptions import (
    ResourceClassificationAlreadyExistsError,
    ResourceClassificationNotFoundError,
    ResourceNotFoundError,
)
from eke.application.unit_of_work import UnitOfWork
from eke.domain.classification import (
    ClassificationConcept,
    ClassificationScheme,
)
from eke.domain.identity import ResourceUUID
from eke.domain.localization import LanguageCode
from eke.domain.resources import Resource


class ResourceClassificationService:
    """Coordinate classification operations on Resource aggregates."""

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
    ) -> tuple[ClassificationConcept, ...]:
        """Return all classifications assigned to a Resource."""
        self._validate_resource_uuid(resource_uuid)

        with self._unit_of_work_factory() as uow:
            resource = uow.resources.get(resource_uuid)
            if resource is None:
                raise ResourceNotFoundError(
                    f"resource not found: {resource_uuid}"
                )
            return resource.classifications

    def add(
        self,
        resource_uuid: ResourceUUID,
        classification: ClassificationConcept,
    ) -> ClassificationConcept:
        """Assign one classification concept to a Resource."""
        self._validate_resource_uuid(resource_uuid)
        if not isinstance(
            classification,
            ClassificationConcept,
        ):
            raise TypeError(
                "classification must be a ClassificationConcept"
            )

        with self._unit_of_work_factory() as uow:
            resource = uow.resources.get(resource_uuid)
            if resource is None:
                raise ResourceNotFoundError(
                    f"resource not found: {resource_uuid}"
                )

            if any(
                _same_key(existing, classification)
                for existing in resource.classifications
            ):
                raise ResourceClassificationAlreadyExistsError(
                    "resource classification already exists"
                )

            updated = _replace_classifications(
                resource,
                (*resource.classifications, classification),
            )
            uow.resources.save(updated)
            uow.commit()
            return classification

    def remove(
        self,
        resource_uuid: ResourceUUID,
        scheme: ClassificationScheme,
        code: str,
        language: LanguageCode,
    ) -> None:
        """Remove one classification selected by its stable key."""
        self._validate_resource_uuid(resource_uuid)
        if not isinstance(scheme, ClassificationScheme):
            raise TypeError(
                "scheme must be a ClassificationScheme"
            )
        if not isinstance(code, str):
            raise TypeError("code must be a string")
        if not code.strip():
            raise ValueError("code must not be empty")
        if not isinstance(language, LanguageCode):
            raise TypeError(
                "language must be a LanguageCode"
            )

        with self._unit_of_work_factory() as uow:
            resource = uow.resources.get(resource_uuid)
            if resource is None:
                raise ResourceNotFoundError(
                    f"resource not found: {resource_uuid}"
                )

            remaining = tuple(
                classification
                for classification in resource.classifications
                if not (
                    classification.scheme is scheme
                    and classification.code == code
                    and classification.language == language
                )
            )
            if len(remaining) == len(
                resource.classifications
            ):
                raise ResourceClassificationNotFoundError(
                    "resource classification not found"
                )

            uow.resources.save(
                _replace_classifications(resource, remaining)
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


def _same_key(
    left: ClassificationConcept,
    right: ClassificationConcept,
) -> bool:
    return (
        left.scheme is right.scheme
        and left.code == right.code
        and left.language == right.language
    )


def _replace_classifications(
    resource: Resource,
    classifications: tuple[ClassificationConcept, ...],
) -> Resource:
    return Resource(
        resource_uuid=resource.resource_uuid,
        identifiers=resource.identifiers,
        resource_type=resource.resource_type,
        status=resource.status,
        titles=resource.titles,
        versions=resource.versions,
        relationships=resource.relationships,
        provenance_records=resource.provenance_records,
        classifications=classifications,
    )
