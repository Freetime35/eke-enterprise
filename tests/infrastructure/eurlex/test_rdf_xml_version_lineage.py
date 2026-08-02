"""Tests for RDF/XML consolidated-version lineage extraction."""

from datetime import UTC, date, datetime

from eke.application.eurlex import (
    EurLexDocument,
    EurLexVersionLineageKind,
)
from eke.domain.identity import CelexIdentifier
from eke.infrastructure.eurlex import (
    RdfXmlEurLexMetadataParser,
)

PAYLOAD = b"""<rdf:RDF
 xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:cdm="http://publications.europa.eu/ontology/cdm#">
 <rdf:Description>
  <cdm:resource_legal_id_celex>32013R0575</cdm:resource_legal_id_celex>
  <cdm:initial_act
   rdf:resource="http://publications.europa.eu/resource/celex/32013R0575"/>
  <cdm:consolidated_version
   rdf:resource="http://publications.europa.eu/resource/celex/02013R0575-20240101">
   <cdm:consolidates_celex>32013R0575</cdm:consolidates_celex>
   <cdm:consolidation_date>2024-01-01</cdm:consolidation_date>
  </cdm:consolidated_version>
  <cdm:consolidated_version
   rdf:resource="http://publications.europa.eu/resource/celex/02013R0575-20250101">
   <cdm:consolidates_celex>32013R0575</cdm:consolidates_celex>
   <cdm:consolidation_date>2025-01-01</cdm:consolidation_date>
  </cdm:consolidated_version>
 </rdf:Description>
</rdf:RDF>"""


def test_parser_extracts_version_lineage() -> None:
    document = EurLexDocument(
        celex_identifier=CelexIdentifier.parse(
            "32013R0575"
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

    lineage = (
        RdfXmlEurLexMetadataParser()
        .parse(document)
        .version_lineage
    )

    assert len(lineage) == 3
    assert lineage[0].kind is (
        EurLexVersionLineageKind
        .CONSOLIDATED_VERSION
    )
    assert lineage[0].consolidation_date == (
        date(2024, 1, 1)
    )
    assert (
        lineage[0].version_identifier
        is not None
    )
    assert lineage[0].version_identifier.value == (
        "02013R0575-20240101"
    )
    assert lineage[1].consolidation_date == (
        date(2025, 1, 1)
    )
    assert lineage[2].kind is (
        EurLexVersionLineageKind.INITIAL_ACT
    )
    assert lineage[2].act_celex is not None
    assert lineage[2].act_celex.value == (
        "32013R0575"
    )
