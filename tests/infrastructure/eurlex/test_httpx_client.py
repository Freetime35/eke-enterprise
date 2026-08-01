"""Tests for the HTTPX EUR-Lex adapter."""

from datetime import UTC, datetime

import httpx
import pytest

from eke.application.eurlex import (
    EurLexClient,
    EurLexDocumentNotFoundError,
    EurLexUpstreamError,
)
from eke.domain.identity import CelexIdentifier
from eke.infrastructure.eurlex import HttpxEurLexClient

NOW = datetime(2026, 8, 1, 12, 0, tzinfo=UTC)


def make_http_client(
    handler: httpx.MockTransport,
) -> httpx.Client:
    return httpx.Client(
        transport=handler,
        follow_redirects=True,
    )


def test_adapter_satisfies_client_protocol() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            request=request,
            content=b"payload",
        )
    )
    adapter = HttpxEurLexClient(
        client=make_http_client(transport)
    )

    assert isinstance(adapter, EurLexClient)


def test_fetch_document_uses_celex_url_and_accept_header() -> None:
    def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        assert request.url == (
            "https://publications.europa.eu/"
            "resource/celex/32023R1114"
        )
        assert (
            request.headers["accept"]
            == "application/rdf+xml"
        )
        return httpx.Response(
            200,
            request=request,
            headers={
                "Content-Type": (
                    "application/rdf+xml; charset=utf-8"
                )
            },
            content=b"<rdf:RDF />",
        )

    adapter = HttpxEurLexClient(
        client=make_http_client(
            httpx.MockTransport(handler)
        ),
        clock=lambda: NOW,
    )

    document = adapter.fetch_document(
        CelexIdentifier.parse("32023R1114")
    )

    assert document.content_type == "application/rdf+xml"
    assert document.content == b"<rdf:RDF />"
    assert document.retrieved_at == NOW


def test_fetch_document_maps_not_found() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            404,
            request=request,
        )
    )
    adapter = HttpxEurLexClient(
        client=make_http_client(transport)
    )

    with pytest.raises(
        EurLexDocumentNotFoundError,
        match="32023R1114",
    ):
        adapter.fetch_document(
            CelexIdentifier.parse("32023R1114")
        )


def test_fetch_document_maps_upstream_status() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            503,
            request=request,
        )
    )
    adapter = HttpxEurLexClient(
        client=make_http_client(transport)
    )

    with pytest.raises(
        EurLexUpstreamError,
        match="HTTP 503",
    ):
        adapter.fetch_document(
            CelexIdentifier.parse("32023R1114")
        )


def test_fetch_document_maps_transport_failure() -> None:
    def handler(
        request: httpx.Request,
    ) -> httpx.Response:
        raise httpx.ConnectError(
            "connection failed",
            request=request,
        )

    adapter = HttpxEurLexClient(
        client=make_http_client(
            httpx.MockTransport(handler)
        )
    )

    with pytest.raises(
        EurLexUpstreamError,
        match="request failed",
    ):
        adapter.fetch_document(
            CelexIdentifier.parse("32023R1114")
        )
