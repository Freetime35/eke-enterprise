"""EUR-Lex metadata parser application port."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from eke.application.eurlex.document import EurLexDocument
from eke.application.eurlex.metadata import EurLexMetadata


@runtime_checkable
class EurLexMetadataParser(Protocol):
    """Parse transport-neutral metadata from an EUR-Lex document."""

    def parse(
        self,
        document: EurLexDocument,
    ) -> EurLexMetadata:
        """Return metadata extracted from a retrieved document."""
