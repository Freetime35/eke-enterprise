"""Tests for the enriched Resource aggregate root."""

from __future__ import annotations

from datetime import date

import pytest

from eke.domain.identity import (
    BusinessIdentifier,
    IdentifierScheme,
    ResourceUUID,
    ResourceVersionUUID,
)
from eke.domain.localization import LanguageCode, LocalizedText
from eke.domain.resources import (
    Resource,
    ResourceStatus,
    ResourceTitle,
    ResourceType,
    ResourceVersion,
)
from eke.domain.temporal import ValidityPeriod


def make_identifier() -> BusinessIdentifier:
    return BusinessIdentifier(
        IdentifierScheme.CELEX,
        "32023R1114",
    )


def make_resource_uuid() -> ResourceUUID:
    return ResourceUUID.generate()


def test_defaults_preserve_minimal_resource_construction() -> None:
    resource = Resource(
        resource_uuid=make_resource_uuid(),
        identifiers=(make_identifier(),),
    )

    assert resource.resource_type is ResourceType.OTHER
    assert resource.status is ResourceStatus.UNKNOWN
    assert resource.titles == ()
    assert resource.versions == ()


def test_resource_accepts_type_status_titles_and_versions() -> None:
    resource_uuid = make_resource_uuid()
    title = ResourceTitle(
        LocalizedText(LanguageCode("en"), "Banking regulation")
    )
    version = ResourceVersion(
        version_uuid=ResourceVersionUUID.generate(),
        resource_uuid=resource_uuid,
        status=ResourceStatus.IN_FORCE,
    )

    resource = Resource(
        resource_uuid=resource_uuid,
        identifiers=(make_identifier(),),
        resource_type=ResourceType.REGULATION,
        status=ResourceStatus.IN_FORCE,
        titles=(title,),
        versions=(version,),
    )

    assert resource.resource_type is ResourceType.REGULATION
    assert resource.status is ResourceStatus.IN_FORCE
    assert resource.titles == (title,)
    assert resource.versions == (version,)


@pytest.mark.parametrize(
    ("field_name", "value", "message"),
    [
        (
            "resource_type",
            "REGULATION",
            "resource_type must be a ResourceType",
        ),
        (
            "status",
            "IN_FORCE",
            "status must be a ResourceStatus",
        ),
        (
            "titles",
            [],
            "titles must be a tuple",
        ),
        (
            "versions",
            [],
            "versions must be a tuple",
        ),
    ],
)
def test_invalid_enrichment_field_types_are_rejected(
    field_name: str,
    value: object,
    message: str,
) -> None:
    arguments: dict[str, object] = {
        "resource_uuid": make_resource_uuid(),
        "identifiers": (make_identifier(),),
        "resource_type": ResourceType.REGULATION,
        "status": ResourceStatus.IN_FORCE,
        "titles": (),
        "versions": (),
    }
    arguments[field_name] = value

    with pytest.raises(TypeError, match=message):
        Resource(**arguments)  # type: ignore[arg-type]


def test_titles_must_contain_resource_titles() -> None:
    with pytest.raises(
        TypeError,
        match="only ResourceTitle instances",
    ):
        Resource(
            resource_uuid=make_resource_uuid(),
            identifiers=(make_identifier(),),
            titles=("Title",),  # type: ignore[arg-type]
        )


def test_duplicate_titles_are_rejected() -> None:
    title = ResourceTitle(
        LocalizedText(LanguageCode("en"), "Banking regulation")
    )

    with pytest.raises(
        ValueError,
        match="resource titles must be unique",
    ):
        Resource(
            resource_uuid=make_resource_uuid(),
            identifiers=(make_identifier(),),
            titles=(title, title),
        )


def test_overlapping_titles_in_same_language_are_rejected() -> None:
    first = ResourceTitle(
        LocalizedText(LanguageCode("en"), "First"),
        ValidityPeriod(
            valid_from=date(2024, 1, 1),
            valid_to=date(2024, 6, 30),
        ),
    )
    second = ResourceTitle(
        LocalizedText(LanguageCode("en"), "Second"),
        ValidityPeriod(
            valid_from=date(2024, 6, 1),
            valid_to=date(2024, 12, 31),
        ),
    )

    with pytest.raises(
        ValueError,
        match="must not have overlapping validity periods",
    ):
        Resource(
            resource_uuid=make_resource_uuid(),
            identifiers=(make_identifier(),),
            titles=(first, second),
        )


def test_titles_in_different_languages_may_overlap() -> None:
    period = ValidityPeriod(valid_from=date(2024, 1, 1))
    english = ResourceTitle(
        LocalizedText(LanguageCode("en"), "English title"),
        period,
    )
    french = ResourceTitle(
        LocalizedText(LanguageCode("fr"), "Titre français"),
        period,
    )

    resource = Resource(
        resource_uuid=make_resource_uuid(),
        identifiers=(make_identifier(),),
        titles=(english, french),
    )

    assert resource.titles == (english, french)


def test_versions_must_contain_resource_versions() -> None:
    with pytest.raises(
        TypeError,
        match="only ResourceVersion instances",
    ):
        Resource(
            resource_uuid=make_resource_uuid(),
            identifiers=(make_identifier(),),
            versions=("v1",),  # type: ignore[arg-type]
        )


