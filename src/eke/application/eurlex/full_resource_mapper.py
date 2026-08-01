"""Map complete EUR-Lex metadata into Resource-owned domain values."""

from __future__ import annotations

from eke.application.eurlex.metadata import EurLexMetadata
from eke.application.eurlex.resource_mapper import map_resource_status
from eke.domain.classification import (
    ClassificationConcept,
    ClassificationScheme,
)
from eke.domain.identity import ResourceUUID, ResourceVersionUUID
from eke.domain.localization import LocalizedText
from eke.domain.relationships import ResourceRelationship
from eke.domain.resources import ResourceVersion
from eke.domain.temporal import ValidityPeriod


def map_version(
    resource_uuid: ResourceUUID,
    metadata: EurLexMetadata,
) -> ResourceVersion:
    """Create the initial canonical version from legal dates."""
    return ResourceVersion(
        version_uuid=ResourceVersionUUID.generate(),
        resource_uuid=resource_uuid,
        status=map_resource_status(
            metadata.status_uri,
            metadata.entry_into_force_date,
            metadata.end_of_validity_date,
        ),
        validity=ValidityPeriod(
            metadata.entry_into_force_date
            or metadata.document_date,
            metadata.end_of_validity_date,
        ),
    )


def map_classifications(
    metadata: EurLexMetadata,
) -> tuple[ClassificationConcept, ...]:
    """Map labeled EuroVoc metadata to domain concepts."""
    return tuple(
        ClassificationConcept(
            scheme=ClassificationScheme.EUROVOC,
            code=item.code,
            label=LocalizedText(item.language, item.label),
        )
        for item in metadata.classifications
    )


def map_relationships(
    source_uuid: ResourceUUID,
    metadata: EurLexMetadata,
    targets: dict[str, ResourceUUID],
) -> tuple[ResourceRelationship, ...]:
    """Map CELEX relationships after target UUID resolution."""
    return tuple(
        ResourceRelationship(
            source=source_uuid,
            target=targets[item.target_celex.value],
            relationship_type=item.relationship_type,
        )
        for item in metadata.relationships
    )
