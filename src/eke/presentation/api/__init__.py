"""FastAPI presentation adapter."""

from eke.presentation.api.app import create_app
from eke.presentation.api.settings import APISettings

__all__ = ["APISettings", "create_app"]
