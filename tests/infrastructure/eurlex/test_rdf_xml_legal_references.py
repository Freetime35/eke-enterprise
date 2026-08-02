"""Tests for RDF/XML legal reference extraction."""

from datetime import UTC, datetime

from eke.application.eurlex import (
    EurLexDocument,
    EurLexLegalReferenceKind,
)
from eke.domain.identity import CelexIdentifier
from eke.infrastructure.eurlex import (
    RdfXmlEurLexMetadataParser,
)

PAYLOAD = b"""<rdf:RDF
 xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:cdm="http://publications.europa.eu/ontology/cdm#">
 <rdf:Description>
  <cdm:resource_legal_id_celex>32023R1114</cdm:resource_legal_id_celex>
  <cdm:work_cites_work
   rdf:resource="http://publications.europa.eu/resource/celex/32013R0575"/>
  <cdm:work_based_on_treaty
   rdf:resource="http://data.europa.eu/eli/treaty/tfeu_2012/art_114/oj">
   <cdm:article>Article 114 TFEU</cdm:article>
  </cdm:work_based_on_treaty>
  <cdm:work_cites_work
   rdf:resource="http://publications.europa.eu/resource/celex/32013R0575"/>
 </rdf:Description>
</rdf:RDF>"""


def test_parser_extracts_unique_legal_references() -> None:
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

    references = (
        RdfXmlEurLexMetadataParser()
        .parse(document)
        .legal_references
    )

    assert len(references) == 2
    assert references[0].kind is (
        EurLexLegalReferenceKind.CITES
    )
    assert references[0].target_celex is not None
    assert references[0].target_celex.value == (
        "32013R0575"
    )
    assert references[1].kind is (
        EurLexLegalReferenceKind.TREATY_BASIS
    )
    assert references[1].article == (
        "Article 114 TFEU"
    )
