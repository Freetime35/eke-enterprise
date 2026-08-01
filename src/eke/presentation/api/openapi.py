"""Stable OpenAPI metadata and operation identifiers."""

from __future__ import annotations

from fastapi.routing import APIRoute

OPENAPI_TAGS: list[dict[str, str]] = [
    {
        "name": "system",
        "description": "Application health and readiness endpoints.",
    },
    {
        "name": "resources",
        "description": (
            "Create, retrieve, update, delete, search, and paginate "
            "canonical legal resources."
        ),
    },
    {
        "name": "resource-titles",
        "description": (
            "Manage localized and temporally valid Resource titles."
        ),
    },
    {
        "name": "resource-versions",
        "description": (
            "Manage ordered Resource versions and version history."
        ),
    },
    {
        "name": "resource-relationships",
        "description": (
            "Manage directed relationships between Resources."
        ),
    },
    {
        "name": "resource-provenance",
        "description": (
            "Manage immutable acquisition provenance records."
        ),
    },
    {
        "name": "resource-classifications",
        "description": (
            "Manage controlled-vocabulary classification assignments."
        ),
    },
]


def generate_operation_id(route: APIRoute) -> str:
    """Generate a deterministic operation identifier from tag and name."""
    raw_tag = route.tags[0] if route.tags else "default"
    tag = str(raw_tag)
    normalized_tag = tag.replace("-", "_")
    return f"{normalized_tag}_{route.name}"
