"""HTTPX adapter for the Publications Office CELEX resolver."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

import httpx

from eke.application.eurlex import (
    EurLexClient,
    EurLexDocument,
    EurLexDocumentNotFoundError,
    EurLexUpstreamError,
)
from eke.domain.identity import CelexIdentifier

DEFAULT_CELEX_BASE_URL = (
    "https://publications.europa.eu/resource/celex"
)


class HttpxEurLexClient:
    """Retrieve CELEX resources using HTTP content negotiation."""

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_CELEX_BASE_URL,
        timeout: float = 20.0,
        client: httpx.Client | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        if not isinstance(base_url, str):
            raise TypeError("base_url must be a string")
        normalized_base_url = base_url.rstrip("/")
        if not normalized_base_url:
            raise ValueError("base_url must not be empty")
        if not isinstance(timeout, (int, float)):
            raise TypeError("timeout must be numeric")
        if timeout <= 0:
            raise ValueError("timeout must be greater than zero")
        if client is not None and not isinstance(
            client,
            httpx.Client,
        ):
            raise TypeError(
                "client must be an httpx.Client or None"
            )

        self._base_url = normalized_base_url
        self._client = client or httpx.Client(
            timeout=float(timeout),
            follow_redirects=True,
        )
        self._owns_client = client is None
        self._clock = clock or (
            lambda: datetime.now(UTC)
        )

    def fetch_document(
        self,
        celex_identifier: CelexIdentifier,
        *,
        accept: str = "application/rdf+xml",
    ) -> EurLexDocument:
        """Retrieve one CELEX resource payload."""
        if not isinstance(
            celex_identifier,
            CelexIdentifier,
        ):
            raise TypeError(
                "celex_identifier must be a CelexIdentifier"
            )
        if not isinstance(accept, str):
            raise TypeError("accept must be a string")
        if not accept.strip():
            raise ValueError("accept must not be empty")

        url = f"{self._base_url}/{celex_identifier.value}"

        try:
            response = self._client.get(
                url,
                headers={"Accept": accept},
            )
        except httpx.HTTPError as exc:
            raise EurLexUpstreamError(
                "EUR-Lex request failed"
            ) from exc

        if response.status_code == 404:
            raise EurLexDocumentNotFoundError(
                "EUR-Lex document not found: "
                f"{celex_identifier.value}"
            )
        if response.status_code >= 400:
            raise EurLexUpstreamError(
                "EUR-Lex returned HTTP "
                f"{response.status_code}"
            )

        content_type = response.headers.get(
            "content-type",
            "application/octet-stream",
        ).split(";", maxsplit=1)[0].strip()

        return EurLexDocument(
            celex_identifier=celex_identifier,
            content_type=content_type,
            content=response.content,
            source_url=str(response.url),
            retrieved_at=self._clock(),
        )

    def close(self) -> None:
        """Close the internally-owned HTTP client."""
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> HttpxEurLexClient:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None:
        self.close()


eurlex_client_contract: type[EurLexClient]
eurlex_client_contract = HttpxEurLexClient
