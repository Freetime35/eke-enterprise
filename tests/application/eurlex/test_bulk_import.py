"""Tests for bulk EUR-Lex import orchestration."""

from __future__ import annotations

from eke.application.eurlex import (
    EurLexBulkImportService,
    EurLexBulkImportStatus,
    EurLexImportResult,
    EurLexResourceImportService,
)
from eke.domain.identity import (
    BusinessIdentifier,
    CelexIdentifier,
    IdentifierScheme,
    ResourceUUID,
)
from eke.domain.resources import Resource


class FakeImportService(EurLexResourceImportService):
    def __init__(self) -> None:
        self.calls: list[str] = []

    def import_resource(
        self,
        celex_identifier: CelexIdentifier,
    ) -> EurLexImportResult:
        self.calls.append(celex_identifier.value)
        resource = Resource(
            resource_uuid=ResourceUUID.generate(),
            identifiers=(
                BusinessIdentifier(
                    IdentifierScheme.CELEX,
                    celex_identifier.value,
                ),
            ),
        )
        return EurLexImportResult(
            resource=resource,
            created=celex_identifier.value != "32013R0575",
        )


def test_bulk_import_deduplicates_and_preserves_order() -> None:
    import_service = FakeImportService()
    service = EurLexBulkImportService(import_service)

    result = service.import_resources(
        (
            CelexIdentifier.parse("32023R1114"),
            CelexIdentifier.parse("32013R0575"),
            CelexIdentifier.parse("32023R1114"),
        )
    )

    assert result.total == 2
    assert result.created == 1
    assert result.existing == 1
    assert result.failed == 0
    assert [item.celex for item in result.items] == [
        "32023R1114",
        "32013R0575",
    ]
    assert result.items[0].status is (
        EurLexBulkImportStatus.CREATED
    )
    assert result.items[1].status is (
        EurLexBulkImportStatus.EXISTING
    )
