"""Map transport-neutral EUR-Lex metadata to the Resource domain."""

from __future__ import annotations

from datetime import datetime
from hashlib import sha256

from eke.application.eurlex.document import EurLexDocument
from eke.application.eurlex.metadata import EurLexMetadata
from eke.domain.identity import ResourceUUID
from eke.domain.localization import LocalizedText
from eke.domain.provenance import (
    AcquisitionMethod,
    ProvenanceRecord,
    ProvenanceSource,
)
from eke.domain.resources import (
    Resource,
    ResourceStatus,
    ResourceTitle,
    ResourceType,
)


def resource_from_eurlex(
    document: EurLexDocument,
    metadata: EurLexMetadata,
) -> Resource:
    """Build a new canonical Resource from parsed EUR-Lex metadata."""
    if not isinstance(document, EurLexDocument):
        raise TypeError("document must be an EurLexDocument")
    if not isinstance(metadata, EurLexMetadata):
        raise TypeError("metadata must be an EurLexMetadata")
    if (
        document.celex_identifier
        != metadata.celex_identifier
    ):
        raise ValueError(
            "document and metadata CELEX identifiers must match"
        )

    resource_uuid = ResourceUUID.generate()
    titles = tuple(
        ResourceTitle(
            text=LocalizedText(
                title.language,
                title.value,
            )
        )
        for title in metadata.titles
        if title.language is not None
    )
    checksum = (
        "sha256:"
        f"{sha256(document.content).hexdigest()}"
    )
    provenance = ProvenanceRecord(
        resource_uuid=resource_uuid,
        source=ProvenanceSource.EUR_LEX,
        source_reference=document.source_url,
        acquired_at=document.retrieved_at,
        acquisition_method=AcquisitionMethod.API,
        checksum=checksum,
    )

    return Resource(
        resource_uuid=resource_uuid,
        identifiers=(
            metadata.celex_identifier.to_business_identifier(),
        ),
        resource_type=map_resource_type(
            metadata.resource_type_uri,
            metadata.celex_identifier.document_type,
            metadata.celex_identifier.sector.value,
        ),
        status=map_resource_status(
            metadata.status_uri,
            metadata.entry_into_force_date,
            metadata.end_of_validity_date,
        ),
        titles=titles,
        provenance_records=(
            provenance,
            *_institution_provenance_records(
                resource_uuid,
                metadata,
                document.retrieved_at,
            ),
        ),
    )



def _institution_provenance_records(
    resource_uuid: ResourceUUID,
    metadata: EurLexMetadata,
    acquired_at: datetime,
) -> tuple[ProvenanceRecord, ...]:
    """Map recognized financial authorities to derived provenance."""
    if not isinstance(acquired_at, datetime):
        raise TypeError(
            "acquired_at must be a datetime"
        )

    records: list[ProvenanceRecord] = []

    for institution in metadata.institutions:
        source = institution.provenance_source
        if source is None:
            continue

        record = ProvenanceRecord(
            resource_uuid=resource_uuid,
            source=source,
            source_reference=institution.uri,
            acquired_at=acquired_at,
            acquisition_method=AcquisitionMethod.DERIVED,
        )
        if record not in records:
            records.append(record)

    return tuple(records)


def map_resource_type(
    resource_type_uri: str | None,
    document_type: str,
    sector: str,
) -> ResourceType:
    """Map Cellar type information with a conservative fallback."""
    token = _uri_token(resource_type_uri)

    explicit = {
        "REG": ResourceType.REGULATION,
        "REGULATION": ResourceType.REGULATION,
        "DIR": ResourceType.DIRECTIVE,
        "DIRECTIVE": ResourceType.DIRECTIVE,
        "DEC": ResourceType.DECISION,
        "DECISION": ResourceType.DECISION,
        "RECO": ResourceType.RECOMMENDATION,
        "RECOMMENDATION": ResourceType.RECOMMENDATION,
        "OPINION": ResourceType.OPINION,
        "TREATY": ResourceType.TREATY,
        "CASE_LAW": ResourceType.CASE_LAW,
        "NOTICE": ResourceType.NOTICE,
        "COMMUNICATION": ResourceType.COMMUNICATION,
        "GUIDELINE": ResourceType.GUIDELINE,
        "REPORT": ResourceType.REPORT,
        "PROPOSAL": ResourceType.PROPOSAL,
        "CORRIGENDUM": ResourceType.CORRIGENDUM,
    }
    if token in explicit:
        return explicit[token]

    if sector == "6":
        return ResourceType.CASE_LAW

    celex_types = {
        "R": ResourceType.REGULATION,
        "L": ResourceType.DIRECTIVE,
        "D": ResourceType.DECISION,
        "DC": ResourceType.COMMUNICATION,
        "PC": ResourceType.PROPOSAL,
        "CJ": ResourceType.CASE_LAW,
        "CC": ResourceType.CASE_LAW,
        "CO": ResourceType.CASE_LAW,
    }
    return celex_types.get(
        document_type,
        ResourceType.OTHER,
    )


def map_resource_status(
    status_uri: str | None,
    entry_into_force_date: object | None = None,
    end_of_validity_date: object | None = None,
) -> ResourceStatus:
    """Map a Cellar status URI without inventing unknown semantics."""
    del entry_into_force_date, end_of_validity_date

    token = _uri_token(status_uri)
    mapping = {
        "DRAFT": ResourceStatus.DRAFT,
        "ADOPTED": ResourceStatus.ADOPTED,
        "PUBLISHED": ResourceStatus.PUBLISHED,
        "IN_FORCE": ResourceStatus.IN_FORCE,
        "PARTIALLY_IN_FORCE": (
            ResourceStatus.PARTIALLY_IN_FORCE
        ),
        "NOT_YET_IN_FORCE": (
            ResourceStatus.NOT_YET_IN_FORCE
        ),
        "REPEALED": ResourceStatus.REPEALED,
        "EXPIRED": ResourceStatus.EXPIRED,
        "WITHDRAWN": ResourceStatus.WITHDRAWN,
        "ANNULLED": ResourceStatus.ANNULLED,
        "SUPERSEDED": ResourceStatus.SUPERSEDED,
    }
    return mapping.get(token, ResourceStatus.UNKNOWN)


def _uri_token(value: str | None) -> str:
    if value is None:
        return ""
    return (
        value.rstrip("/")
        .rsplit("/", maxsplit=1)[-1]
        .replace("-", "_")
        .upper()
    )
