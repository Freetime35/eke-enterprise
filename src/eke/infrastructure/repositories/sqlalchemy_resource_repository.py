"""SQLAlchemy ResourceRepository implementation."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from eke.domain.identity import BusinessIdentifier, ResourceUUID
from eke.domain.repositories import ResourceRepository
from eke.domain.resources import Resource
from eke.infrastructure.database.models import (
    ResourceIdentifierModel,
    ResourceModel,
)
from eke.infrastructure.repositories.resource_codec import (
    RESOURCE_PAYLOAD_VERSION,
    decode_resource,
    encode_resource,
)


class SQLAlchemyResourceRepository:
    """Persist Resource aggregates through SQLAlchemy."""

    def __init__(
        self,
        session_source: Session | sessionmaker[Session],
    ) -> None:
        if not isinstance(
            session_source,
            (Session, sessionmaker),
        ):
            raise TypeError(
                "session_source must be a Session or sessionmaker"
            )
        self._session_source = session_source

    @contextmanager
    def _session(
        self,
        *,
        write: bool = False,
    ) -> Iterator[Session]:
        if isinstance(self._session_source, Session):
            yield self._session_source
            return

        if write:
            with self._session_source.begin() as session:
                yield session
        else:
            with self._session_source() as session:
                yield session

    def save(self, resource: Resource) -> None:
        """Create or replace a Resource aggregate."""
        if not isinstance(resource, Resource):
            raise TypeError("resource must be a Resource")

        resource_key = str(resource.resource_uuid)
        with self._session(write=True) as session:
            model = session.get(ResourceModel, resource_key)
            if model is None:
                model = ResourceModel(
                    resource_uuid=resource_key,
                    payload_version=RESOURCE_PAYLOAD_VERSION,
                    payload=encode_resource(resource),
                )
                session.add(model)
            else:
                model.payload_version = (
                    RESOURCE_PAYLOAD_VERSION
                )
                model.payload = encode_resource(resource)
                model.identifiers.clear()

            model.identifiers.extend(
                ResourceIdentifierModel(
                    scheme=identifier.scheme.value,
                    value=identifier.value,
                )
                for identifier in resource.identifiers
            )

            try:
                session.flush()
            except IntegrityError as exc:
                raise ValueError(
                    "business identifier already belongs "
                    "to another resource"
                ) from exc

    def get(
        self,
        resource_uuid: ResourceUUID,
    ) -> Resource | None:
        """Return a Resource by internal identity."""
        self._validate_resource_uuid(resource_uuid)

        with self._session() as session:
            model = session.get(
                ResourceModel,
                str(resource_uuid),
            )
            return (
                decode_resource(model.payload)
                if model
                else None
            )

    def get_by_identifier(
        self,
        identifier: BusinessIdentifier,
    ) -> Resource | None:
        """Return a Resource by business identifier."""
        if not isinstance(identifier, BusinessIdentifier):
            raise TypeError(
                "identifier must be a BusinessIdentifier"
            )

        statement = (
            select(ResourceModel)
            .join(ResourceModel.identifiers)
            .where(
                ResourceIdentifierModel.scheme
                == identifier.scheme.value,
                ResourceIdentifierModel.value
                == identifier.value,
            )
        )

        with self._session() as session:
            model = session.scalar(statement)
            return (
                decode_resource(model.payload)
                if model
                else None
            )

    def exists(self, resource_uuid: ResourceUUID) -> bool:
        """Return whether a Resource exists."""
        self._validate_resource_uuid(resource_uuid)

        with self._session() as session:
            return (
                session.get(
                    ResourceModel,
                    str(resource_uuid),
                )
                is not None
            )

    def delete(self, resource_uuid: ResourceUUID) -> bool:
        """Delete a Resource aggregate."""
        self._validate_resource_uuid(resource_uuid)

        with self._session(write=True) as session:
            model = session.get(
                ResourceModel,
                str(resource_uuid),
            )
            if model is None:
                return False

            session.delete(model)
            session.flush()
            return True

    @staticmethod
    def _validate_resource_uuid(
        resource_uuid: ResourceUUID,
    ) -> None:
        if not isinstance(resource_uuid, ResourceUUID):
            raise TypeError(
                "resource_uuid must be a ResourceUUID"
            )


resource_repository_contract: type[ResourceRepository]
resource_repository_contract = SQLAlchemyResourceRepository
