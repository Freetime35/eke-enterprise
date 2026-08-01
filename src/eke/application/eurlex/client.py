"""EUR-Lex client application port."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from eke.application.eurlex.document import EurLexDocument
from eke.domain.identity import CelexIdentifier


@runtime_checkable
class EurLexClient(Protocol):
    """Retrieve legal content by canonical CELEX identifier."""

    def fetch_document(
        self,
        celex_identifier: CelexIdentifier,
        *,
        accept: str = "application/rdf+xml",
    ) -> EurLexDocument:
        """Return one document payload from EUR-Lex/Cellar."""
