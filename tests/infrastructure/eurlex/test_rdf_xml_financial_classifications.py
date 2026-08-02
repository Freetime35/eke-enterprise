"""Tests for financial EuroVoc RDF/XML extraction."""

from datetime import UTC, datetime

from eke.application.eurlex import (
    EurLexDocument,
    FinancialClassificationCategory,
)
from eke.domain.identity import CelexIdentifier
from eke.infrastructure.eurlex import (
    FullRdfXmlEurLexMetadataParser,
)

PAYLOAD = b"""<rdf:RDF
 xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
 xmlns:cdm="http://publications.europa.eu/ontology/cdm#"
 xmlns:skos="http://www.w3.org/2004/02/skos/core#">
 <rdf:Description>
  <cdm:resource_legal_id_celex>32023R1114</cdm:resource_legal_id_celex>
  <cdm:work_is_about_concept_eurovoc
   rdf:resource="http://eurovoc.europa.eu/1001"/>
  <cdm:work_is_about_concept_eurovoc
   rdf:resource="http://eurovoc.europa.eu/1002"/>
 </rdf:Description>
 <rdf:Description rdf:about="http://eurovoc.europa.eu/1001">
  <skos:prefLabel xml:lang="en">financial institution</skos:prefLabel>
  <skos:prefLabel xml:lang="fr">institution financiere</skos:prefLabel>
  <skos:inScheme
   rdf:resource="http://eurovoc.europa.eu/100141"/>
  <skos:broader
   rdf:resource="http://eurovoc.europa.eu/10"/>
  <skos:narrower
   rdf:resource="http://eurovoc.europa.eu/10011"/>
 </rdf:Description>
 <rdf:Description rdf:about="http://eurovoc.europa.eu/1002">
  <skos:prefLabel xml:lang="en">agriculture</skos:prefLabel>
 </rdf:Description>
</rdf:RDF>"""


def test_parser_keeps_only_english_financial_concepts() -> None:
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

    classifications = (
        FullRdfXmlEurLexMetadataParser()
        .parse(document)
        .classifications
    )

    assert len(classifications) == 1
    classification = classifications[0]
    assert classification.label == "financial institution"
    assert (
        classification.financial_category
        is FinancialClassificationCategory
        .FINANCIAL_INSTITUTION
    )
    assert classification.scheme_uri == (
        "http://eurovoc.europa.eu/100141"
    )
    assert classification.broader_uris == (
        "http://eurovoc.europa.eu/10",
    )
    assert classification.narrower_uris == (
        "http://eurovoc.europa.eu/10011",
    )
