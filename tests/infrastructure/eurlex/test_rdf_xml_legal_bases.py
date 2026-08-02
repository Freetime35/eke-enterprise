"""Tests for RDF/XML legal-basis extraction."""

from datetime import UTC, datetime

from eke.application.eurlex import (
    EurLexDocument,
    EurLexLegalBasisKind,
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
  <cdm:work_based_on_treaty
   rdf:resource="http://data.europa.eu/eli/treaty/tfeu_2012/art_114/oj">
   <cdm:treaty>TFEU</cdm:treaty>
   <cdm:article>114</cdm:article>
   <cdm:paragraph>1</cdm:paragraph>
   <cdm:label>Article 114(1) TFEU</cdm:label>
  </cdm:work_based_on_treaty>
  <cdm:work_based_on_legal_resource
   rdf:resource="http://publications.europa.eu/resource/celex/32013R0575"/>
  <cdm:work_based_on_treaty
   rdf:resource="http://data.europa.eu/eli/treaty/tfeu_2012/art_114/oj">
   <cdm:treaty>TFEU</cdm:treaty>
   <cdm:article>114</cdm:article>
   <cdm:paragraph>1</cdm:paragraph>
   <cdm:label>Article 114(1) TFEU</cdm:label>
  </cdm:work_based_on_treaty>
 </rdf:Description>
</rdf:RDF>"""


def test_parser_extracts_unique_legal_bases() -> None:
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

    legal_bases = (
        RdfXmlEurLexMetadataParser()
        .parse(document)
        .legal_bases
    )

    assert len(legal_bases) == 2
    assert legal_bases[0].kind is (
        EurLexLegalBasisKind.TREATY_ARTICLE
    )
    assert legal_bases[0].treaty == "TFEU"
    assert legal_bases[0].article == "114"
    assert legal_bases[0].paragraph == "1"
    assert legal_bases[1].kind is (
        EurLexLegalBasisKind.SECONDARY_ACT
    )
    assert legal_bases[1].target_celex is not None
    assert legal_bases[1].target_celex.value == (
        "32013R0575"
    )
