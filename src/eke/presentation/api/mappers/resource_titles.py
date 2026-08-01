"""Mapping between ResourceTitle and HTTP schemas."""

from eke.domain.localization import LanguageCode, LocalizedText
from eke.domain.resources import ResourceTitle
from eke.domain.temporal import ValidityPeriod
from eke.presentation.api.schemas.resource_titles import (
    ResourceTitleCreateRequest,
    ResourceTitleResponse,
)


def resource_title_from_request(
    request: ResourceTitleCreateRequest,
) -> ResourceTitle:
    return ResourceTitle(
        text=LocalizedText(LanguageCode(request.language), request.value),
        validity=ValidityPeriod(request.valid_from, request.valid_to),
    )


def resource_title_to_response(title: ResourceTitle) -> ResourceTitleResponse:
    return ResourceTitleResponse(
        language=title.text.language.value,
        value=title.text.value,
        valid_from=title.validity.valid_from,
        valid_to=title.validity.valid_to,
    )
