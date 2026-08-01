"""Tests for the Cellar RDF/XML metadata parser."""

from datetime import UTC, datetime

import pytest

from eke.application.eurlex import (
    EurLexDocument,
    EurLexMalformedMetadataError,
    EurLexMetadataMismatchError,
    EurLexMetadataParser,
    EurLexUnsupportedMediaTypeError,
)
from eke.domain.identity import CelexIdentifier
from eke.domain.localization import LanguageCode
from eke.infrastructure.eurlex import (
    RdfXmlEurLexMetadataParser,
)

RDF_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:cdm="http://publications.europa.eu/ontology/cdm#"
    xmlns:dc="http://purl.org/dc/elements/1.1/">
  <rdf:Description rdf:about="http://example.test/work">
    <cdm:resource_legal_id_celex>32023R1114</cdm:resource_legal_id_celex>
    <cdm:work_title xml:lang="en">
      Regulation on markets in crypto-assets
    </cdm:work_title>
    <cdm:work_title xml:lang="fr">
      RÃ¨glement sur les marchÃ©s de crypto-actifs
    </cdm:work_title>
    <cdm:work_date_document>2023-05-31</cdm:work_date_document>
    <cdm:work_date_publication>2023-06-09</cdm:work_date_publication>
    <cdm:work_date_entry-into-force>2023-06-29</cdm:work_date_entry-into-force>
    <cdm:work_date_end-of-validity>2026-12-31</cdm:work_date_end-of-validity>
    <cdm:work_has_resource-type
        rdf:resource="http://publications.europa.eu/resource/authority/resource-type/REG"/>
    <cdm:work_has_status
        rdf:resource="http://publications.europa.eu/resource/authority/resource-status/IN_FORCE"/>
    <cdm:expression_uses_language
        rdf:resource="http://publications.europa.eu/resource/authority/language/ENG"/>
    <cdm:expression_uses_language
        rdf:resource="http://publications.europa.eu/resource/authority/language/FRA"/>
    <cdm:work_is_about_concept_eurovoc
        rdf:resource="http://eurovoc.europa.eu/1001"/>
    <cdm:work_is_about_concept_eurovoc
        rdf:resource="http://eurovoc.europa.eu/1002"/>
  </rdf:Description>
</rdf:RDF>
""".encode()


def make_document(
    *,
    content: bytes = RDF_XML,
    content_type: str = "application/rdf+xml",
    celex: str = "32023R1114",
) -> EurLexDocument:
    return EurLexDocument(
        celex_identifier=CelexIdentifier.parse(celex),
        content_type=content_type,
        content=content,
        source_url="https://example.test/metadata",
        retrieved_at=datetime(
            2026,
            8,
            1,
            12,
            0,
            tzinfo=UTC,
        ),
    )


def test_parser_satisfies_protocol() -> None:
    parser = RdfXmlEurLexMetadataParser()

    assert isinstance(parser, EurLexMetadataParser)


def test_parse_extracts_stable_metadata() -> None:
    metadata = RdfXmlEurLexMetadataParser().parse(
        make_document()
    )

    assert metadata.celex_identifier.value == "32023R1114"
    assert tuple(
        title.language
        for title in metadata.titles
    ) == (
        LanguageCode("en"),
        LanguageCode("fr"),
    )
    assert metadata.titles[0].value == (
        "Regulation on markets in crypto-assets"
    )
    assert metadata.document_date.isoformat() == (
        "2023-05-31"
    )
    assert metadata.publication_date.isoformat() == (
        "2023-06-09"
    )
    assert metadata.entry_into_force_date.isoformat() == (
        "2023-06-29"
    )
    assert metadata.end_of_validity_date.isoformat() == (
        "2026-12-31"
    )
    assert metadata.languages == (
        LanguageCode("en"),
        LanguageCode("fr"),
    )
    assert metadata.resource_type_uri.endswith("/REG")
    assert metadata.status_uri.endswith("/IN_FORCE")
    assert metadata.eurovoc_concept_uris == (
        "http://eurovoc.europa.eu/1001",
        "http://eurovoc.europa.eu/1002",
    )


def test_parse_rejects_unsupported_media_type() -> None:
    parser = RdfXmlEurLexMetadataParser()

    with pytest.raises(
        EurLexUnsupportedMediaTypeError,
        match="unsupported",
    ):
        parser.parse(
            make_document(content_type="application/pdf")
        )


def test_parse_rejects_malformed_xml() -> None:
    parser = RdfXmlEurLexMetadataParser()

    with pytest.raises(
        EurLexMalformedMetadataError,
        match="not valid XML",
    ):
        parser.parse(make_document(content=b"<rdf:RDF>"))


def test_parse_rejects_celex_mismatch() -> None:
    parser = RdfXmlEurLexMetadataParser()

    with pytest.raises(
        EurLexMetadataMismatchError,
        match="does not match",
    ):
        parser.parse(
            make_document(celex="32013R0575")
        )


def test_parse_uses_requested_celex_when_absent() -> None:
    payload = b"""<rdf:RDF
        xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        xmlns:cdm="http://publications.europa.eu/ontology/cdm#">
      <rdf:Description>
        <cdm:work_title xml:lang="en">
          A title
        </cdm:work_title>
      </rdf:Description>
    </rdf:RDF>"""

    metadata = RdfXmlEurLexMetadataParser().parse(
        make_document(content=payload)
    )

    assert metadata.celex_identifier.value == "32023R1114"
