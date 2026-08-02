"""English financial classification rules for EUR-Lex concepts."""

from __future__ import annotations

from enum import StrEnum


class FinancialClassificationCategory(StrEnum):
    """Canonical financial topic categories."""

    BANKING = "BANKING"
    FINANCIAL_INSTITUTION = "FINANCIAL_INSTITUTION"
    FINANCIAL_SERVICE = "FINANCIAL_SERVICE"
    PAYMENTS = "PAYMENTS"
    CREDIT = "CREDIT"
    CAPITAL_MARKETS = "CAPITAL_MARKETS"
    INVESTMENT_SERVICES = "INVESTMENT_SERVICES"
    INSURANCE = "INSURANCE"
    FINANCIAL_SUPERVISION = "FINANCIAL_SUPERVISION"
    FINANCIAL_REGULATION = "FINANCIAL_REGULATION"


_CATEGORY_TERMS: tuple[
    tuple[FinancialClassificationCategory, tuple[str, ...]],
    ...,
] = (
    (
        FinancialClassificationCategory.FINANCIAL_SUPERVISION,
        (
            "prudential supervision",
            "banking supervision",
            "financial supervision",
            "supervisory authority",
        ),
    ),
    (
        FinancialClassificationCategory.FINANCIAL_REGULATION,
        (
            "financial regulation",
            "banking regulation",
            "financial law",
            "prudential requirement",
            "capital requirement",
            "anti-money laundering",
            "money laundering",
        ),
    ),
    (
        FinancialClassificationCategory.INVESTMENT_SERVICES,
        (
            "investment service",
            "investment firm",
            "asset management",
            "fund management",
            "collective investment",
            "investment fund",
        ),
    ),
    (
        FinancialClassificationCategory.CAPITAL_MARKETS,
        (
            "capital market",
            "financial market",
            "securities market",
            "stock exchange",
            "securities",
            "market infrastructure",
            "financial instrument",
        ),
    ),
    (
        FinancialClassificationCategory.PAYMENTS,
        (
            "payment service",
            "payment system",
            "electronic money",
            "payment institution",
            "money transfer",
        ),
    ),
    (
        FinancialClassificationCategory.CREDIT,
        (
            "consumer credit",
            "mortgage credit",
            "credit agreement",
            "credit institution",
            "lending",
            "loan",
        ),
    ),
    (
        FinancialClassificationCategory.FINANCIAL_INSTITUTION,
        (
            "financial institution",
            "credit institution",
            "monetary financial institution",
            "central bank",
        ),
    ),
    (
        FinancialClassificationCategory.BANKING,
        (
            "banking",
            "bank",
            "deposit guarantee",
            "bank resolution",
        ),
    ),
    (
        FinancialClassificationCategory.INSURANCE,
        (
            "insurance undertaking",
            "insurance service",
            "reinsurance",
            "insurance market",
        ),
    ),
    (
        FinancialClassificationCategory.FINANCIAL_SERVICE,
        (
            "financial service",
            "financial sector",
            "financial activity",
            "financial intermediary",
        ),
    ),
)


def classify_financial_label(
    label: str,
) -> FinancialClassificationCategory | None:
    """Classify one English label inside the financial scope."""
    if not isinstance(label, str):
        raise TypeError("label must be a string")

    normalized = " ".join(label.casefold().split())
    if not normalized:
        return None

    for category, terms in _CATEGORY_TERMS:
        if any(term in normalized for term in terms):
            return category

    return None
