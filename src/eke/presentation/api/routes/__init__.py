"""HTTP route modules."""

from eke.presentation.api.routes.eurlex_bulk_imports import (
    router as eurlex_bulk_imports_router,
)
from eke.presentation.api.routes.eurlex_imports import (
    router as eurlex_imports_router,
)
from eke.presentation.api.routes.import_jobs import (
    router as import_jobs_router,
)
from eke.presentation.api.routes.resource_classifications import (
    router as resource_classifications_router,
)
from eke.presentation.api.routes.resource_provenance import (
    router as resource_provenance_router,
)
from eke.presentation.api.routes.resource_relationships import (
    router as resource_relationships_router,
)
from eke.presentation.api.routes.resource_titles import (
    router as resource_titles_router,
)
from eke.presentation.api.routes.resource_versions import (
    router as resource_versions_router,
)
from eke.presentation.api.routes.resources import (
    router as resources_router,
)
from eke.presentation.api.routes.system import (
    router as system_router,
)

__all__ = [
    "eurlex_bulk_imports_router",
    "eurlex_imports_router",
    "import_jobs_router",
    "resource_classifications_router",
    "resource_provenance_router",
    "resource_relationships_router",
    "resource_titles_router",
    "resource_versions_router",
    "resources_router",
    "system_router",
]
