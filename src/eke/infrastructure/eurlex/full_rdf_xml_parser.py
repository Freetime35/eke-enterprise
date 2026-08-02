"""Enriched RDF/XML parser for the full EUR-Lex import pipeline."""

from __future__ import annotations

from dataclasses import replace
from xml.etree import ElementTree

from eke.application.eurlex import (
    EurLexClassification,
    EurLexDocument,
    EurLexMetadata,
)
from eke.application.eurlex.financial_classification import (
    classify_financial_label,
)
from eke.domain.localization import LanguageCode
from eke.infrastructure.eurlex.rdf_xml_parser import (
    RdfXmlEurLexMetadataParser as BaseParser,
)

_RDF_ABOUT = (
    "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"
)
_RDF_RESOURCE = (
    "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"
)
_XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"

_LABEL_NAMES = frozenset(
    {
        "prefLabel",
        "label",
        "concept_label",
    }
)
_BROADER_NAMES = frozenset({"broader"})
_NARROWER_NAMES = frozenset({"narrower"})
_SCHEME_NAMES = frozenset(
    {
        "inScheme",
        "topConceptOf",
    }
)
_SUBJECT_NAMES = frozenset(
    {
        "work_is_about_concept_eurovoc",
        "subject",
    }
)


class FullRdfXmlEurLexMetadataParser(BaseParser):
    """Parse base metadata plus English financial classifications."""

    def parse(
        self,
        document: EurLexDocument,
    ) -> EurLexMetadata:
        metadata = super().parse(document)
        root = ElementTree.fromstring(document.content)

        return replace(
            metadata,
            classifications=_parse_classifications(root),
        )


def _parse_classifications(
    root: ElementTree.Element,
) -> tuple[EurLexClassification, ...]:
    descriptions = _description_index(root)
    concept_uris = _subject_concept_uris(root)
    results: list[EurLexClassification] = []
    seen: set[tuple[str, str]] = set()

    for uri in concept_uris:
        description = descriptions.get(uri)
        if description is None:
            continue

        label = _english_label(description)
        if label is None:
            continue

        category = classify_financial_label(label)
        if category is None:
            continue

        language = LanguageCode("en")
        identity = (uri, language.value)
        if identity in seen:
            continue
        seen.add(identity)

        results.append(
            EurLexClassification(
                uri=uri,
                code=uri.rstrip("/").rsplit(
                    "/",
                    maxsplit=1,
                )[-1],
                language=language,
                label=label,
                scheme_uri=_first_resource(
                    description,
                    _SCHEME_NAMES,
                ),
                broader_uris=_resources(
                    description,
                    _BROADER_NAMES,
                ),
                narrower_uris=_resources(
                    description,
                    _NARROWER_NAMES,
                ),
                financial_category=category,
            )
        )

    return tuple(results)


def _description_index(
    root: ElementTree.Element,
) -> dict[str, ElementTree.Element]:
    result: dict[str, ElementTree.Element] = {}

    for element in root.iter():
        uri = element.attrib.get(_RDF_ABOUT)
        if uri:
            result[uri.strip()] = element

    return result


def _subject_concept_uris(
    root: ElementTree.Element,
) -> tuple[str, ...]:
    results: list[str] = []

    for element in root.iter():
        if _local_name(element.tag) not in _SUBJECT_NAMES:
            continue

        uri = element.attrib.get(_RDF_RESOURCE)
        if (
            uri is not None
            and "eurovoc" in uri.casefold()
            and uri not in results
        ):
            results.append(uri)

    return tuple(results)


def _english_label(
    description: ElementTree.Element,
) -> str | None:
    for element in description.iter():
        if _local_name(element.tag) not in _LABEL_NAMES:
            continue

        raw_language = element.attrib.get(_XML_LANG)
        if raw_language is None:
            continue

        language = raw_language.split(
            "-",
            maxsplit=1,
        )[0].casefold()
        if language not in {"en", "eng"}:
            continue

        value = _text(element)
        if value is not None:
            return value

    return None


def _first_resource(
    description: ElementTree.Element,
    names: frozenset[str],
) -> str | None:
    values = _resources(description, names)
    return values[0] if values else None


def _resources(
    description: ElementTree.Element,
    names: frozenset[str],
) -> tuple[str, ...]:
    results: list[str] = []

    for element in description.iter():
        if _local_name(element.tag) not in names:
            continue

        uri = element.attrib.get(_RDF_RESOURCE)
        if uri is not None:
            normalized = uri.strip()
            if normalized and normalized not in results:
                results.append(normalized)

    return tuple(results)


def _local_name(tag: str) -> str:
    return tag.rsplit("}", maxsplit=1)[-1]


def _text(element: ElementTree.Element) -> str | None:
    if element.text is None:
        return None

    value = " ".join(element.text.split())
    return value or None