def test_duplicate_version_identities_are_rejected() -> None:
    resource_uuid = make_resource_uuid()
    version_uuid = ResourceVersionUUID.generate()
    first = ResourceVersion(
        version_uuid,
        resource_uuid,
        ResourceStatus.PUBLISHED,
    )
    second = ResourceVersion(
        version_uuid,
        resource_uuid,
        ResourceStatus.IN_FORCE,
    )

    with pytest.raises(
        ValueError,
        match="version identities must be unique",
    ):
        Resource(
            resource_uuid=resource_uuid,
            identifiers=(make_identifier(),),
            versions=(first, second),
        )


def test_versions_must_belong_to_resource() -> None:
    version = ResourceVersion(
        ResourceVersionUUID.generate(),
        make_resource_uuid(),
        ResourceStatus.IN_FORCE,
    )

    with pytest.raises(
        ValueError,
        match="must belong to the resource",
    ):
        Resource(
            resource_uuid=make_resource_uuid(),
            identifiers=(make_identifier(),),
            versions=(version,),
        )


def test_previous_version_must_exist_in_aggregate() -> None:
    resource_uuid = make_resource_uuid()
    version = ResourceVersion(
        ResourceVersionUUID.generate(),
        resource_uuid,
        ResourceStatus.IN_FORCE,
        previous_version_uuid=ResourceVersionUUID.generate(),
    )

    with pytest.raises(
        ValueError,
        match="previous resource version must belong",
    ):
        Resource(
            resource_uuid=resource_uuid,
            identifiers=(make_identifier(),),
            versions=(version,),
        )


def test_titles_for_language_returns_matching_titles() -> None:
    english = ResourceTitle(
        LocalizedText(LanguageCode("en"), "English title")
    )
    french = ResourceTitle(
        LocalizedText(LanguageCode("fr"), "Titre français")
    )
    resource = Resource(
        make_resource_uuid(),
        (make_identifier(),),
        titles=(english, french),
    )

    assert resource.titles_for_language(
        LanguageCode("EN")
    ) == (english,)


def test_title_valid_on_returns_matching_temporal_title() -> None:
    historic = ResourceTitle(
        LocalizedText(LanguageCode("en"), "Historic title"),
        ValidityPeriod(
            valid_from=date(2020, 1, 1),
            valid_to=date(2023, 12, 31),
        ),
    )
    current = ResourceTitle(
        LocalizedText(LanguageCode("en"), "Current title"),
        ValidityPeriod(valid_from=date(2024, 1, 1)),
    )
    resource = Resource(
        make_resource_uuid(),
        (make_identifier(),),
        titles=(historic, current),
    )

    assert resource.title_valid_on(
        LanguageCode("en"),
        date(2022, 1, 1),
    ) == historic
    assert resource.title_valid_on(
        LanguageCode("en"),
        date(2025, 1, 1),
    ) == current
    assert resource.title_valid_on(
        LanguageCode("fr"),
        date(2025, 1, 1),
    ) is None


def test_find_version_and_has_version() -> None:
    resource_uuid = make_resource_uuid()
    version = ResourceVersion(
        ResourceVersionUUID.generate(),
        resource_uuid,
        ResourceStatus.IN_FORCE,
    )
    resource = Resource(
        resource_uuid,
        (make_identifier(),),
        versions=(version,),
    )

    assert resource.find_version(version.version_uuid) == version
    assert resource.has_version(version.version_uuid)
    assert not resource.has_version(
        ResourceVersionUUID.generate()
    )


def test_versions_valid_on_filters_versions() -> None:
    resource_uuid = make_resource_uuid()
    historic = ResourceVersion(
        ResourceVersionUUID.generate(),
        resource_uuid,
        ResourceStatus.SUPERSEDED,
        ValidityPeriod(
            valid_from=date(2020, 1, 1),
            valid_to=date(2023, 12, 31),
        ),
    )
    current = ResourceVersion(
        ResourceVersionUUID.generate(),
        resource_uuid,
        ResourceStatus.IN_FORCE,
        ValidityPeriod(valid_from=date(2024, 1, 1)),
        previous_version_uuid=historic.version_uuid,
    )
    resource = Resource(
        resource_uuid,
        (make_identifier(),),
        versions=(historic, current),
    )

    assert resource.versions_valid_on(
        date(2022, 1, 1)
    ) == (historic,)
    assert resource.versions_valid_on(
        date(2025, 1, 1)
    ) == (current,)


def test_query_methods_reject_invalid_types() -> None:
    resource = Resource(
        make_resource_uuid(),
        (make_identifier(),),
    )

    with pytest.raises(
        TypeError,
        match="language must be a LanguageCode",
    ):
        resource.titles_for_language("en")  # type: ignore[arg-type]

    with pytest.raises(
        TypeError,
        match="language must be a LanguageCode",
    ):
        resource.title_valid_on(  # type: ignore[arg-type]
            "en",
            date.today(),
        )

    with pytest.raises(TypeError, match="value must be a date"):
        resource.title_valid_on(
            LanguageCode("en"),
            "today",  # type: ignore[arg-type]
        )

    with pytest.raises(
        TypeError,
        match="version_uuid must be a ResourceVersionUUID",
    ):
        resource.find_version("v1")  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="value must be a date"):
        resource.versions_valid_on("today")  # type: ignore[arg-type]
