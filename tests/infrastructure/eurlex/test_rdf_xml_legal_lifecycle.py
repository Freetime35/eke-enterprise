"""Tests for RDF/XML lifecycle and amendment extraction."""

from datetime import UTC, date, datetime

from eke.application.eurlex import (
    EurLexDocument,
    EurLexLegalLifecycleEventKind,
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
  <cdm:work_date_adoption>2023-05-31</cdm:work_date_adoption>
  <cdm:work_date_publication>2023-06-09</cdm:work_date_publication>
  <cdm:work_date_entry-into-force>2023-06-29</cdm:work_date_entry-into-force>
  <cdm:work_date_application>2024-06-30</cdm:work_date_application>
  <cdm:amendment_event>
   <cdm:amending_celex>32024R0001</cdm:amending_celex>
   <cdm:amended_celex>32023R1114</cdm:amended_celex>
   <cdm:effective_on>2024-07-01</cdm:effective_on>
  </cdm:amendment_event>
 </rdf:Description>
</rdf:RDF>"""


def test_parser_extracts_lifecycle_and_amendment_dates() -> None:
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

    metadata = RdfXmlEurLexMetadataParser().parse(
        document
    )

    assert tuple(
        event.kind
        for event in metadata.legal_lifecycle
    ) == (
        EurLexLegalLifecycleEventKind.ADOPTION,
        EurLexLegalLifecycleEventKind.PUBLICATION,
        EurLexLegalLifecycleEventKind.ENTRY_INTO_FORCE,
        EurLexLegalLifecycleEventKind.APPLICATION,
    )
    assert metadata.amendment_events[0].effective_on == (
        date(2024, 7, 1)
    )
    assert (
        metadata.amendment_events[0].amending_celex.value
        == "32024R0001"
    )
