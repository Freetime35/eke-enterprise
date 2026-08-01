"""Default ASGI application entry point."""

from eke.presentation.api.app import create_app

app = create_app()
