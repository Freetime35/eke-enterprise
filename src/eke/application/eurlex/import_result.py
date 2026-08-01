"""Result of one EUR-Lex Resource import."""

from __future__ import annotations

from dataclasses import dataclass

from eke.domain.resources import Resource


@dataclass(frozen=True, slots=True)
class EurLexImportResult:
    """Report the canonical Resource and whether it was created."""

    resource: Resource
    created: bool

    def __post_init__(self) -> None:
        if not isinstance(self.resource, Resource):
            raise TypeError("resource must be a Resource")
        if not isinstance(self.created, bool):
            raise TypeError("created must be a boolean")
