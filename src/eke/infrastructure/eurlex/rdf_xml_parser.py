"""RDF/XML metadata parser for Cellar notices."""

from __future__ import annotations

from datetime import date
from xml.etree import ElementTree

from eke.application.eurlex import (
    EurLexDocument,
    EurLexMalformedMetadataError,
    EurLexMetadata,
    EurLexMetadataMismatchError,
    EurLexMetadataParser,
    EurLexOfficialJournalReference,
    EurLexRelationship,
    EurLexTitle,
    EurLexUnsupportedMediaTypeError,
)
from eke.application.eurlex.institutional_provenance import (
    normalize_institutions,
)
from eke.application.eurlex.legal_lifecycle import (
    EurLexAmendmentEvent,
    EurLexLegalLifecycleEvent,
    EurLexLegalLifecycleEventKind,
    normalize_amendment_events,
    normalize_lifecycle_events,
)
from eke.application.eurlex.legal_references import (
    EurLexLegalReference,
    legal_reference_kind_from_predicate,
    normalize_legal_references,
)
from eke.application.eurlex.regulatory_families import (
    detect_regulatory_families,
)
from eke.application.eurlex.relationship_mapper import (
    relationship_type_from_predicate,
)
from eke.application.eurlex.titles import (
    title_kind_from_predicate,
)
from eke.domain.identity import CelexIdentifier
from eke.domain.localization import LanguageCode

_RDF_RESOURCE_ATTRIBUTE = (
    "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"
)
_XML_LANGUAGE_ATTRIBUTE = (
    "{http://www.w3.org/XML/1998/namespace}lang"
)

_SUPPORTED_MEDIA_TYPES = frozenset(
    {
        "application/rdf+xml",
        "application/xml",
        "text/xml",
    }
)

_CELEX_NAMES = frozenset(
    {
        "resource_legal_id_celex",
        "celex",
        "celex_number",
    }
)
_TITLE_NAMES = frozenset(
    {
        "title",
        "work_title",
        "expression_title",
        "resource_legal_title",
        "work_title_short",
        "expression_title_short",
        "resource_legal_title_short",
        "title_short",
        "short_title",
        "work_title_alternative",
        "expression_title_alternative",
        "resource_legal_title_alternative",
        "title_alternative",
        "alternative_title",
    }
)
_DOCUMENT_DATE_NAMES = frozenset(
    {
        "work_date_document",
        "date_document",
    }
)
_PUBLICATION_DATE_NAMES = frozenset(
    {
        "work_date_publication",
        "date_publication",
    }
)
_ENTRY_INTO_FORCE_NAMES = frozenset(
    {
        "work_date_entry-into-force",
        "date_entry-into-force",
        "date_entry_into_force",
    }
)
_END_OF_VALIDITY_NAMES = frozenset(
    {
        "work_date_end-of-validity",
        "date_end-of-validity",
        "date_end_of_validity",
    }
)

_LIFECYCLE_PREDICATES: dict[
    str,
    EurLexLegalLifecycleEventKind,
] = {
    "work_date_document": EurLexLegalLifecycleEventKind.DOCUMENT,
    "date_document": EurLexLegalLifecycleEventKind.DOCUMENT,
    "work_date_adoption": EurLexLegalLifecycleEventKind.ADOPTION,
    "date_adoption": EurLexLegalLifecycleEventKind.ADOPTION,
    "work_date_signature": EurLexLegalLifecycleEventKind.SIGNATURE,
    "date_signature": EurLexLegalLifecycleEventKind.SIGNATURE,
    "work_date_notification": EurLexLegalLifecycleEventKind.NOTIFICATION,
    "date_notification": EurLexLegalLifecycleEventKind.NOTIFICATION,
    "work_date_publication": EurLexLegalLifecycleEventKind.PUBLICATION,
    "date_publication": EurLexLegalLifecycleEventKind.PUBLICATION,
    "work_date_entry-into-force": EurLexLegalLifecycleEventKind.ENTRY_INTO_FORCE,
    "date_entry-into-force": EurLexLegalLifecycleEventKind.ENTRY_INTO_FORCE,
    "date_entry_into_force": EurLexLegalLifecycleEventKind.ENTRY_INTO_FORCE,
    "work_date_taking-effect": EurLexLegalLifecycleEventKind.TAKING_EFFECT,
    "date_taking-effect": EurLexLegalLifecycleEventKind.TAKING_EFFECT,
    "date_taking_effect": EurLexLegalLifecycleEventKind.TAKING_EFFECT,
    "work_date_application": EurLexLegalLifecycleEventKind.APPLICATION,
    "date_application": EurLexLegalLifecycleEventKind.APPLICATION,
    "work_date_transposition": EurLexLegalLifecycleEventKind.TRANSPOSITION_DEADLINE,
    "date_transposition": EurLexLegalLifecycleEventKind.TRANSPOSITION_DEADLINE,
    "transposition_deadline": EurLexLegalLifecycleEventKind.TRANSPOSITION_DEADLINE,
    "work_date_end-of-validity": EurLexLegalLifecycleEventKind.END_OF_VALIDITY,
    "date_end-of-validity": EurLexLegalLifecycleEventKind.END_OF_VALIDITY,
    "date_end_of_validity": EurLexLegalLifecycleEventKind.END_OF_VALIDITY,
    "work_date_repeal": EurLexLegalLifecycleEventKind.REPEAL,
    "date_repeal": EurLexLegalLifecycleEventKind.REPEAL,
    "work_date_withdrawal": EurLexLegalLifecycleEventKind.WITHDRAWAL,
    "date_withdrawal": EurLexLegalLifecycleEventKind.WITHDRAWAL,
}

