"""Tests for full RDF/XML enrichment extraction."""

from datetime import UTC, datetime

from eke.application.eurlex import EurLexDocument
from eke.domain.identity import CelexIdentifier
from eke.domain.relationships import RelationshipType
from eke.infrastructure.eurlex import RdfXmlEurLexMetadataParser

PAYLOAD = b"""<rdf:RDF
 xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:cdm="http://publications.europa.eu/ontology/cdm#"
 xmlns:skos="http://www.w3.org/2004/02/skos/core#">
 <rdf:Description rdf:about="http://example.test/work">
  <cdm:resource_legal_id_celex>32023R1114</cdm:resource_legal_id_celex>
  <cdm:work_is_about_concept_eurovoc
   rdf:resource="http://eurovoc.europa.eu/1001"/>
  <cdm:work_amends_work
   rdf:resource="http://publications.europa.eu/resource/celex/32013R0575"/>
 </rdf:Description>
 <rdf:Description rdf:about="http://eurovoc.europa.eu/1001">
  <skos:prefLabel xml:lang="en">financial market</skos:prefLabel>
 </rdf:Description>
</rdf:RDF>"""


def test_full_parser_extracts_labels_and_relationships() -> None:
    document = EurLexDocument(
        celex_identifier=CelexIdentifier.parse("32023R1114"),
        content_type="application/rdf+xml",
        content=PAYLOAD,
        source_url="https://example.test/source",
        retrieved_at=datetime(2026, 8, 1, 12, 0, tzinfo=UTC),
    )

    metadata = RdfXmlEurLexMetadataParser().parse(document)

    assert metadata.classifications[0].code == "1001"
    assert metadata.classifications[0].label == "financial market"
    assert metadata.relationships[0].target_celex.value == "32013R0575"
    assert (
        metadata.relationships[0].relationship_type
        is RelationshipType.AMENDS
    )
