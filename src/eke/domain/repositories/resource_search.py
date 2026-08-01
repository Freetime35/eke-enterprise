"""Search criteria and results for Resource repositories."""

from __future__ import annotations

from dataclasses import dataclass

from eke.domain.identity import IdentifierScheme
from eke.domain.resources import Resource, ResourceStatus, ResourceType


@dataclass(frozen=True, slots=True)
class ResourceSearchCriteria:
    """Define filters and pagination for Resource searches."""

    identifier_scheme: IdentifierScheme | None = None
    resource_type: ResourceType | None = None
    status: ResourceStatus | None = None
    limit: int = 20
    offset: int = 0

    def __post_init__(self) -> None:
        if (
            self.identifier_scheme is not None
            and not isinstance(
                self.identifier_scheme,
                IdentifierScheme,
            )
        ):
            raise TypeError(
                "identifier_scheme must be an "
                "IdentifierScheme or None"
            )

        if (
            self.resource_type is not None
            and not isinstance(
                self.resource_type,
                ResourceType,
            )
        ):
            raise TypeError(
                "resource_type must be a ResourceType or None"
            )

        if (
            self.status is not None
            and not isinstance(self.status, ResourceStatus)
        ):
            raise TypeError(
                "status must be a ResourceStatus or None"
            )

        if not isinstance(self.limit, int):
            raise TypeError("limit must be an integer")
        if not 1 <= self.limit <= 100:
            raise ValueError(
                "limit must be between 1 and 100"
            )

        if not isinstance(self.offset, int):
            raise TypeError("offset must be an integer")
        if self.offset < 0:
            raise ValueError(
                "offset must be greater than or equal to zero"
            )


@dataclass(frozen=True, slots=True)
class ResourceSearchPage:
    """Represent one stable page of Resource search results."""

    items: tuple[Resource, ...]
    total: int
    limit: int
    offset: int

    def __post_init__(self) -> None:
        if not isinstance(self.items, tuple):
            raise TypeError("items must be a tuple")
        if not all(
            isinstance(item, Resource)
            for item in self.items
        ):
            raise TypeError(
                "items must contain only Resource instances"
            )

        if not isinstance(self.total, int):
            raise TypeError("total must be an integer")
        if self.total < 0:
            raise ValueError(
                "total must be greater than or equal to zero"
            )

        if not isinstance(self.limit, int):
            raise TypeError("limit must be an integer")
        if self.limit < 1:
            raise ValueError(
                "limit must be greater than zero"
            )

        if not isinstance(self.offset, int):
            raise TypeError("offset must be an integer")
        if self.offset < 0:
            raise ValueError(
                "offset must be greater than or equal to zero"
            )
