"""Tests for the versioned Resource JSON codec."""

from __future__ import annotations

import json

import pytest

from eke.domain.identity import (
    BusinessIdentifier,
    IdentifierScheme,
    ResourceUUID,
)
from eke.domain.resources import Resource
from eke.infrastructure.repositories.resource_codec import (
    RESOURCE_PAYLOAD_VERSION,
    decode_resource,
    encode_resource,
    payload_version,
)


def make_resource() -> Resource:
    return Resource(
        ResourceUUID.generate(),
        (
            BusinessIdentifier(
                IdentifierScheme.CELEX,
                "32023R1114",
            ),
        ),
    )


def test_encoded_payload_uses_versioned_envelope() -> None:
    resource = make_resource()

    payload = encode_resource(resource)
    decoded = json.loads(payload)

    assert decoded["schema_version"] == (
        RESOURCE_PAYLOAD_VERSION
    )
    assert decoded["resource"]["resource_uuid"] == str(
        resource.resource_uuid
    )


def test_versioned_payload_round_trip() -> None:
    resource = make_resource()

    assert decode_resource(encode_resource(resource)) == resource


def test_legacy_payload_remains_supported() -> None:
    resource = make_resource()
    envelope = json.loads(encode_resource(resource))
    legacy_payload = json.dumps(envelope["resource"])

    assert payload_version(legacy_payload) == 0
    assert decode_resource(legacy_payload) == resource


def test_unknown_payload_version_is_rejected() -> None:
    resource = make_resource()
    envelope = json.loads(encode_resource(resource))
    envelope["schema_version"] = 999

    with pytest.raises(
        ValueError,
        match="unsupported resource payload version",
    ):
        decode_resource(json.dumps(envelope))


def test_invalid_envelope_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="must contain a resource object",
    ):
        decode_resource(
            json.dumps(
                {
                    "schema_version": (
                        RESOURCE_PAYLOAD_VERSION
                    ),
                    "resource": "invalid",
                }
            )
        )


def test_payload_version_requires_integer() -> None:
    with pytest.raises(
        ValueError,
        match="schema_version must be an integer",
    ):
        payload_version(
            json.dumps({"schema_version": "1"})
        )
