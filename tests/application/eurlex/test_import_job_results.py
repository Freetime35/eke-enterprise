"""Tests for persisted import-job result parsing."""

from json import dumps

import pytest

from eke.application.eurlex import (
    EurLexBulkImportStatus,
)
from eke.application.eurlex.import_job_results import (
    ImportJobResultError,
    parse_import_job_results,
)


def test_parse_import_job_results() -> None:
    items = parse_import_job_results(
        dumps(
            [
                {
                    "celex": "32023R1114",
                    "status": "CREATED",
                    "resource_uuid": "resource-1",
                    "error_code": None,
                    "detail": None,
                },
                {
                    "celex": "32024R0001",
                    "status": "FAILED",
                    "resource_uuid": None,
                    "error_code": "INVALID_METADATA",
                    "detail": "missing resource type",
                },
            ]
        )
    )

    assert len(items) == 2
    assert (
        items[0].status
        is EurLexBulkImportStatus.CREATED
    )
    assert items[1].error_code == "INVALID_METADATA"


def test_parse_import_job_results_rejects_status() -> None:
    with pytest.raises(
        ImportJobResultError,
        match="invalid status",
    ):
        parse_import_job_results(
            dumps(
                [
                    {
                        "celex": "32023R1114",
                        "status": "UNKNOWN",
                    }
                ]
            )
        )
