"""Transport-neutral EUR-Lex document representation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from eke.domain.identity import CelexIdentifier


@dataclass(frozen=True, slots=True)
class EurLexDocument:
    """Represent one payload retrieved for a CELEX identifier."""

    celex_identifier: CelexIdentifier
    content_type: str
    content: bytes
    source_url: str
    retrieved_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(
            self.celex_identifier,
            CelexIdentifier,
        ):
            raise TypeError(
                "celex_identifier must be a CelexIdentifier"
            )
        if not isinstance(self.content_type, str):
            raise TypeError("content_type must be a string")
        if not self.content_type.strip():
            raise ValueError("content_type must not be empty")
        if not isinstance(self.content, bytes):
            raise TypeError("content must be bytes")
        if not self.content:
            raise ValueError("content must not be empty")
        if not isinstance(self.source_url, str):
            raise TypeError("source_url must be a string")
        if not self.source_url.strip():
            raise ValueError("source_url must not be empty")
        if not isinstance(self.retrieved_at, datetime):
            raise TypeError(
                "retrieved_at must be a datetime"
            )
        if (
            self.retrieved_at.tzinfo is None
            or self.retrieved_at.utcoffset() is None
        ):
            raise ValueError(
                "retrieved_at must be timezone-aware"
            )
