"""Runtime settings for the HTTP application."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class APISettings:
    """Configure the FastAPI application and database adapter."""

    application_name: str = "EKE Enterprise"
    application_version: str = "0.0.1"
    environment: str = "development"
    database_url: str = "sqlite+pysqlite:///eke-enterprise.db"
    docs_enabled: bool = True

    def __post_init__(self) -> None:
        for field_name in (
            "application_name",
            "application_version",
            "environment",
            "database_url",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str):
                raise TypeError(f"{field_name} must be a string")
            if not value.strip():
                raise ValueError(f"{field_name} must not be empty")

        if not isinstance(self.docs_enabled, bool):
            raise TypeError("docs_enabled must be a bool")

    @classmethod
    def from_environment(cls) -> APISettings:
        """Build settings from EKE-prefixed environment variables."""
        return cls(
            application_name=os.getenv(
                "EKE_APPLICATION_NAME",
                "EKE Enterprise",
            ),
            application_version=os.getenv(
                "EKE_APPLICATION_VERSION",
                "0.0.1",
            ),
            environment=os.getenv(
                "EKE_ENVIRONMENT",
                "development",
            ),
            database_url=os.getenv(
                "EKE_DATABASE_URL",
                "sqlite+pysqlite:///eke-enterprise.db",
            ),
            docs_enabled=_parse_bool(
                os.getenv("EKE_DOCS_ENABLED", "true")
            ),
        )


def _parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(
        "boolean environment value must be one of "
        "true, false, 1, 0, yes, no, on, off"
    )
