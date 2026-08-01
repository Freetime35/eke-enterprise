"""Bulk EUR-Lex import orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from eke.application.eurlex.exceptions import (
    EurLexClientError,
    EurLexMetadataError,
)
from eke.application.eurlex.import_service import (
    EurLexResourceImportService,
)
from eke.domain.identity import CelexIdentifier


class EurLexBulkImportStatus(StrEnum):
    """Outcome of one CELEX import in a bulk request."""

    CREATED = "CREATED"
    EXISTING = "EXISTING"
    FAILED = "FAILED"


@dataclass(frozen=True, slots=True)
class EurLexBulkImportItem:
    """Report one CELEX import outcome."""

    celex: str
    status: EurLexBulkImportStatus
    resource_uuid: str | None = None
    error_code: str | None = None
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class EurLexBulkImportResult:
    """Report all outcomes and aggregate counts."""

    items: tuple[EurLexBulkImportItem, ...]

    @property
    def total(self) -> int:
        return len(self.items)

    @property
    def created(self) -> int:
        return sum(
            item.status is EurLexBulkImportStatus.CREATED
            for item in self.items
        )

    @property
    def existing(self) -> int:
        return sum(
            item.status is EurLexBulkImportStatus.EXISTING
            for item in self.items
        )

    @property
    def failed(self) -> int:
        return sum(
            item.status is EurLexBulkImportStatus.FAILED
            for item in self.items
        )


class EurLexBulkImportService:
    """Import multiple CELEX identifiers independently."""

    def __init__(
        self,
        import_service: EurLexResourceImportService,
    ) -> None:
        if not isinstance(
            import_service,
            EurLexResourceImportService,
        ):
            raise TypeError(
                "import_service must be an "
                "EurLexResourceImportService"
            )
        self._import_service = import_service

    def import_resources(
        self,
        identifiers: tuple[CelexIdentifier, ...],
    ) -> EurLexBulkImportResult:
        """Import each unique CELEX while preserving request order."""
        if not isinstance(identifiers, tuple):
            raise TypeError("identifiers must be a tuple")
        if any(
            not isinstance(identifier, CelexIdentifier)
            for identifier in identifiers
        ):
            raise TypeError(
                "identifiers must contain CelexIdentifier values"
            )

        unique = tuple(
            dict.fromkeys(
                identifier.value
                for identifier in identifiers
            )
        )
        items: list[EurLexBulkImportItem] = []

        for value in unique:
            identifier = CelexIdentifier.parse(value)
            try:
                result = self._import_service.import_resource(
                    identifier
                )
            except EurLexClientError as exc:
                items.append(
                    EurLexBulkImportItem(
                        celex=value,
                        status=EurLexBulkImportStatus.FAILED,
                        error_code="eurlex_client_error",
                        detail=str(exc),
                    )
                )
                continue
            except EurLexMetadataError as exc:
                items.append(
                    EurLexBulkImportItem(
                        celex=value,
                        status=EurLexBulkImportStatus.FAILED,
                        error_code="eurlex_metadata_error",
                        detail=str(exc),
                    )
                )
                continue

            items.append(
                EurLexBulkImportItem(
                    celex=value,
                    status=(
                        EurLexBulkImportStatus.CREATED
                        if result.created
                        else EurLexBulkImportStatus.EXISTING
                    ),
                    resource_uuid=str(
                        result.resource.resource_uuid
                    ),
                )
            )

        return EurLexBulkImportResult(tuple(items))
