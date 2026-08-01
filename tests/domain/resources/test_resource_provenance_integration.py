"""Tests for Resource provenance aggregate integration."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from eke.domain.identity import (
    BusinessIdentifier,
    IdentifierScheme,
    ResourceUUID,
)
from eke.domain.provenance import (
    AcquisitionMethod,
    ProvenanceRecord,
    ProvenanceSource,
)
from eke.domain.resources import Resource


def make_identifier() -> BusinessIdentifier:
    return BusinessIdentifier(
        IdentifierScheme.CELEX,
        "32023R1114",
    )


def make_record(
    resource_uuid: ResourceUUID,
    *,
    source: ProvenanceSource = ProvenanceSource.EUR_LEX,
    reference: str = "CELEX:32023R1114",
    acquired_at: datetime | None = None,
    method: AcquisitionMethod = AcquisitionMethod.API,
    checksum: str | None = None,
) -> ProvenanceRecord:
    return ProvenanceRecord(
        resource_uuid=resource_uuid,
        source=source,
        source_reference=reference,
        acquired_at=acquired_at
        or datetime(2026, 8, 1, 12, 0, tzinfo=UTC),
        acquisition_method=method,
        checksum=checksum,
    )


def make_resource(
    resource_uuid: ResourceUUID,
    records: tuple[ProvenanceRecord, ...] = (),
) -> Resource:
    return Resource(
        resource_uuid=resource_uuid,
        identifiers=(make_identifier(),),
        provenance_records=records,
    )


def test_default_provenance_collection_is_empty() -> None:
    resource = make_resource(ResourceUUID.generate())

    assert resource.provenance_records == ()
    assert resource.latest_provenance_record() is None


def test_resource_accepts_provenance_records() -> None:
    resource_uuid = ResourceUUID.generate()
    record = make_record(resource_uuid)

    resource = make_resource(resource_uuid, (record,))

    assert resource.provenance_records == (record,)


def test_provenance_records_must_be_a_tuple() -> None:
    with pytest.raises(
        TypeError,
        match="provenance_records must be a tuple",
    ):
        Resource(
            resource_uuid=ResourceUUID.generate(),
            identifiers=(make_identifier(),),
            provenance_records=[],  # type: ignore[arg-type]
        )


def test_provenance_records_reject_invalid_members() -> None:
    with pytest.raises(
        TypeError,
        match="only ProvenanceRecord instances",
    ):
        Resource(
            resource_uuid=ResourceUUID.generate(),
            identifiers=(make_identifier(),),
            provenance_records=("source",),  # type: ignore[arg-type]
        )


def test_duplicate_provenance_records_are_rejected() -> None:
    resource_uuid = ResourceUUID.generate()
    record = make_record(resource_uuid)

    with pytest.raises(
        ValueError,
        match="provenance records must be unique",
    ):
        make_resource(resource_uuid, (record, record))


def test_provenance_record_must_belong_to_resource() -> None:
    aggregate_uuid = ResourceUUID.generate()
    record = make_record(ResourceUUID.generate())

    with pytest.raises(
        ValueError,
        match="must belong to the resource",
    ):
        make_resource(aggregate_uuid, (record,))


def test_distinct_records_with_same_source_reference_are_allowed() -> None:
    resource_uuid = ResourceUUID.generate()
    first = make_record(
        resource_uuid,
        acquired_at=datetime(2026, 8, 1, 10, 0, tzinfo=UTC),
        checksum="sha256:first",
    )
    second = make_record(
        resource_uuid,
        acquired_at=datetime(2026, 8, 1, 11, 0, tzinfo=UTC),
        checksum="sha256:second",
    )

    resource = make_resource(resource_uuid, (first, second))

    assert resource.provenance_records == (first, second)


def test_provenance_from_filters_by_source() -> None:
    resource_uuid = ResourceUUID.generate()
    eur_lex = make_record(
        resource_uuid,
        source=ProvenanceSource.EUR_LEX,
    )
    cellar = make_record(
        resource_uuid,
        source=ProvenanceSource.CELLAR,
        reference="cellar:abc",
    )
    resource = make_resource(resource_uuid, (eur_lex, cellar))

    assert resource.provenance_from(
        ProvenanceSource.EUR_LEX
    ) == (eur_lex,)
    assert resource.provenance_from(
        ProvenanceSource.ESMA
    ) == ()


def test_provenance_from_rejects_invalid_source() -> None:
    resource = make_resource(ResourceUUID.generate())

    with pytest.raises(
        TypeError,
        match="source must be a ProvenanceSource",
    ):
        resource.provenance_from(  # type: ignore[arg-type]
            "EUR_LEX"
        )


def test_provenance_acquired_by_filters_by_method() -> None:
    resource_uuid = ResourceUUID.generate()
    api = make_record(
        resource_uuid,
        method=AcquisitionMethod.API,
    )
    bulk = make_record(
        resource_uuid,
        method=AcquisitionMethod.BULK_DOWNLOAD,
        reference="bulk:2026-08-01",
    )
    resource = make_resource(resource_uuid, (api, bulk))

    assert resource.provenance_acquired_by(
        AcquisitionMethod.API
    ) == (api,)
    assert resource.provenance_acquired_by(
        AcquisitionMethod.MANUAL_ENTRY
    ) == ()


def test_provenance_acquired_by_rejects_invalid_method() -> None:
    resource = make_resource(ResourceUUID.generate())

    with pytest.raises(
        TypeError,
        match="acquisition_method must be an AcquisitionMethod",
    ):
        resource.provenance_acquired_by(  # type: ignore[arg-type]
            "API"
        )


def test_provenance_acquired_between_uses_inclusive_boundaries() -> None:
    resource_uuid = ResourceUUID.generate()
    first = make_record(
        resource_uuid,
        acquired_at=datetime(2026, 8, 1, 10, 0, tzinfo=UTC),
    )
    second = make_record(
        resource_uuid,
        acquired_at=datetime(2026, 8, 1, 11, 0, tzinfo=UTC),
        reference="CELLAR:abc",
    )
    third = make_record(
        resource_uuid,
        acquired_at=datetime(2026, 8, 1, 12, 0, tzinfo=UTC),
        reference="ELI:xyz",
    )
    resource = make_resource(
        resource_uuid,
        (first, second, third),
    )

    assert resource.provenance_acquired_between(
        datetime(2026, 8, 1, 10, 0, tzinfo=UTC),
        datetime(2026, 8, 1, 11, 0, tzinfo=UTC),
    ) == (first, second)


@pytest.mark.parametrize(
    ("start", "end", "message"),
    [
        (
            "start",
            datetime(2026, 8, 1, 12, 0, tzinfo=UTC),
            "start must be a datetime",
        ),
        (
            datetime(2026, 8, 1, 10, 0, tzinfo=UTC),
            "end",
            "end must be a datetime",
        ),
    ],
)
def test_provenance_range_rejects_invalid_types(
    start: object,
    end: object,
    message: str,
) -> None:
    resource = make_resource(ResourceUUID.generate())

    with pytest.raises(TypeError, match=message):
        resource.provenance_acquired_between(  # type: ignore[arg-type]
            start,
            end,
        )


def test_provenance_range_requires_timezone_aware_start() -> None:
    resource = make_resource(ResourceUUID.generate())

    with pytest.raises(
        ValueError,
        match="start must be timezone-aware",
    ):
        resource.provenance_acquired_between(
            datetime(2026, 8, 1, 10, 0),
            datetime(2026, 8, 1, 12, 0, tzinfo=UTC),
        )


def test_provenance_range_requires_timezone_aware_end() -> None:
    resource = make_resource(ResourceUUID.generate())

    with pytest.raises(
        ValueError,
        match="end must be timezone-aware",
    ):
        resource.provenance_acquired_between(
            datetime(2026, 8, 1, 10, 0, tzinfo=UTC),
            datetime(2026, 8, 1, 12, 0),
        )


def test_provenance_range_rejects_reversed_boundaries() -> None:
    resource = make_resource(ResourceUUID.generate())

    with pytest.raises(
        ValueError,
        match="start must not be later than end",
    ):
        resource.provenance_acquired_between(
            datetime(2026, 8, 1, 12, 0, tzinfo=UTC),
            datetime(2026, 8, 1, 10, 0, tzinfo=UTC),
        )


def test_latest_provenance_record_returns_most_recent_record() -> None:
    resource_uuid = ResourceUUID.generate()
    first = make_record(
        resource_uuid,
        acquired_at=datetime(2026, 8, 1, 10, 0, tzinfo=UTC),
    )
    latest = make_record(
        resource_uuid,
        acquired_at=datetime(2026, 8, 1, 12, 0, tzinfo=UTC),
        reference="latest",
    )
    middle = make_record(
        resource_uuid,
        acquired_at=datetime(2026, 8, 1, 11, 0, tzinfo=UTC),
        reference="middle",
    )
    resource = make_resource(
        resource_uuid,
        (first, latest, middle),
    )

    assert resource.latest_provenance_record() == latest
