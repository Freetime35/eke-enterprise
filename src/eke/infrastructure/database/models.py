from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from eke.infrastructure.database.base import Base


class ResourceModel(Base):
    """Persistence model for a serialized Resource aggregate."""

    __tablename__ = "resources"

    resource_uuid: Mapped[str] = mapped_column(String(36), primary_key=True)
    payload: Mapped[str] = mapped_column(Text, nullable=False)


class ResourceIdentifierModel(Base):
    """Search index for Resource business identifiers."""

    __tablename__ = "resource_identifiers"
    __table_args__ = (
        UniqueConstraint(
            "scheme",
            "value",
            name="uq_resource_identifier_scheme_value",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    resource_uuid: Mapped[str] = mapped_column(
        ForeignKey("resources.resource_uuid", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    scheme: Mapped[str] = mapped_column(String(64), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
