"""Create the initial Resource persistence schema.

Revision ID: 20260801_0001
Revises:
Create Date: 2026-08-01 18:30:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260801_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create Resource aggregate and identifier-index tables."""
    op.create_table(
        "resources",
        sa.Column(
            "resource_uuid",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "payload_version",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "payload",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint(
            "resource_uuid",
            name="pk_resources",
        ),
    )
    op.create_index(
        "ix_resources_updated_at",
        "resources",
        ["updated_at"],
        unique=False,
    )

    op.create_table(
        "resource_identifiers",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "resource_uuid",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "scheme",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column(
            "value",
            sa.Text(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["resource_uuid"],
            ["resources.resource_uuid"],
            name=(
                "fk_resource_identifiers_"
                "resource_uuid_resources"
            ),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name="pk_resource_identifiers",
        ),
        sa.UniqueConstraint(
            "scheme",
            "value",
            name=(
                "uq_resource_identifiers_"
                "scheme_value"
            ),
        ),
    )
    op.create_index(
        "ix_resource_identifiers_resource_uuid",
        "resource_identifiers",
        ["resource_uuid"],
        unique=False,
    )
    op.create_index(
        "ix_resource_identifiers_scheme_value",
        "resource_identifiers",
        ["scheme", "value"],
        unique=False,
    )


def downgrade() -> None:
    """Drop the initial Resource persistence schema."""
    op.drop_index(
        "ix_resource_identifiers_scheme_value",
        table_name="resource_identifiers",
    )
    op.drop_index(
        "ix_resource_identifiers_resource_uuid",
        table_name="resource_identifiers",
    )
    op.drop_table("resource_identifiers")
    op.drop_index(
        "ix_resources_updated_at",
        table_name="resources",
    )
    op.drop_table("resources")
