"""Enriched RDF/XML parser for the full EUR-Lex import pipeline."""

from __future__ import annotations

from dataclasses import replace
from xml.etree import ElementTree

from eke.application.eurlex import (
    EurLexClassification,
    EurLexDocument,
    EurLexMetadata,
    EurLexRelationship,
)
from eke.domain.identity import CelexIdentifier
from eke.domain.localization import LanguageCode
from eke.domain.relationships import RelationshipType
from eke.infrastructure.eurlex.rdf_xml_parser import (
    RdfXmlEurLexMetadataParser as BaseParser,
)

_RDF_RESOURCE = (
    "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource"
)
_XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"

_RELATIONSHIP_NAMES = {
    "work_amends_work": RelationshipType.AMENDS,
    "work_repeals_work": RelationshipType.REPEALS,
    "work_cites_work": RelationshipType.CITES,
    "work_implements_work": RelationshipType.IMPLEMENTS,
    "work_has_legal_basis_work": RelationshipType.LEGAL_BASIS,
    "work_corrects_work": RelationshipType.CORRECTS,
    "work_related_to_work": RelationshipType.RELATED_TO,
}


class FullRdfXmlEurLexMetadataParser(BaseParser):
    """Parse base metadata plus labeled EuroVoc and CELEX relations."""

    def parse(
        self,
        document: EurLexDocument,
    ) -> EurLexMetadata:
        metadata = super().parse(document)
        root = ElementTree.fromstring(document.content)
        return replace(
            metadata,
            classifications=_parse_classifications(root),
            relationships=_parse_relationships(root),
        )


def _parse_classifications(
    root: ElementTree.Element,
) -> tuple[EurLexClassification, ...]:
    labels: dict[str, list[tuple[LanguageCode, str]]] = {}

    for element in root.iter():
        local = _local_name(element.tag)
        if local not in {
            "prefLabel",
            "label",
            "concept_label",
        }:
            continue
        subject = _nearest_subject_uri(root, element)
        raw_language = element.attrib.get(_XML_LANG)
        language = _language(raw_language)
        value = _text(element)
        if (
            subject is not None
            and language is not None
            and value is not None
        ):
            labels.setdefault(subject, []).append(
                (language, value)
            )

    concept_uris: list[str] = []
    for element in root.iter():
        if _local_name(element.tag) not in {
            "work_is_about_concept_eurovoc",
            "subject",
        }:
            continue
        uri = element.attrib.get(_RDF_RESOURCE)
        if (
            uri
            and "eurovoc" in uri.casefold()
            and uri not in concept_uris
        ):
            concept_uris.append(uri)

    results: list[EurLexClassification] = []
    for uri in concept_uris:
        code = uri.rstrip("/").rsplit("/", maxsplit=1)[-1]
        for language, label in labels.get(uri, []):
            results.append(
                EurLexClassification(
                    uri=uri,
                    code=code,
                    language=language,
                    label=label,
                )
            )
    return tuple(results)


def _parse_relationships(
    root: ElementTree.Element,
) -> tuple[EurLexRelationship, ...]:
    relationships: list[EurLexRelationship] = []

    for element in root.iter():
        relationship_type = _RELATIONSHIP_NAMES.get(
            _local_name(element.tag)
        )
        if relationship_type is None:
            continue
        raw_target = element.attrib.get(_RDF_RESOURCE)
        if raw_target is None:
            continue
        celex_value = raw_target.rstrip("/").rsplit("/", maxsplit=1)[-1]
        try:
            target = CelexIdentifier.parse(celex_value)
        except (TypeError, ValueError):
            continue
        relationship = EurLexRelationship(
            target_celex=target,
            relationship_type=relationship_type,
        )
        if relationship not in relationships:
            relationships.append(relationship)

    return tuple(relationships)


def _nearest_subject_uri(
    root: ElementTree.Element,
    target: ElementTree.Element,
) -> str | None:
    for description in root.iter():
        if target not in tuple(description.iter()):
            continue
        uri = description.attrib.get(
            "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about"
        )
        if uri:
            return uri
    return None


def _local_name(tag: str) -> str:
    return tag.rsplit("}", maxsplit=1)[-1]


def _text(element: ElementTree.Element) -> str | None:
    if element.text is None:
        return None
    value = " ".join(element.text.split())
    return value or None


def _language(value: str | None) -> LanguageCode | None:
    if value is None:
        return None
    token = value.split("-", maxsplit=1)[0]
    if len(token) != 2:
        return None
    try:
        return LanguageCode(token)
    except (TypeError, ValueError):
        return None
