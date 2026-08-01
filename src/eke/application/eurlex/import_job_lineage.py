"""Import-job retry lineage value."""

from __future__ import annotations

from dataclasses import dataclass

from eke.domain.imports import ImportJob


@dataclass(frozen=True, slots=True)
class ImportJobLineage:
    """Represent a retry chain from origin to current job."""

    items: tuple[ImportJob, ...]

    def __post_init__(self) -> None:
        if not self.items:
            raise ValueError("items must not be empty")
        if any(
            not isinstance(item, ImportJob)
            for item in self.items
        ):
            raise TypeError(
                "items must contain only ImportJob values"
            )

        for previous, current in zip(
            self.items,
            self.items[1:],
            strict=False,
        ):
            if (
                current.retried_from_job_uuid
                != previous.job_uuid
            ):
                raise ValueError(
                    "items must form a valid retry chain"
                )

    @property
    def root(self) -> ImportJob:
        """Return the first job in the chain."""
        return self.items[0]

    @property
    def current(self) -> ImportJob:
        """Return the requested job at the end of the chain."""
        return self.items[-1]

    @property
    def depth(self) -> int:
        """Return the number of retry edges."""
        return len(self.items) - 1
