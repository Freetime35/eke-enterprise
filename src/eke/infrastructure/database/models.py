"""SQLAlchemy ORM models for Resource persistence."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from eke.infrastructure.database.base import Base


class ResourceModel(Base):
    """Persistence model for a serialized Resource aggregate."""

    __tablename__ = "resources"
    __table_args__ = (
        Index("ix_resources_updated_at", "updated_at"),
    )

    resource_uuid: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
    )
    payload_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    identifiers: Mapped[list[ResourceIdentifierModel]] = relationship(
        back_populates="resource",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )


class ResourceIdentifierModel(Base):
    """Search index for Resource business identifiers."""

    __tablename__ = "resource_identifiers"
    __table_args__ = (
        UniqueConstraint(
            "scheme",
            "value",
            name="uq_resource_identifiers_scheme_value",
        ),
        Index(
            "ix_resource_identifiers_resource_uuid",
            "resource_uuid",
        ),
        Index(
            "ix_resource_identifiers_scheme_value",
            "scheme",
            "value",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    resource_uuid: Mapped[str] = mapped_column(
        ForeignKey(
            "resources.resource_uuid",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    scheme: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    value: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    resource: Mapped[ResourceModel] = relationship(
        back_populates="identifiers",
    )
