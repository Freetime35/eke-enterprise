"""Canonical JSON codec for Resource aggregates."""

from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any, Final

from eke.domain.classification import (
    ClassificationConcept,
    ClassificationScheme,
)
from eke.domain.identity import (
    BusinessIdentifier,
    IdentifierScheme,
    ResourceUUID,
    ResourceVersionUUID,
)
from eke.domain.localization import LanguageCode, LocalizedText
from eke.domain.provenance import (
    AcquisitionMethod,
    ProvenanceRecord,
    ProvenanceSource,
)
from eke.domain.relationships import (
    RelationshipType,
    ResourceRelationship,
)
from eke.domain.resources import (
    Resource,
    ResourceStatus,
    ResourceTitle,
    ResourceType,
    ResourceVersion,
)
from eke.domain.temporal import ValidityPeriod

RESOURCE_PAYLOAD_VERSION: Final = 1


def encode_resource(resource: Resource) -> str:
    """Serialize a Resource aggregate into versioned canonical JSON."""
    if not isinstance(resource, Resource):
        raise TypeError("resource must be a Resource")

    envelope = {
        "schema_version": RESOURCE_PAYLOAD_VERSION,
        "resource": _resource_to_dict(resource),
    }
    return json.dumps(
        envelope,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def decode_resource(payload: str) -> Resource:
    """Deserialize versioned or legacy Resource JSON."""
    if not isinstance(payload, str):
        raise TypeError("payload must be a string")

    decoded = json.loads(payload)
    if not isinstance(decoded, dict):
        raise ValueError("payload must contain a JSON object")

    if "schema_version" not in decoded:
        return _resource_from_dict(decoded)

    schema_version = decoded.get("schema_version")
    if schema_version != RESOURCE_PAYLOAD_VERSION:
        raise ValueError(
            f"unsupported resource payload version: {schema_version}"
        )

    resource_data = decoded.get("resource")
    if not isinstance(resource_data, dict):
        raise ValueError(
            "versioned payload must contain a resource object"
        )

    return _resource_from_dict(resource_data)


def payload_version(payload: str) -> int:
    """Return the schema version of a payload.

    Legacy payloads are treated as version zero.
    """
    if not isinstance(payload, str):
        raise TypeError("payload must be a string")

    decoded = json.loads(payload)
    if not isinstance(decoded, dict):
        raise ValueError("payload must contain a JSON object")

    version = decoded.get("schema_version", 0)
    if not isinstance(version, int):
        raise ValueError("schema_version must be an integer")

    return version


def _period_to_dict(period: ValidityPeriod) -> dict[str, str | None]:
    return {
        "valid_from": (
            period.valid_from.isoformat()
            if period.valid_from
            else None
        ),
        "valid_to": (
            period.valid_to.isoformat()
            if period.valid_to
            else None
        ),
    }


def _period_from_dict(data: dict[str, Any]) -> ValidityPeriod:
    return ValidityPeriod(
        valid_from=(
            date.fromisoformat(data["valid_from"])
            if data["valid_from"] is not None
            else None
        ),
        valid_to=(
            date.fromisoformat(data["valid_to"])
            if data["valid_to"] is not None
            else None
        ),
    )


def _localized_text_to_dict(
    value: LocalizedText,
) -> dict[str, str]:
    return {
        "language": value.language.value,
        "value": value.value,
    }


def _localized_text_from_dict(
    data: dict[str, Any],
) -> LocalizedText:
    return LocalizedText(
        LanguageCode(data["language"]),
        data["value"],
    )


def _resource_to_dict(resource: Resource) -> dict[str, Any]:
    return {
        "resource_uuid": str(resource.resource_uuid),
        "identifiers": [
            {
                "scheme": identifier.scheme.value,
                "value": identifier.value,
            }
            for identifier in resource.identifiers
        ],
        "resource_type": resource.resource_type.value,
        "status": resource.status.value,
        "titles": [
            {
                "text": _localized_text_to_dict(title.text),
                "validity": _period_to_dict(title.validity),
            }
            for title in resource.titles
        ],
        "versions": [
            {
                "version_uuid": str(version.version_uuid),
                "resource_uuid": str(version.resource_uuid),
                "status": version.status.value,
                "validity": _period_to_dict(version.validity),
                "previous_version_uuid": (
                    str(version.previous_version_uuid)
                    if version.previous_version_uuid
                    else None
                ),
            }
            for version in resource.versions
        ],
        "relationships": [
            {
                "source": str(relationship.source),
                "target": str(relationship.target),
                "relationship_type": (
                    relationship.relationship_type.value
                ),
                "validity": _period_to_dict(
                    relationship.validity
                ),
            }
            for relationship in resource.relationships
        ],
        "provenance_records": [
            {
                "resource_uuid": str(record.resource_uuid),
                "source": record.source.value,
                "source_reference": record.source_reference,
                "acquired_at": record.acquired_at.isoformat(),
                "acquisition_method": (
                    record.acquisition_method.value
                ),
                "checksum": record.checksum,
            }
            for record in resource.provenance_records
        ],
        "classifications": [
            {
                "scheme": classification.scheme.value,
                "code": classification.code,
                "label": _localized_text_to_dict(
                    classification.label
                ),
                "validity": _period_to_dict(
                    classification.validity
                ),
            }
            for classification in resource.classifications
        ],
    }


def _resource_from_dict(data: dict[str, Any]) -> Resource:
    return Resource(
        resource_uuid=ResourceUUID.from_string(
            data["resource_uuid"]
        ),
        identifiers=tuple(
            BusinessIdentifier(
                IdentifierScheme(item["scheme"]),
                item["value"],
            )
            for item in data["identifiers"]
        ),
        resource_type=ResourceType(data["resource_type"]),
        status=ResourceStatus(data["status"]),
        titles=tuple(
            ResourceTitle(
                _localized_text_from_dict(item["text"]),
                _period_from_dict(item["validity"]),
            )
            for item in data["titles"]
        ),
        versions=tuple(
            ResourceVersion(
                version_uuid=ResourceVersionUUID.from_string(
                    item["version_uuid"]
                ),
                resource_uuid=ResourceUUID.from_string(
                    item["resource_uuid"]
                ),
                status=ResourceStatus(item["status"]),
                validity=_period_from_dict(item["validity"]),
                previous_version_uuid=(
                    ResourceVersionUUID.from_string(
                        item["previous_version_uuid"]
                    )
                    if item["previous_version_uuid"]
                    else None
                ),
            )
            for item in data["versions"]
        ),
        relationships=tuple(
            ResourceRelationship(
                source=ResourceUUID.from_string(item["source"]),
                target=ResourceUUID.from_string(item["target"]),
                relationship_type=RelationshipType(
                    item["relationship_type"]
                ),
                validity=_period_from_dict(item["validity"]),
            )
            for item in data["relationships"]
        ),
        provenance_records=tuple(
            ProvenanceRecord(
                resource_uuid=ResourceUUID.from_string(
                    item["resource_uuid"]
                ),
                source=ProvenanceSource(item["source"]),
                source_reference=item["source_reference"],
                acquired_at=datetime.fromisoformat(
                    item["acquired_at"]
                ),
                acquisition_method=AcquisitionMethod(
                    item["acquisition_method"]
                ),
                checksum=item["checksum"],
            )
            for item in data["provenance_records"]
        ),
        classifications=tuple(
            ClassificationConcept(
                scheme=ClassificationScheme(item["scheme"]),
                code=item["code"],
                label=_localized_text_from_dict(item["label"]),
                validity=_period_from_dict(item["validity"]),
            )
            for item in data["classifications"]
        ),
    )
