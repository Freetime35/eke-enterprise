from datetime import date

import pytest

from eke.application.resources import (
    ResourceClassificationAlreadyExistsError,
    ResourceClassificationNotFoundError,
    ResourceClassificationService,
)
from eke.domain.classification import (
    ClassificationConcept,
    ClassificationScheme,
)
from eke.domain.identity import (
    BusinessIdentifier,
    IdentifierScheme,
    ResourceUUID,
)
from eke.domain.localization import (
    LanguageCode,
    LocalizedText,
)
from eke.domain.resources import Resource
from eke.domain.temporal import ValidityPeriod
from eke.infrastructure.repositories import (
    InMemoryResourceRepository,
)
from eke.infrastructure.unit_of_work import InMemoryUnitOfWork


def make_service() -> tuple[
    ResourceClassificationService,
    Resource,
]:
    repository = InMemoryResourceRepository()
    resource = Resource(
        ResourceUUID.generate(),
        (
            BusinessIdentifier(
                IdentifierScheme.CELEX,
                "32023R1114",
            ),
        ),
    )
    repository.save(resource)
    return (
        ResourceClassificationService(
            lambda: InMemoryUnitOfWork(repository)
        ),
        resource,
    )


def make_classification() -> ClassificationConcept:
    return ClassificationConcept(
        scheme=ClassificationScheme.EUROVOC,
        code="1001",
        label=LocalizedText(
            LanguageCode("fr"),
            "Marchés financiers",
        ),
        validity=ValidityPeriod(
            date(2024, 1, 1),
            None,
        ),
    )


def test_add_and_list_classification() -> None:
    service, resource = make_service()
    classification = make_classification()

    service.add(resource.resource_uuid, classification)

    assert service.list(resource.resource_uuid) == (
        classification,
    )


def test_duplicate_classification_key_is_rejected() -> None:
    service, resource = make_service()
    classification = make_classification()
    service.add(resource.resource_uuid, classification)

    conflicting = ClassificationConcept(
        scheme=classification.scheme,
        code=classification.code,
        label=LocalizedText(
            classification.language,
            "Libellé différent",
        ),
    )
    with pytest.raises(
        ResourceClassificationAlreadyExistsError
    ):
        service.add(resource.resource_uuid, conflicting)


def test_remove_classification() -> None:
    service, resource = make_service()
    classification = make_classification()
    service.add(resource.resource_uuid, classification)

    service.remove(
        resource.resource_uuid,
        classification.scheme,
        classification.code,
        classification.language,
    )

    assert service.list(resource.resource_uuid) == ()


def test_remove_missing_classification_is_rejected() -> None:
    service, resource = make_service()

    with pytest.raises(
        ResourceClassificationNotFoundError
    ):
        service.remove(
            resource.resource_uuid,
            ClassificationScheme.EUROVOC,
            "1001",
            LanguageCode("fr"),
        )
