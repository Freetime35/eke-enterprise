"""Tests for English typed title extraction."""

from datetime import UTC, datetime

from eke.application.eurlex import (
    EurLexDocument,
    EurLexTitleKind,
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
      32023R1114
    </cdm:resource_legal_id_celex>
    <cdm:work_title xml:lang="en">
      Regulation (EU) 2023/1114 on markets in crypto-assets
    </cdm:work_title>
    <cdm:work_title_short xml:lang="eng">
      MiCA Regulation
    </cdm:work_title_short>
    <cdm:alternative_title xml:lang="en">
      Markets in Crypto-assets Regulation
    </cdm:alternative_title>
    <cdm:work_title_short xml:lang="en">
      MiCA Regulation
    </cdm:work_title_short>
    <cdm:work_title xml:lang="fr">
      Reglement sur les marches de crypto-actifs
    </cdm:work_title>
    <cdm:short_title>
      Untagged title
    </cdm:short_title>
  </rdf:Description>
</rdf:RDF>"""


def test_parser_extracts_unique_english_typed_titles() -> None:
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

    titles = (
        RdfXmlEurLexMetadataParser()
        .parse(document)
        .titles
    )

    assert len(titles) == 3
    assert tuple(
        title.kind
        for title in titles
    ) == (
        EurLexTitleKind.OFFICIAL,
        EurLexTitleKind.SHORT,
        EurLexTitleKind.ALTERNATIVE,
    )
    assert all(
        title.language.value == "en"
        for title in titles
        if title.language is not None
    )
    assert titles[1].value == "MiCA Regulation"
