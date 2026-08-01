"""HTTP route modules."""

from eke.presentation.api.routes.resource_titles import (
    router as resource_titles_router,
)
from eke.presentation.api.routes.resources import router as resources_router
from eke.presentation.api.routes.system import router as system_router

__all__ = [
    "resource_titles_router",
    "resources_router",
    "system_router",
]