_AMENDMENT_EVENT_NAMES = frozenset(
    {
        "amendment_event",
        "legal_amendment_event",
        "resource_legal_amendment_event",
    }
)
_AMENDING_CELEX_NAMES = frozenset(
    {
        "amending_celex",
        "amending_act_celex",
    }
)
_AMENDED_CELEX_NAMES = frozenset(
    {
        "amended_celex",
        "amended_act_celex",
    }
)
_AMENDMENT_EFFECTIVE_DATE_NAMES = frozenset(
    {
        "effective_on",
        "date_effect",
        "date_effective",
    }
)

_LEGAL_REFERENCE_ARTICLE_NAMES = frozenset(
    {
        "article",
        "article_label",
        "reference_article",
    }
)

_LANGUAGE_NAMES = frozenset(
    {
        "expression_uses_language",
        "language",
    }
)
_RESOURCE_TYPE_NAMES = frozenset(
    {
        "work_has_resource-type",
        "resource_type",
    }
)
_STATUS_NAMES = frozenset(
    {
        "work_has_status",
        "status",
    }
)
_EUROVOC_NAMES = frozenset(
    {
        "work_is_about_concept_eurovoc",
        "subject",
    }
)

_ELI_NAMES = frozenset(
    {
        "resource_legal_eli",
        "work_eli",
        "eli",
    }
)
_OFFICIAL_JOURNAL_NAMES = frozenset(
    {
        "work_is_published_in_official-journal",
        "published_in_official_journal",
        "official_journal",
    }
)
_OFFICIAL_JOURNAL_NUMBER_NAMES = frozenset(
    {
        "official-journal_number",
        "official_journal_number",
        "oj_number",
    }
)
_OFFICIAL_JOURNAL_PAGE_FIRST_NAMES = frozenset(
    {
        "official-journal_page_first",
        "official_journal_page_first",
        "page_first",
    }
)
_OFFICIAL_JOURNAL_PAGE_LAST_NAMES = frozenset(
    {
        "official-journal_page_last",
        "official_journal_page_last",
        "page_last",
    }
)
_RESPONSIBLE_AGENT_NAMES = frozenset(
    {
        "work_created_by_agent",
        "work_adopted_by_agent",
        "created_by",
        "creator",
    }
)
_RDF_ABOUT_ATTRIBUTE = (
    "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"
)


