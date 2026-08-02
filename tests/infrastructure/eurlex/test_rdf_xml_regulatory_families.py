"""Tests for regulatory-family detection during RDF parsing."""

from datetime import UTC, datetime

from eke.application.eurlex import (
    EurLexDocument,
    EurLexRegulatoryFamily,
    RegulatoryFamilyEvidenceKind,
)
from eke.domain.identity import CelexIdentifier
from eke.infrastructure.eurlex import (
    RdfXmlEurLexMetadataParser,
)

PAYLOAD = b"""<rdf:RDF
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:cdm="http://publications.europa.eu/ontology/cdm#">
  <rdf:Description>
    <cdm:resource_legal_id_celex>
      32022R2554
    </cdm:resource_legal_id_celex>
    <cdm:work_title xml:lang="en">
      Regulation on digital operational resilience
      for the financial sector
    </cdm:work_title>
    <cdm:work_title_short xml:lang="en">
      DORA
    </cdm:work_title_short>
    <cdm:work_title xml:lang="fr">
      Reglement sur la resilience operationnelle
    </cdm:work_title>
  </rdf:Description>
</rdf:RDF>"""


def test_parser_detects_dora_once() -> None:
    document = EurLexDocument(
        celex_identifier=CelexIdentifier.parse(
            "32022R2554"
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

    matches = (
        RdfXmlEurLexMetadataParser()
        .parse(document)
        .regulatory_families
    )

    assert len(matches) == 1
    assert (
        matches[0].family
        is EurLexRegulatoryFamily.DORA
    )
    assert (
        matches[0].evidence_kind
        is RegulatoryFamilyEvidenceKind.CELEX
    )
