"""Create the import job persistence schema.

Revision ID: 20260801_0002
Revises: 20260801_0001
Create Date: 2026-08-01 23:55:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260801_0002"
down_revision: str | None = "20260801_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the import_jobs table."""
    op.create_table(
        "import_jobs",
        sa.Column(
            "job_uuid",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=32),
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
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint(
            "job_uuid",
            name="pk_import_jobs",
        ),
    )
    op.create_index(
        "ix_import_jobs_status_created_at",
        "import_jobs",
        ["status", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    """Drop the import_jobs table."""
    op.drop_index(
        "ix_import_jobs_status_created_at",
        table_name="import_jobs",
    )
    op.drop_table("import_jobs")