class RdfXmlEurLexMetadataParser:
    """Extract stable metadata from a Cellar RDF/XML notice."""

    def parse(
        self,
        document: EurLexDocument,
    ) -> EurLexMetadata:
        """Parse an RDF/XML EUR-Lex document."""
        if not isinstance(document, EurLexDocument):
            raise TypeError(
                "document must be an EurLexDocument"
            )

        media_type = document.content_type.casefold()
        if media_type not in _SUPPORTED_MEDIA_TYPES:
            raise EurLexUnsupportedMediaTypeError(
                "unsupported EUR-Lex metadata media type: "
                f"{document.content_type}"
            )

        try:
            root = ElementTree.fromstring(document.content)
        except ElementTree.ParseError as exc:
            raise EurLexMalformedMetadataError(
                "EUR-Lex metadata is not valid XML"
            ) from exc

        parsed_celex = self._parse_celex(root)
        if (
            parsed_celex is not None
            and parsed_celex != document.celex_identifier
        ):
            raise EurLexMetadataMismatchError(
                "metadata CELEX does not match requested CELEX"
            )

        titles = self._parse_titles(root)
        languages = self._parse_languages(root, titles)
        responsible_agent_uris = self._parse_resources(
            root,
            _RESPONSIBLE_AGENT_NAMES,
        )

        return EurLexMetadata(
            celex_identifier=(
                parsed_celex or document.celex_identifier
            ),
            titles=titles,
            document_date=self._parse_first_date(
                root,
                _DOCUMENT_DATE_NAMES,
            ),
            publication_date=self._parse_first_date(
                root,
                _PUBLICATION_DATE_NAMES,
            ),
            entry_into_force_date=self._parse_first_date(
                root,
                _ENTRY_INTO_FORCE_NAMES,
            ),
            end_of_validity_date=self._parse_first_date(
                root,
                _END_OF_VALIDITY_NAMES,
            ),
            languages=languages,
            resource_type_uri=self._parse_first_resource(
                root,
                _RESOURCE_TYPE_NAMES,
            ),
            status_uri=self._parse_first_resource(
                root,
                _STATUS_NAMES,
            ),
            eli_uri=self._parse_first_resource(
                root,
                _ELI_NAMES,
            ),
            cellar_uri=self._parse_cellar_uri(root),
            official_journal=self._parse_official_journal(
                root
            ),
            responsible_agent_uris=responsible_agent_uris,
            institutions=normalize_institutions(
                responsible_agent_uris
            ),
            eurovoc_concept_uris=self._parse_resources(
                root,
                _EUROVOC_NAMES,
            ),
            relationships=self._parse_relationships(
                root
            ),
            legal_lifecycle=(
                self._parse_legal_lifecycle(root)
            ),
            amendment_events=(
                self._parse_amendment_events(root)
            ),
            legal_references=(
                self._parse_legal_references(root)
            ),
            regulatory_families=detect_regulatory_families(
                parsed_celex or document.celex_identifier,
                titles,
            ),
        )

    @staticmethod
    def _parse_celex(
        root: ElementTree.Element,
    ) -> CelexIdentifier | None:
        for element in root.iter():
            if _local_name(element.tag) not in _CELEX_NAMES:
                continue
            value = _element_value(element)
            if value is None:
                continue
            try:
                return CelexIdentifier.parse(value)
            except (TypeError, ValueError) as exc:
                raise EurLexMalformedMetadataError(
                    "metadata contains an invalid CELEX value"
                ) from exc
        return None

    @staticmethod
    def _parse_titles(
        root: ElementTree.Element,
    ) -> tuple[EurLexTitle, ...]:
        titles: list[EurLexTitle] = []
        english = LanguageCode("en")

        for element in root.iter():
            predicate = _local_name(element.tag)
            if predicate not in _TITLE_NAMES:
                continue

            kind = title_kind_from_predicate(
                predicate
            )
            if kind is None:
                continue

            raw_language = element.attrib.get(
                _XML_LANGUAGE_ATTRIBUTE
            )
            language = _parse_language(raw_language)
            if language != english:
                continue

            value = _text_value(element)
            if value is None:
                continue

            title = EurLexTitle(
                language=english,
                value=value,
                kind=kind,
            )
            if title not in titles:
                titles.append(title)

        return tuple(titles)

    @staticmethod
    def _parse_languages(
        root: ElementTree.Element,
        titles: tuple[EurLexTitle, ...],
    ) -> tuple[LanguageCode, ...]:
        languages: list[LanguageCode] = [
            title.language
            for title in titles
            if title.language is not None
        ]

        for element in root.iter():
            if _local_name(element.tag) not in _LANGUAGE_NAMES:
                continue
            raw_value = _element_value(element)
            language = _parse_language_uri(raw_value)
            if language is not None:
                languages.append(language)

        return tuple(dict.fromkeys(languages))

    @staticmethod
    def _parse_relationships(
        root: ElementTree.Element,
    ) -> tuple[EurLexRelationship, ...]:
        relationships: list[EurLexRelationship] = []

        for element in root.iter():
            relationship_type = (
                relationship_type_from_predicate(
                    _local_name(element.tag)
                )
            )
            if relationship_type is None:
                continue

            raw_target = _element_value(element)
            target_celex = _parse_celex_reference(
                raw_target
            )
            if target_celex is None:
                continue

            relationship = EurLexRelationship(
                target_celex=target_celex,
                relationship_type=relationship_type,
            )
            if relationship not in relationships:
                relationships.append(relationship)

        return tuple(relationships)

    @staticmethod
    def _parse_legal_lifecycle(
        root: ElementTree.Element,
    ) -> tuple[EurLexLegalLifecycleEvent, ...]:
        events: list[EurLexLegalLifecycleEvent] = []

        for element in root.iter():
            predicate = _local_name(element.tag)
            kind = _LIFECYCLE_PREDICATES.get(
                predicate
            )
            if kind is None:
                continue

            value = _text_value(element)
            if value is None:
                continue

            try:
                occurred_on = date.fromisoformat(
                    value[:10]
                )
            except ValueError as exc:
                raise EurLexMalformedMetadataError(
                    "metadata contains an invalid "
                    "lifecycle date"
                ) from exc

            events.append(
                EurLexLegalLifecycleEvent(
                    kind=kind,
                    occurred_on=occurred_on,
                    source_predicate=predicate,
                )
            )

        return normalize_lifecycle_events(
            tuple(events)
        )

    @staticmethod
    def _parse_amendment_events(
        root: ElementTree.Element,
    ) -> tuple[EurLexAmendmentEvent, ...]:
        events: list[EurLexAmendmentEvent] = []

        for element in root.iter():
            predicate = _local_name(element.tag)
            if predicate not in _AMENDMENT_EVENT_NAMES:
                continue

            amending = _first_nested_celex(
                element,
                _AMENDING_CELEX_NAMES,
            )
            amended = _first_nested_celex(
                element,
                _AMENDED_CELEX_NAMES,
            )
            effective_on = _first_nested_date(
                element,
                _AMENDMENT_EFFECTIVE_DATE_NAMES,
            )

            if (
                amending is None
                or amended is None
                or effective_on is None
            ):
                continue

            events.append(
                EurLexAmendmentEvent(
                    amending_celex=amending,
                    amended_celex=amended,
                    effective_on=effective_on,
                    source_predicate=predicate,
                )
            )

        return normalize_amendment_events(
            tuple(events)
        )

    @staticmethod
    def _parse_legal_references(
        root: ElementTree.Element,
    ) -> tuple[EurLexLegalReference, ...]:
        references: list[EurLexLegalReference] = []

        for element in root.iter():
            predicate = _local_name(element.tag)
            kind = legal_reference_kind_from_predicate(
                predicate
            )
            if kind is None:
                continue

            raw_target = _element_value(element)
            target_celex = _parse_celex_reference(
                raw_target
            )
            target_uri = (
                raw_target
                if (
                    raw_target is not None
                    and target_celex is None
                )
                else None
            )
            article = _first_nested_text(
                element,
                _LEGAL_REFERENCE_ARTICLE_NAMES,
            )

            if (
                target_celex is None
                and target_uri is None
            ):
                continue

            references.append(
                EurLexLegalReference(
                    kind=kind,
                    target_celex=target_celex,
                    target_uri=target_uri,
                    article=article,
                    source_predicate=predicate,
                )
            )

        return normalize_legal_references(
            tuple(references)
        )

    @staticmethod
    def _parse_first_date(
        root: ElementTree.Element,
        names: frozenset[str],
    ) -> date | None:
        for element in root.iter():
            if _local_name(element.tag) not in names:
                continue
            value = _text_value(element)
            if value is None:
                continue
            try:
                return date.fromisoformat(value[:10])
            except ValueError as exc:
                raise EurLexMalformedMetadataError(
                    "metadata contains an invalid date"
                ) from exc
        return None

    @staticmethod
    def _parse_cellar_uri(
        root: ElementTree.Element,
    ) -> str | None:
        for element in root.iter():
            value = element.attrib.get(
                _RDF_ABOUT_ATTRIBUTE
            )
            if (
                value is not None
                and "/cellar/" in value.casefold()
            ):
                return value.strip() or None

        return None

    @staticmethod
    def _parse_official_journal(
        root: ElementTree.Element,
    ) -> EurLexOfficialJournalReference | None:
        uri = (
            RdfXmlEurLexMetadataParser
            ._parse_first_resource(
                root,
                _OFFICIAL_JOURNAL_NAMES,
            )
        )
        number = (
            RdfXmlEurLexMetadataParser
            ._parse_first_text(
                root,
                _OFFICIAL_JOURNAL_NUMBER_NAMES,
            )
        )
        page_first = (
            RdfXmlEurLexMetadataParser
            ._parse_first_text(
                root,
                _OFFICIAL_JOURNAL_PAGE_FIRST_NAMES,
            )
        )
        page_last = (
            RdfXmlEurLexMetadataParser
            ._parse_first_text(
                root,
                _OFFICIAL_JOURNAL_PAGE_LAST_NAMES,
            )
        )

        if all(
            value is None
            for value in (
                uri,
                number,
                page_first,
                page_last,
            )
        ):
            return None

        return EurLexOfficialJournalReference(
            uri=uri,
            number=number,
            page_first=page_first,
            page_last=page_last,
        )

    @staticmethod
    def _parse_first_text(
        root: ElementTree.Element,
        names: frozenset[str],
    ) -> str | None:
        for element in root.iter():
            if _local_name(element.tag) not in names:
                continue

            value = _text_value(element)
            if value is not None:
                return value

        return None

    @staticmethod
    def _parse_first_resource(
        root: ElementTree.Element,
        names: frozenset[str],
    ) -> str | None:
        resources = (
            RdfXmlEurLexMetadataParser._parse_resources(
                root,
                names,
            )
        )
        return resources[0] if resources else None

    @staticmethod
    def _parse_resources(
        root: ElementTree.Element,
        names: frozenset[str],
    ) -> tuple[str, ...]:
        values: list[str] = []

        for element in root.iter():
            if _local_name(element.tag) not in names:
                continue
            value = _element_value(element)
            if value is not None and value not in values:
                values.append(value)

        return tuple(values)


