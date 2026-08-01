"""Resource concepts for the EKE Enterprise domain model."""

from eke.domain.resources.resource import Resource
from eke.domain.resources.resource_status import ResourceStatus
from eke.domain.resources.resource_title import ResourceTitle
from eke.domain.resources.resource_type import ResourceType

__all__ = [
    "Resource",
    "ResourceStatus",
    "ResourceTitle",
    "ResourceType",
]
