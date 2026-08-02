"""Tests for complete EUR-Lex RDF/XML metadata extraction."""

from datetime import UTC, datetime

from eke.application.eurlex import EurLexDocument
from eke.domain.identity import CelexIdentifier
from eke.domain.localization import LanguageCode
from eke.infrastructure.eurlex import (
    RdfXmlEurLexMetadataParser,
)

RDF_XML = b"""<rdf:RDF
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:cdm="http://publications.europa.eu/ontology/cdm#">
  <rdf:Description
   rdf:about="http://publications.europa.eu/resource/cellar/abc">
    <cdm:resource_legal_id_celex>
      32023R1114
    </cdm:resource_legal_id_celex>
    <cdm:work_title xml:lang="en">
      Markets in Crypto-assets
    </cdm:work_title>
    <cdm:work_date_document>
      2023-05-31
    </cdm:work_date_document>
    <cdm:work_date_publication>
      2023-06-09
    </cdm:work_date_publication>
    <cdm:expression_uses_language
     rdf:resource="http://publications.europa.eu/resource/authority/language/ENG"/>
    <cdm:work_has_resource-type
     rdf:resource="http://publications.europa.eu/resource/authority/resource-type/REG"/>
    <cdm:work_has_status
     rdf:resource="http://publications.europa.eu/resource/authority/resource-status/IN_FORCE"/>
    <cdm:resource_legal_eli
     rdf:resource="http://data.europa.eu/eli/reg/2023/1114/oj"/>
    <cdm:work_is_published_in_official-journal
     rdf:resource="http://publications.europa.eu/resource/oj/JOL_2023_150_R"/>
    <cdm:official-journal_number>
      L 150
    </cdm:official-journal_number>
    <cdm:official-journal_page_first>
      40
    </cdm:official-journal_page_first>
    <cdm:official-journal_page_last>
      205
    </cdm:official-journal_page_last>
    <cdm:work_created_by_agent
     rdf:resource="http://publications.europa.eu/resource/authority/corporate-body/CONSIL"/>
  </rdf:Description>
</rdf:RDF>"""


def test_parser_extracts_completeness_metadata() -> None:
    document = EurLexDocument(
        celex_identifier=CelexIdentifier.parse(
            "32023R1114"
        ),
        content_type="application/rdf+xml",
        content=RDF_XML,
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

    assert metadata.eli_uri == (
        "http://data.europa.eu/eli/"
        "reg/2023/1114/oj"
    )
    assert metadata.cellar_uri.endswith(
        "/cellar/abc"
    )
    assert metadata.languages == (
        LanguageCode("en"),
    )
    assert metadata.official_journal is not None
    assert (
        metadata.official_journal.number
        == "L 150"
    )
    assert metadata.official_journal.page_first == "40"
    assert metadata.official_journal.page_last == "205"
    assert len(metadata.responsible_agent_uris) == 1
    assert metadata.assess_completeness().score == 1.0