def _local_name(tag: str) -> str:
    return tag.rsplit("}", maxsplit=1)[-1]


def _text_value(
    element: ElementTree.Element,
) -> str | None:
    if element.text is None:
        return None
    normalized = " ".join(element.text.split())
    return normalized or None


def _element_value(
    element: ElementTree.Element,
) -> str | None:
    resource = element.attrib.get(_RDF_RESOURCE_ATTRIBUTE)
    if resource is not None:
        normalized_resource = resource.strip()
        return normalized_resource or None
    return _text_value(element)


def _parse_celex_reference(
    raw_value: str | None,
) -> CelexIdentifier | None:
    if raw_value is None:
        return None

    normalized = raw_value.strip()
    if not normalized:
        return None

    candidate = normalized.rstrip("/").rsplit(
        "/",
        maxsplit=1,
    )[-1]
    if "CELEX:" in candidate.upper():
        candidate = candidate.split(":", maxsplit=1)[-1]

    try:
        return CelexIdentifier.parse(candidate)
    except (TypeError, ValueError):
        return None



def _first_nested_celex(
    root: ElementTree.Element,
    names: frozenset[str],
) -> CelexIdentifier | None:
    for element in root.iter():
        if _local_name(element.tag) not in names:
            continue
        parsed = _parse_celex_reference(
            _element_value(element)
        )
        if parsed is not None:
            return parsed

    return None


