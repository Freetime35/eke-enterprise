"""Tests for the ProvenanceRecord business concept."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest

from eke.domain.identity import ResourceUUID
from eke.domain.provenance import (
    AcquisitionMethod,
    ProvenanceRecord,
    ProvenanceSource,
)


@pytest.fixture
def resource_uuid() -> ResourceUUID:
    return ResourceUUID.generate()


@pytest.fixture
def acquired_at() -> datetime:
    return datetime(2026, 8, 1, 12, 30, tzinfo=UTC)


def test_create_provenance_record(
    resource_uuid: ResourceUUID,
    acquired_at: datetime,
) -> None:
    record = ProvenanceRecord(
        resource_uuid=resource_uuid,
        source=ProvenanceSource.EUR_LEX,
        source_reference="CELEX:32023R1114",
        acquired_at=acquired_at,
        acquisition_method=AcquisitionMethod.API,
        checksum="sha256:abc123",
    )

    assert record.resource_uuid == resource_uuid
    assert record.source is ProvenanceSource.EUR_LEX
    assert record.source_reference == "CELEX:32023R1114"
    assert record.acquired_at == acquired_at
    assert record.acquisition_method is AcquisitionMethod.API
    assert record.checksum == "sha256:abc123"


def test_checksum_is_optional(
    resource_uuid: ResourceUUID,
    acquired_at: datetime,
) -> None:
    record = ProvenanceRecord(
        resource_uuid=resource_uuid,
        source=ProvenanceSource.CELLAR,
        source_reference="cellar:abc",
        acquired_at=acquired_at,
        acquisition_method=AcquisitionMethod.BULK_DOWNLOAD,
    )

    assert record.checksum is None
    assert not record.has_checksum


def test_has_checksum_reports_presence(
    resource_uuid: ResourceUUID,
    acquired_at: datetime,
) -> None:
    record = ProvenanceRecord(
        resource_uuid=resource_uuid,
        source=ProvenanceSource.CELLAR,
        source_reference="cellar:abc",
        acquired_at=acquired_at,
        acquisition_method=AcquisitionMethod.FILE_IMPORT,
        checksum="sha256:def456",
    )

    assert record.has_checksum


@pytest.mark.parametrize(
    ("field_name", "value", "message"),
    [
        (
            "resource_uuid",
            "invalid",
            "resource_uuid must be a ResourceUUID",
        ),
        (
            "source",
            "EUR_LEX",
            "source must be a ProvenanceSource",
        ),
        (
            "source_reference",
            123,
            "source_reference must be a string",
        ),
        (
            "acquired_at",
            "2026-08-01",
            "acquired_at must be a datetime",
        ),
        (
            "acquisition_method",
            "API",
            "acquisition_method must be an AcquisitionMethod",
        ),
        (
            "checksum",
            123,
            "checksum must be a string or None",
        ),
    ],
)
def test_invalid_field_types_are_rejected(
    resource_uuid: ResourceUUID,
    acquired_at: datetime,
    field_name: str,
    value: object,
    message: str,
) -> None:
    arguments: dict[str, object] = {
        "resource_uuid": resource_uuid,
        "source": ProvenanceSource.EUR_LEX,
        "source_reference": "CELEX:32023R1114",
        "acquired_at": acquired_at,
        "acquisition_method": AcquisitionMethod.API,
        "checksum": None,
    }
    arguments[field_name] = value

    with pytest.raises(TypeError, match=message):
        ProvenanceRecord(**arguments)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", ["", " ", "\t", "\n"])
def test_empty_source_reference_is_rejected(
    resource_uuid: ResourceUUID,
    acquired_at: datetime,
    value: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="source_reference must not be empty",
    ):
        ProvenanceRecord(
            resource_uuid=resource_uuid,
            source=ProvenanceSource.EUR_LEX,
            source_reference=value,
            acquired_at=acquired_at,
            acquisition_method=AcquisitionMethod.API,
        )


def test_naive_acquisition_datetime_is_rejected(
    resource_uuid: ResourceUUID,
) -> None:
    with pytest.raises(
        ValueError,
        match="acquired_at must be timezone-aware",
    ):
        ProvenanceRecord(
            resource_uuid=resource_uuid,
            source=ProvenanceSource.EUR_LEX,
            source_reference="CELEX:32023R1114",
            acquired_at=datetime(2026, 8, 1, 12, 30),
            acquisition_method=AcquisitionMethod.API,
        )


@pytest.mark.parametrize("checksum", ["", " ", "\t", "\n"])
def test_empty_checksum_is_rejected(
    resource_uuid: ResourceUUID,
    acquired_at: datetime,
    checksum: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="checksum must not be empty",
    ):
        ProvenanceRecord(
            resource_uuid=resource_uuid,
            source=ProvenanceSource.EUR_LEX,
            source_reference="CELEX:32023R1114",
            acquired_at=acquired_at,
            acquisition_method=AcquisitionMethod.API,
            checksum=checksum,
        )


def test_belongs_to_reports_resource_ownership(
    resource_uuid: ResourceUUID,
    acquired_at: datetime,
) -> None:
    record = ProvenanceRecord(
        resource_uuid=resource_uuid,
        source=ProvenanceSource.EUR_LEX,
        source_reference="CELEX:32023R1114",
        acquired_at=acquired_at,
        acquisition_method=AcquisitionMethod.API,
    )

    assert record.belongs_to(resource_uuid)
    assert not record.belongs_to(ResourceUUID.generate())


def test_comes_from_reports_source(
    resource_uuid: ResourceUUID,
    acquired_at: datetime,
) -> None:
    record = ProvenanceRecord(
        resource_uuid=resource_uuid,
        source=ProvenanceSource.EUR_LEX,
        source_reference="CELEX:32023R1114",
        acquired_at=acquired_at,
        acquisition_method=AcquisitionMethod.API,
    )

    assert record.comes_from(ProvenanceSource.EUR_LEX)
    assert not record.comes_from(ProvenanceSource.CELLAR)


def test_was_acquired_by_reports_method(
    resource_uuid: ResourceUUID,
    acquired_at: datetime,
) -> None:
    record = ProvenanceRecord(
        resource_uuid=resource_uuid,
        source=ProvenanceSource.EUR_LEX,
        source_reference="CELEX:32023R1114",
        acquired_at=acquired_at,
        acquisition_method=AcquisitionMethod.API,
    )

    assert record.was_acquired_by(AcquisitionMethod.API)
    assert not record.was_acquired_by(
        AcquisitionMethod.BULK_DOWNLOAD
    )


def test_query_methods_reject_invalid_types(
    resource_uuid: ResourceUUID,
    acquired_at: datetime,
) -> None:
    record = ProvenanceRecord(
        resource_uuid=resource_uuid,
        source=ProvenanceSource.EUR_LEX,
        source_reference="CELEX:32023R1114",
        acquired_at=acquired_at,
        acquisition_method=AcquisitionMethod.API,
    )

    with pytest.raises(
        TypeError,
        match="resource_uuid must be a ResourceUUID",
    ):
        record.belongs_to("invalid")  # type: ignore[arg-type]

    with pytest.raises(
        TypeError,
        match="source must be a ProvenanceSource",
    ):
        record.comes_from("EUR_LEX")  # type: ignore[arg-type]

    with pytest.raises(
        TypeError,
        match="acquisition_method must be an AcquisitionMethod",
    ):
        record.was_acquired_by("API")  # type: ignore[arg-type]


def test_provenance_record_is_immutable_hashable_and_comparable(
    resource_uuid: ResourceUUID,
    acquired_at: datetime,
) -> None:
    first = ProvenanceRecord(
        resource_uuid=resource_uuid,
        source=ProvenanceSource.EUR_LEX,
        source_reference="CELEX:32023R1114",
        acquired_at=acquired_at,
        acquisition_method=AcquisitionMethod.API,
    )
    second = ProvenanceRecord(
        resource_uuid=resource_uuid,
        source=ProvenanceSource.EUR_LEX,
        source_reference="CELEX:32023R1114",
        acquired_at=acquired_at,
        acquisition_method=AcquisitionMethod.API,
    )

    assert first == second
    assert hash(first) == hash(second)

    with pytest.raises(FrozenInstanceError):
        first.source_reference = "changed"  # type: ignore[misc]
