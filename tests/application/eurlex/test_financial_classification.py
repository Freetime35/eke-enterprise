"""Tests for English financial classification rules."""

import pytest

from eke.application.eurlex import (
    FinancialClassificationCategory,
    classify_financial_label,
)


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        (
            "banking supervision",
            FinancialClassificationCategory.FINANCIAL_SUPERVISION,
        ),
        (
            "credit institution",
            FinancialClassificationCategory.CREDIT,
        ),
        (
            "financial institution",
            FinancialClassificationCategory.FINANCIAL_INSTITUTION,
        ),
        (
            "payment service",
            FinancialClassificationCategory.PAYMENTS,
        ),
        (
            "capital market",
            FinancialClassificationCategory.CAPITAL_MARKETS,
        ),
        (
            "investment service",
            FinancialClassificationCategory.INVESTMENT_SERVICES,
        ),
    ],
)
def test_classifies_financial_labels(
    label: str,
    expected: FinancialClassificationCategory,
) -> None:
    assert classify_financial_label(label) is expected


@pytest.mark.parametrize(
    "label",
    [
        "agriculture",
        "environmental protection",
        "public health",
        "transport policy",
    ],
)
def test_rejects_non_financial_labels(
    label: str,
) -> None:
    assert classify_financial_label(label) is None
