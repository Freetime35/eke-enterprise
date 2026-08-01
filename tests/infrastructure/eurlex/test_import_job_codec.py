"""Tests for the ImportJob JSON codec."""

from datetime import UTC, datetime

from eke.domain.imports import ImportJob
from eke.infrastructure.eurlex.import_job_codec import (
    decode_import_job,
    encode_import_job,
)

NOW = datetime(2026, 8, 1, 22, 0, tzinfo=UTC)


def test_codec_preserves_timezone_aware_job() -> None:
    job = ImportJob.create(
        ("32023R1114",),
        created_at=NOW,
    )

    decoded = decode_import_job(
        encode_import_job(job)
    )

    assert decoded == job
    assert decoded.created_at.tzinfo is not None
