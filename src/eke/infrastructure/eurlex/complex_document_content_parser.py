"""Parse complex content from structured EUR-Lex XML or XHTML."""

from __future__ import annotations

from xml.etree import ElementTree

from eke.application.eurlex.complex_document_content import (
    EurLexComplexDocumentContent,
    EurLexFootnote,
    EurLexFormula,
    EurLexTable,
    EurLexTableCell,
    EurLexVisualElement,
    EurLexVisualKind,
)


class EurLexComplexDocumentContentParseError(
    ValueError
):
    """Raised when complex document content is malformed."""


_TABLE_NAMES = frozenset(
    {"TABLE"}
)
_ROW_NAMES = frozenset(
    {"TR", "ROW"}
)
_HEADER_CELL_NAMES = frozenset(
    {"TH", "HEADERCELL"}
)
_CELL_NAMES = frozenset(
    {"TD", "CELL", "TH", "HEADERCELL"}
)
_FORMULA_NAMES = frozenset(
    {"FORMULA", "MATH", "MATHML"}
)
_FOOTNOTE_NAMES = frozenset(
    {"FOOTNOTE", "NOTE"}
)
_VISUAL_NAMES = frozenset(
    {"IMAGE", "FIGURE", "GRAPHIC"}
)
_CAPTION_NAMES = frozenset(
    {"CAPTION", "TITLE", "HEADING"}
)
_MARKER_NAMES = frozenset(
    {"MARKER", "NUMBER", "LABEL"}
)


class XmlEurLexComplexContentParser:
    """Parse tables, formulas, notes and visuals."""

    def parse(
        self,
        content: bytes,
    ) -> EurLexComplexDocumentContent:
        """Parse complex content from one XML/XHTML document."""
        if not isinstance(content, bytes):
            raise TypeError(
                "content must be bytes"
            )
        if not content.strip():
            raise (
                EurLexComplexDocumentContentParseError(
                    "content must not be empty"
                )
            )

        try:
            root = ElementTree.fromstring(content)
        except ElementTree.ParseError as exc:
            raise (
                EurLexComplexDocumentContentParseError(
                    "content must be valid XML or XHTML"
                )
            ) from exc

        tables: list[EurLexTable] = []
        formulas: list[EurLexFormula] = []
        footnotes: list[EurLexFootnote] = []
        visuals: list[EurLexVisualElement] = []

        position = 0
        self._walk(
            root,
            parent_node_id=None,
            tables=tables,
            formulas=formulas,
            footnotes=footnotes,
            visuals=visuals,
            position_counter=[position],
        )

        return EurLexComplexDocumentContent(
            tables=tuple(tables),
            formulas=tuple(formulas),
            footnotes=tuple(footnotes),
            visuals=tuple(visuals),
        )

    def _walk(
        self,
        element: ElementTree.Element,
        *,
        parent_node_id: str | None,
        tables: list[EurLexTable],
        formulas: list[EurLexFormula],
        footnotes: list[EurLexFootnote],
        visuals: list[EurLexVisualElement],
        position_counter: list[int],
    ) -> None:
        local_name = _local_name(element.tag)
        current_parent = parent_node_id

        element_id = _element_identifier(
            element
        )
        if (
            element_id is not None
            and local_name not in (
                _TABLE_NAMES
                | _FORMULA_NAMES
                | _FOOTNOTE_NAMES
                | _VISUAL_NAMES
            )
        ):
            current_parent = element_id

        if local_name in _TABLE_NAMES:
            if parent_node_id is not None:
                tables.append(
                    _parse_table(
                        element,
                        parent_node_id=(
                            parent_node_id
                        ),
                        position=position_counter[
                            0
                        ],
                    )
                )
                position_counter[0] += 1
            return

        if local_name in _FORMULA_NAMES:
            if parent_node_id is not None:
                formulas.append(
                    _parse_formula(
                        element,
                        parent_node_id=(
                            parent_node_id
                        ),
                        position=position_counter[
                            0
                        ],
                    )
                )
                position_counter[0] += 1
            return

        if local_name in _FOOTNOTE_NAMES:
            if parent_node_id is not None:
                footnotes.append(
                    _parse_footnote(
                        element,
                        parent_node_id=(
                            parent_node_id
                        ),
                        position=position_counter[
                            0
                        ],
                    )
                )
                position_counter[0] += 1
            return

        if local_name in _VISUAL_NAMES:
            if parent_node_id is not None:
                visuals.append(
                    _parse_visual(
                        element,
                        parent_node_id=(
                            parent_node_id
                        ),
                        position=position_counter[
                            0
                        ],
                    )
                )
                position_counter[0] += 1
            return

        for child in element:
            self._walk(
                child,
                parent_node_id=current_parent,
                tables=tables,
                formulas=formulas,
                footnotes=footnotes,
                visuals=visuals,
                position_counter=(
                    position_counter
                ),
            )


def _parse_table(
    element: ElementTree.Element,
    *,
    parent_node_id: str,
    position: int,
) -> EurLexTable:
    cells: list[EurLexTableCell] = []

    row_index = 0
    for row in element.iter():
        if _local_name(row.tag) not in _ROW_NAMES:
            continue

        column_index = 0
        for cell in row:
            local_name = _local_name(
                cell.tag
            )
            if local_name not in _CELL_NAMES:
                continue

            row_span = _positive_int_attribute(
                cell,
                ("rowspan", "ROWSPAN"),
                default=1,
            )
            column_span = _positive_int_attribute(
                cell,
                ("colspan", "COLSPAN"),
                default=1,
            )

            cells.append(
                EurLexTableCell(
                    row=row_index,
                    column=column_index,
                    text=_all_text(cell),
                    row_span=row_span,
                    column_span=column_span,
                    is_header=(
                        local_name
                        in _HEADER_CELL_NAMES
                    ),
                )
            )
            column_index += column_span

        row_index += 1

    return EurLexTable(
        content_id=_required_content_id(
            element,
            prefix="table",
            position=position,
        ),
        parent_node_id=parent_node_id,
        position=position,
        source_element=_local_name(
            element.tag
        ),
        caption=_first_child_text(
            element,
            _CAPTION_NAMES,
        ),
        cells=tuple(cells),
    )


