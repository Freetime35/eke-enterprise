from datetime import date

import pytest

from eke.application.resources import (
    ResourceTitleAlreadyExistsError,
    ResourceTitleNotFoundError,
    ResourceTitleService,
)
from eke.domain.identity import BusinessIdentifier, IdentifierScheme, ResourceUUID
from eke.domain.localization import LanguageCode, LocalizedText
from eke.domain.resources import Resource, ResourceTitle
from eke.domain.temporal import ValidityPeriod
from eke.infrastructure.repositories import InMemoryResourceRepository
from eke.infrastructure.unit_of_work import InMemoryUnitOfWork


def make_title() -> ResourceTitle:
    return ResourceTitle(
        LocalizedText(LanguageCode("fr"), "Titre français"),
        ValidityPeriod(date(2024, 1, 1), None),
    )


def make_service() -> tuple[
    ResourceTitleService,
    InMemoryResourceRepository,
    Resource,
]:
    repository = InMemoryResourceRepository()
    resource = Resource(
        ResourceUUID.generate(),
        (BusinessIdentifier(IdentifierScheme.CELEX, "32023R1114"),),
    )
    repository.save(resource)
    return (
        ResourceTitleService(lambda: InMemoryUnitOfWork(repository)),
        repository,
        resource,
    )


def test_add_and_list_title() -> None:
    service, _, resource = make_service()
    title = make_title()
    service.add(resource.resource_uuid, title)
    assert service.list(resource.resource_uuid) == (title,)


def test_duplicate_title_is_rejected() -> None:
    service, _, resource = make_service()
    title = make_title()
    service.add(resource.resource_uuid, title)
    with pytest.raises(ResourceTitleAlreadyExistsError):
        service.add(resource.resource_uuid, title)


def test_remove_title() -> None:
    service, _, resource = make_service()
    service.add(resource.resource_uuid, make_title())
    service.remove(
        resource.resource_uuid,
        LanguageCode("fr"),
        date(2024, 1, 1),
        None,
    )
    assert service.list(resource.resource_uuid) == ()


def test_remove_missing_title_is_rejected() -> None:
    service, _, resource = make_service()
    with pytest.raises(ResourceTitleNotFoundError):
        service.remove(
            resource.resource_uuid,
            LanguageCode("fr"),
            date(2024, 1, 1),
            None,
        )
