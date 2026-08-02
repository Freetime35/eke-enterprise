"""Tests for RDF/XML EUR-Lex relationship extraction."""

from datetime import UTC, datetime

from eke.application.eurlex import EurLexDocument
from eke.domain.identity import CelexIdentifier
from eke.domain.relationships import RelationshipType
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
    <cdm:work_amends_work
     rdf:resource="http://publications.europa.eu/resource/celex/32013R0575"/>
    <cdm:work_amends_work>
      http://publications.europa.eu/resource/celex/32013R0575
    </cdm:work_amends_work>
    <cdm:work_cites_work
     rdf:resource="http://publications.europa.eu/resource/celex/32016R0679"/>
    <cdm:work_unknown_work
     rdf:resource="http://publications.europa.eu/resource/celex/32019R0001"/>
    <cdm:work_repeals_work
     rdf:resource="https://example.test/not-a-celex"/>
  </rdf:Description>
</rdf:RDF>"""


def test_parser_extracts_known_unique_relations() -> None:
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

    relationships = (
        RdfXmlEurLexMetadataParser()
        .parse(document)
        .relationships
    )

    assert len(relationships) == 2
    assert relationships[0].target_celex.value == (
        "32013R0575"
    )
    assert (
        relationships[0].relationship_type
        is RelationshipType.AMENDS
    )
    assert relationships[1].target_celex.value == (
        "32016R0679"
    )
    assert (
        relationships[1].relationship_type
        is RelationshipType.CITES
    )