def _parse_formula(
    element: ElementTree.Element,
    *,
    parent_node_id: str,
    position: int,
) -> EurLexFormula:
    local_name = _local_name(element.tag)
    mathml = None
    if local_name in {"MATH", "MATHML"}:
        mathml = ElementTree.tostring(
            element,
            encoding="unicode",
        )
    else:
        for child in element.iter():
            if _local_name(child.tag) in {
                "MATH",
                "MATHML",
            }:
                mathml = ElementTree.tostring(
                    child,
                    encoding="unicode",
                )
                break

    return EurLexFormula(
        content_id=_required_content_id(
            element,
            prefix="formula",
            position=position,
        ),
        parent_node_id=parent_node_id,
        position=position,
        source_element=local_name,
        source_text=_all_text(element),
        mathml=mathml,
        image_uri=_first_attribute(
            element,
            (
                "src",
                "SRC",
                "href",
                "HREF",
                "{http://www.w3.org/1999/xlink}href",
            ),
        ),
    )


def _parse_footnote(
    element: ElementTree.Element,
    *,
    parent_node_id: str,
    position: int,
) -> EurLexFootnote:
    return EurLexFootnote(
        content_id=_required_content_id(
            element,
            prefix="footnote",
            position=position,
        ),
        parent_node_id=parent_node_id,
        text=_all_text(element) or "",
        position=position,
        source_element=_local_name(
            element.tag
        ),
        marker=_first_child_text(
            element,
            _MARKER_NAMES,
        ),
        referenced_from=(
            parent_node_id,
        ),
    )


def _parse_visual(
    element: ElementTree.Element,
    *,
    parent_node_id: str,
    position: int,
) -> EurLexVisualElement:
    return EurLexVisualElement(
        content_id=_required_content_id(
            element,
            prefix="visual",
            position=position,
        ),
        parent_node_id=parent_node_id,
        kind=_visual_kind(element),
        position=position,
        source_element=_local_name(
            element.tag
        ),
        caption=_first_child_text(
            element,
            _CAPTION_NAMES,
        ),
        alternative_text=_first_attribute(
            element,
            ("alt", "ALT"),
        ),
        source_uri=_first_attribute(
            element,
            (
                "src",
                "SRC",
                "href",
                "HREF",
                "{http://www.w3.org/1999/xlink}href",
            ),
        ),
        media_type=_first_attribute(
            element,
            (
                "type",
                "TYPE",
                "media-type",
                "MEDIA-TYPE",
            ),
        ),
    )


def _visual_kind(
    element: ElementTree.Element,
) -> EurLexVisualKind:
    explicit = _first_attribute(
        element,
        ("kind", "KIND", "role", "ROLE"),
    )
    if explicit is not None:
        normalized = explicit.strip().upper()
        try:
            return EurLexVisualKind(
                normalized
            )
        except ValueError:
            pass

    local_name = _local_name(element.tag)
    if local_name == "IMAGE":
        return EurLexVisualKind.IMAGE
    if local_name in {
        "FIGURE",
        "GRAPHIC",
    }:
        return EurLexVisualKind.UNKNOWN

    return EurLexVisualKind.UNKNOWN


def _local_name(tag: str) -> str:
    return tag.rsplit(
        "}",
        maxsplit=1,
    )[-1].upper()


def _element_identifier(
    element: ElementTree.Element,
) -> str | None:
    return _first_attribute(
        element,
        (
            "id",
            "ID",
            "{http://www.w3.org/XML/1998/namespace}id",
        ),
    )


def _required_content_id(
    element: ElementTree.Element,
    *,
    prefix: str,
    position: int,
) -> str:
    return (
        _element_identifier(element)
        or f"{prefix}-{position + 1}"
    )


def _first_attribute(
    element: ElementTree.Element,
    names: tuple[str, ...],
) -> str | None:
    for name in names:
        value = element.attrib.get(name)
        if value is not None and value.strip():
            return value.strip()

    return None


def _positive_int_attribute(
    element: ElementTree.Element,
    names: tuple[str, ...],
    *,
    default: int,
) -> int:
    raw = _first_attribute(
        element,
        names,
    )
    if raw is None:
        return default

    try:
        value = int(raw)
    except ValueError as exc:
        raise (
            EurLexComplexDocumentContentParseError(
                "span attributes must be integers"
            )
        ) from exc

    if value <= 0:
        raise (
            EurLexComplexDocumentContentParseError(
                "span attributes must be positive"
            )
        )

    return value


def _first_child_text(
    element: ElementTree.Element,
    names: frozenset[str],
) -> str | None:
    for child in element:
        if _local_name(child.tag) not in names:
            continue
        value = _all_text(child)
        if value is not None:
            return value

    return None


def _all_text(
    element: ElementTree.Element,
) -> str | None:
    normalized = " ".join(
        " ".join(
            element.itertext()
        ).split()
    )
    return normalized or None
