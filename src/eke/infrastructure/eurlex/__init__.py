"""EUR-Lex infrastructure adapters."""

from eke.infrastructure.eurlex.httpx_client import (
    DEFAULT_CELEX_BASE_URL,
    HttpxEurLexClient,
)

__all__ = [
    "DEFAULT_CELEX_BASE_URL",
    "HttpxEurLexClient",
]
