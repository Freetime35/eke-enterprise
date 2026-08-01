"""Tests for provenance controlled vocabularies."""

from __future__ import annotations

import pytest

from eke.domain.provenance import AcquisitionMethod, ProvenanceSource


@pytest.mark.parametrize(
    "source",
    list(ProvenanceSource),
)
def test_provenance_source_serializes_to_stable_string(
    source: ProvenanceSource,
) -> None:
    assert str(source) == source.value


@pytest.mark.parametrize(
    "method",
    list(AcquisitionMethod),
)
def test_acquisition_method_serializes_to_stable_string(
    method: AcquisitionMethod,
) -> None:
    assert str(method) == method.value


def test_provenance_source_members_are_unique() -> None:
    values = [source.value for source in ProvenanceSource]

    assert len(values) == len(set(values))


def test_acquisition_method_members_are_unique() -> None:
    values = [method.value for method in AcquisitionMethod]

    assert len(values) == len(set(values))


def test_enums_reject_unknown_values() -> None:
    with pytest.raises(ValueError):
        ProvenanceSource("UNKNOWN")

    with pytest.raises(ValueError):
        AcquisitionMethod("UNKNOWN")
