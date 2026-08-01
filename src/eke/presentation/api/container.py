"""Application composition container."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from eke.application import UnitOfWork
from eke.application.resources import ResourceService, ResourceTitleService
from eke.infrastructure.unit_of_work import SQLAlchemyUnitOfWork


@dataclass(frozen=True, slots=True)
class ApplicationContainer:
    engine: Engine
    session_factory: sessionmaker[Session]
    unit_of_work_factory: Callable[[], UnitOfWork]

    def resource_service(self) -> ResourceService:
        return ResourceService(self.unit_of_work_factory)

    def resource_title_service(self) -> ResourceTitleService:
        return ResourceTitleService(self.unit_of_work_factory)


def build_container(
    engine: Engine,
    session_factory: sessionmaker[Session],
) -> ApplicationContainer:
    if not isinstance(engine, Engine):
        raise TypeError("engine must be an Engine")
    if not isinstance(session_factory, sessionmaker):
        raise TypeError("session_factory must be a sessionmaker")

    def unit_of_work_factory() -> UnitOfWork:
        return SQLAlchemyUnitOfWork(session_factory)

    return ApplicationContainer(
        engine=engine,
        session_factory=session_factory,
        unit_of_work_factory=unit_of_work_factory,
    )
