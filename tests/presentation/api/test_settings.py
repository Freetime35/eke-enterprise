"""Tests for APISettings."""

from __future__ import annotations

import pytest

from eke.presentation.api import APISettings


def test_defaults_are_valid() -> None:
    settings = APISettings()

    assert settings.application_name == "EKE Enterprise"
    assert settings.docs_enabled


def test_settings_load_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "EKE_APPLICATION_NAME",
        "EKE Test",
    )
    monkeypatch.setenv(
        "EKE_ENVIRONMENT",
        "test",
    )
    monkeypatch.setenv(
        "EKE_DATABASE_URL",
        "sqlite+pysqlite:///:memory:",
    )
    monkeypatch.setenv(
        "EKE_DOCS_ENABLED",
        "false",
    )

    settings = APISettings.from_environment()

    assert settings.application_name == "EKE Test"
    assert settings.environment == "test"
    assert not settings.docs_enabled


@pytest.mark.parametrize(
    "value",
    ["", " ", "\t"],
)
def test_empty_string_settings_are_rejected(
    value: str,
) -> None:
    with pytest.raises(ValueError):
        APISettings(application_name=value)


def test_invalid_environment_boolean_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "EKE_DOCS_ENABLED",
        "sometimes",
    )

    with pytest.raises(
        ValueError,
        match="boolean environment value",
    ):
        APISettings.from_environment()
