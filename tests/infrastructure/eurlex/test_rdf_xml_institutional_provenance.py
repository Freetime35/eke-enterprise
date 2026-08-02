"""Tests for EUR-Lex institution RDF/XML extraction."""

from datetime import UTC, datetime

from eke.application.eurlex import EurLexDocument
from eke.domain.identity import CelexIdentifier
from eke.domain.provenance import ProvenanceSource
from eke.infrastructure.eurlex import (
    RdfXmlEurLexMetadataParser,
)

PAYLOAD = b"""<rdf:RDF
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:cdm="http://publications.europa.eu/ontology/cdm#">
  <rdf:Description>
    <cdm:resource_legal_id_celex>
      32023R1114
    </cdm:resource_legal_id_celex>
    <cdm:work_created_by_agent
     rdf:resource="http://publications.europa.eu/resource/authority/corporate-body/ECB"/>
    <cdm:work_adopted_by_agent
     rdf:resource="http://publications.europa.eu/resource/authority/corporate-body/COM"/>
    <cdm:work_created_by_agent
     rdf:resource="http://publications.europa.eu/resource/authority/corporate-body/ECB"/>
  </rdf:Description>
</rdf:RDF>"""


def test_parser_normalizes_unique_institutions() -> None:
    document = EurLexDocument(
        celex_identifier=CelexIdentifier.parse(
            "32023R1114"
        ),
        content_type="application/rdf+xml",
        content=PAYLOAD,
        source_url="https://example.test/source",
        retrieved_at=datetime(
            2026,
            8,
            2,
            12,
            0,
            tzinfo=UTC,
        ),
    )

    metadata = (
        RdfXmlEurLexMetadataParser()
        .parse(document)
    )

    assert len(metadata.institutions) == 2
    assert metadata.institutions[0].name == (
        "European Central Bank"
    )
    assert (
        metadata.institutions[0].provenance_source
        is ProvenanceSource.ECB
    )
    assert metadata.institutions[1].name == (
        "European Commission"
    )
