"""Tests for Resource classification aggregate integration."""

from __future__ import annotations

from datetime import date

import pytest

from eke.domain.classification import (
    ClassificationConcept,
    ClassificationScheme,
)
from eke.domain.identity import (
    BusinessIdentifier,
    IdentifierScheme,
    ResourceUUID,
)
from eke.domain.localization import LanguageCode, LocalizedText
from eke.domain.resources import Resource
from eke.domain.temporal import ValidityPeriod


def make_identifier() -> BusinessIdentifier:
    return BusinessIdentifier(
        IdentifierScheme.CELEX,
        "32023R1114",
    )


def make_concept(
    *,
    scheme: ClassificationScheme = ClassificationScheme.EUROVOC,
    code: str = "2406",
    language: str = "en",
    label: str = "Banking supervision",
    validity: ValidityPeriod | None = None,
) -> ClassificationConcept:
    return ClassificationConcept(
        scheme=scheme,
        code=code,
        label=LocalizedText(LanguageCode(language), label),
        validity=validity or ValidityPeriod(),
    )


def make_resource(
    classifications: tuple[ClassificationConcept, ...] = (),
) -> Resource:
    return Resource(
        resource_uuid=ResourceUUID.generate(),
        identifiers=(make_identifier(),),
        classifications=classifications,
    )


def test_default_classification_collection_is_empty() -> None:
    resource = make_resource()

    assert resource.classifications == ()


def test_resource_accepts_classifications() -> None:
    concept = make_concept()

    resource = make_resource((concept,))

    assert resource.classifications == (concept,)


def test_classifications_must_be_a_tuple() -> None:
    with pytest.raises(
        TypeError,
        match="classifications must be a tuple",
    ):
        Resource(
            resource_uuid=ResourceUUID.generate(),
            identifiers=(make_identifier(),),
            classifications=[],  # type: ignore[arg-type]
        )


def test_classifications_reject_invalid_members() -> None:
    with pytest.raises(
        TypeError,
        match="only ClassificationConcept instances",
    ):
        Resource(
            resource_uuid=ResourceUUID.generate(),
            identifiers=(make_identifier(),),
            classifications=("EUROVOC",),  # type: ignore[arg-type]
        )


def test_exact_duplicate_classifications_are_rejected() -> None:
    concept = make_concept()

    with pytest.raises(
        ValueError,
        match="resource classifications must be unique",
    ):
        make_resource((concept, concept))


def test_same_scheme_code_and_language_is_rejected() -> None:
    first = make_concept(label="First label")
    second = make_concept(label="Second label")

    with pytest.raises(
        ValueError,
        match="must not repeat the same scheme, code, and language",
    ):
        make_resource((first, second))


def test_same_scheme_and_code_in_different_languages_is_allowed() -> None:
    english = make_concept(
        language="en",
        label="Banking supervision",
    )
    french = make_concept(
        language="fr",
        label="Supervision bancaire",
    )

    resource = make_resource((english, french))

    assert resource.classifications == (english, french)


def test_same_code_in_different_schemes_is_allowed() -> None:
    eurovoc = make_concept(
        scheme=ClassificationScheme.EUROVOC,
        code="2406",
    )
    internal = make_concept(
        scheme=ClassificationScheme.INTERNAL,
        code="2406",
        label="Internal banking category",
    )

    resource = make_resource((eurovoc, internal))

    assert resource.classifications == (eurovoc, internal)


def test_classifications_in_scheme_filters_by_scheme() -> None:
    eurovoc = make_concept(
        scheme=ClassificationScheme.EUROVOC,
    )
    policy = make_concept(
        scheme=ClassificationScheme.POLICY_AREA,
        code="BANKING",
        label="Banking policy",
    )
    resource = make_resource((eurovoc, policy))

    assert resource.classifications_in_scheme(
        ClassificationScheme.EUROVOC
    ) == (eurovoc,)
    assert resource.classifications_in_scheme(
        ClassificationScheme.INTERNAL
    ) == ()


def test_classifications_in_scheme_rejects_invalid_type() -> None:
    resource = make_resource()

    with pytest.raises(
        TypeError,
        match="scheme must be a ClassificationScheme",
    ):
        resource.classifications_in_scheme(  # type: ignore[arg-type]
            "EUROVOC"
        )


def test_classifications_with_code_filters_scheme_and_code() -> None:
    english = make_concept(
        scheme=ClassificationScheme.EUROVOC,
        code="2406",
        language="en",
    )
    french = make_concept(
        scheme=ClassificationScheme.EUROVOC,
        code="2406",
        language="fr",
        label="Supervision bancaire",
    )
    other = make_concept(
        scheme=ClassificationScheme.EUROVOC,
        code="2407",
        label="Financial services",
    )
    resource = make_resource((english, french, other))

    assert resource.classifications_with_code(
        ClassificationScheme.EUROVOC,
        "2406",
    ) == (english, french)
    assert resource.classifications_with_code(
        ClassificationScheme.EUROVOC,
        "9999",
    ) == ()


def test_classifications_with_code_rejects_invalid_types() -> None:
    resource = make_resource()

    with pytest.raises(
        TypeError,
        match="scheme must be a ClassificationScheme",
    ):
        resource.classifications_with_code(  # type: ignore[arg-type]
            "EUROVOC",
            "2406",
        )

    with pytest.raises(TypeError, match="code must be a string"):
        resource.classifications_with_code(
            ClassificationScheme.EUROVOC,
            2406,  # type: ignore[arg-type]
        )


def test_classifications_for_language_filters_labels() -> None:
    english = make_concept(language="en")
    french = make_concept(
        language="fr",
        label="Supervision bancaire",
    )
    resource = make_resource((english, french))

    assert resource.classifications_for_language(
        LanguageCode("EN")
    ) == (english,)
    assert resource.classifications_for_language(
        LanguageCode("de")
    ) == ()


def test_classifications_for_language_rejects_invalid_type() -> None:
    resource = make_resource()

    with pytest.raises(
        TypeError,
        match="language must be a LanguageCode",
    ):
        resource.classifications_for_language(  # type: ignore[arg-type]
            "en"
        )


def test_classifications_valid_on_filters_temporal_validity() -> None:
    historic = make_concept(
        code="HISTORIC",
        label="Historic banking",
        validity=ValidityPeriod(
            valid_from=date(2020, 1, 1),
            valid_to=date(2023, 12, 31),
        ),
    )
    current = make_concept(
        code="CURRENT",
        label="Current banking",
        validity=ValidityPeriod(
            valid_from=date(2024, 1, 1),
        ),
    )
    resource = make_resource((historic, current))

    assert resource.classifications_valid_on(
        date(2022, 1, 1)
    ) == (historic,)
    assert resource.classifications_valid_on(
        date(2025, 1, 1)
    ) == (current,)


def test_classifications_valid_on_rejects_invalid_type() -> None:
    resource = make_resource()

    with pytest.raises(TypeError, match="value must be a date"):
        resource.classifications_valid_on(  # type: ignore[arg-type]
            "today"
        )
