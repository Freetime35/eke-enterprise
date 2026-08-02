"""Tests for financial classification canonical mapping."""

from eke.application.eurlex import (
    EurLexClassification,
    EurLexMetadata,
    FinancialClassificationCategory,
)
from eke.application.eurlex.full_resource_mapper import (
    map_classifications,
)
from eke.domain.identity import CelexIdentifier
from eke.domain.localization import LanguageCode


def test_mapper_keeps_only_english_financial_concepts() -> None:
    metadata = EurLexMetadata(
        celex_identifier=CelexIdentifier.parse(
            "32023R1114"
        ),
        classifications=(
            EurLexClassification(
                uri="http://eurovoc.europa.eu/1001",
                code="1001",
                language=LanguageCode("en"),
                label="financial institution",
                financial_category=(
                    FinancialClassificationCategory
                    .FINANCIAL_INSTITUTION
                ),
            ),
            EurLexClassification(
                uri="http://eurovoc.europa.eu/1002",
                code="1002",
                language=LanguageCode("fr"),
                label="institution financière",
                financial_category=(
                    FinancialClassificationCategory
                    .FINANCIAL_INSTITUTION
                ),
            ),
            EurLexClassification(
                uri="http://eurovoc.europa.eu/1003",
                code="1003",
                language=LanguageCode("en"),
                label="agriculture",
            ),
        ),
    )

    concepts = map_classifications(metadata)

    assert len(concepts) == 1
    assert concepts[0].code == "1001"
    assert concepts[0].label.value == (
        "financial institution"
    )