def _first_nested_date(
    root: ElementTree.Element,
    names: frozenset[str],
) -> date | None:
    for element in root.iter():
        if _local_name(element.tag) not in names:
            continue

        value = _text_value(element)
        if value is None:
            continue

        try:
            return date.fromisoformat(value[:10])
        except ValueError as exc:
            raise EurLexMalformedMetadataError(
                "metadata contains an invalid amendment date"
            ) from exc

    return None

def _first_nested_text(
    root: ElementTree.Element,
    names: frozenset[str],
) -> str | None:
    for element in root.iter():
        if _local_name(element.tag) not in names:
            continue
        value = _text_value(element)
        if value is not None:
            return value

    return None

def _parse_language(
    raw_value: str | None,
) -> LanguageCode | None:
    if raw_value is None:
        return None

    candidate = (
        raw_value.strip()
        .split("-", maxsplit=1)[0]
        .casefold()
    )
    three_letter_codes = {
        "bul": "bg",
        "ces": "cs",
        "dan": "da",
        "deu": "de",
        "ell": "el",
        "eng": "en",
        "est": "et",
        "fin": "fi",
        "fra": "fr",
        "gle": "ga",
        "hrv": "hr",
        "hun": "hu",
        "ita": "it",
        "lit": "lt",
        "lav": "lv",
        "mlt": "mt",
        "nld": "nl",
        "pol": "pl",
        "por": "pt",
        "ron": "ro",
        "slk": "sk",
        "slv": "sl",
        "spa": "es",
        "swe": "sv",
    }
    candidate = three_letter_codes.get(
        candidate,
        candidate,
    )

    if len(candidate) != 2:
        return None

    try:
        return LanguageCode(candidate)
    except (TypeError, ValueError):
        return None


def _parse_language_uri(
    raw_value: str | None,
) -> LanguageCode | None:
    if raw_value is None:
        return None

    token = raw_value.rstrip("/").rsplit("/", maxsplit=1)[-1]
    return _parse_language(token)


eurlex_metadata_parser_contract: type[EurLexMetadataParser]
eurlex_metadata_parser_contract = RdfXmlEurLexMetadataParser
