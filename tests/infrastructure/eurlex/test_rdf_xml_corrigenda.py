"""Tests for RDF/XML corrigendum extraction."""

from datetime import UTC, date, datetime

from eke.application.eurlex import (
    EurLexDocument,
)
from eke.domain.identity import CelexIdentifier
from eke.infrastructure.eurlex import (
    RdfXmlEurLexMetadataParser,
)

PAYLOAD = b"""<rdf:RDF
 xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:cdm="http://publications.europa.eu/ontology/cdm#">
 <rdf:Description>
  <cdm:resource_legal_id_celex>32013L0036</cdm:resource_legal_id_celex>
  <cdm:work_has_corrigendum
   rdf:resource="http://publications.europa.eu/resource/celex/32013L0036R(01)">
   <cdm:publication_date>2014-01-10</cdm:publication_date>
  </cdm:work_has_corrigendum>
  <cdm:work_has_corrigendum
   rdf:resource="http://publications.europa.eu/resource/celex/32013L0036R(02)">
   <cdm:publication_date>2014-05-15</cdm:publication_date>
  </cdm:work_has_corrigendum>
  <cdm:work_has_corrigendum
   rdf:resource="http://publications.europa.eu/resource/celex/32013L0036R(01)">
   <cdm:publication_date>2014-01-10</cdm:publication_date>
  </cdm:work_has_corrigendum>
 </rdf:Description>
</rdf:RDF>"""


def test_parser_extracts_unique_corrigenda() -> None:
    document = EurLexDocument(
        celex_identifier=CelexIdentifier.parse(
            "32013L0036"
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

    corrigenda = (
        RdfXmlEurLexMetadataParser()
        .parse(document)
        .corrigenda
    )

    assert len(corrigenda) == 2
    assert corrigenda[0].identifier.value == (
        "32013L0036R(01)"
    )
    assert corrigenda[0].publication_date == (
        date(2014, 1, 10)
    )
    assert corrigenda[1].identifier.value == (
        "32013L0036R(02)"
    )
