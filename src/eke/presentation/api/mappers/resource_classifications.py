"""Mapping between ClassificationConcept and HTTP schemas."""

from eke.domain.classification import ClassificationConcept
from eke.domain.localization import LanguageCode, LocalizedText
from eke.domain.temporal import ValidityPeriod
from eke.presentation.api.schemas.resource_classifications import (
    ResourceClassificationCreateRequest,
    ResourceClassificationResponse,
)


def resource_classification_from_request(
    request: ResourceClassificationCreateRequest,
) -> ClassificationConcept:
    """Create a ClassificationConcept from an HTTP request."""
    return ClassificationConcept(
        scheme=request.scheme,
        code=request.code,
        label=LocalizedText(
            LanguageCode(request.language),
            request.label,
        ),
        validity=ValidityPeriod(
            request.valid_from,
            request.valid_to,
        ),
    )


def resource_classification_to_response(
    classification: ClassificationConcept,
) -> ResourceClassificationResponse:
    """Convert a classification to an HTTP response."""
    return ResourceClassificationResponse(
        scheme=classification.scheme,
        code=classification.code,
        language=classification.language.value,
        label=classification.label_value,
        valid_from=classification.validity.valid_from,
        valid_to=classification.validity.valid_to,
    )
