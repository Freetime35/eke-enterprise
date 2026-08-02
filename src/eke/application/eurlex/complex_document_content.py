"""Transport-neutral complex EUR-Lex document content."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


def _normalize_optional_text(
    value: str | None,
    *,
    name: str,
) -> str | None:
    if value is None:
        return None

    if not isinstance(value, str):
        raise TypeError(
            f"{name} must be a string or None"
        )

    normalized = " ".join(value.split())
    return normalized or None


def _normalize_required_text(
    value: str,
    *,
    name: str,
) -> str:
    if not isinstance(value, str):
        raise TypeError(
            f"{name} must be a string"
        )

    normalized = " ".join(value.split())
    if not normalized:
        raise ValueError(
            f"{name} must not be empty"
        )

    return normalized


@dataclass(frozen=True, slots=True)
class EurLexTableCell:
    """Represent one source-backed table cell."""

    row: int
    column: int
    text: str | None = None
    row_span: int = 1
    column_span: int = 1
    is_header: bool = False

    def __post_init__(self) -> None:
        for name, value in (
            ("row", self.row),
            ("column", self.column),
            ("row_span", self.row_span),
            ("column_span", self.column_span),
        ):
            if not isinstance(value, int):
                raise TypeError(
                    f"{name} must be an integer"
                )

            if isinstance(value, bool):
                raise TypeError(
                    f"{name} must be an integer"
                )

        if self.row < 0 or self.column < 0:
            raise ValueError(
                "row and column must be zero or positive"
            )

        if self.row_span <= 0:
            raise ValueError(
                "row_span must be strictly positive"
            )

        if self.column_span <= 0:
            raise ValueError(
                "column_span must be strictly positive"
            )

        if not isinstance(self.is_header, bool):
            raise TypeError(
                "is_header must be a boolean"
            )

        object.__setattr__(
            self,
            "text",
            _normalize_optional_text(
                self.text,
                name="text",
            ),
        )


@dataclass(frozen=True, slots=True)
class EurLexTable:
    """Represent one structured table."""

    content_id: str
    parent_node_id: str
    position: int
    source_element: str
    cells: tuple[EurLexTableCell, ...] = ()
    caption: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "content_id",
            _normalize_required_text(
                self.content_id,
                name="content_id",
            ),
        )

        object.__setattr__(
            self,
            "parent_node_id",
            _normalize_required_text(
                self.parent_node_id,
                name="parent_node_id",
            ),
        )

        object.__setattr__(
            self,
            "source_element",
            _normalize_required_text(
                self.source_element,
                name="source_element",
            ),
        )

        object.__setattr__(
            self,
            "caption",
            _normalize_optional_text(
                self.caption,
                name="caption",
            ),
        )

        if not isinstance(self.position, int):
            raise TypeError(
                "position must be an integer"
            )

        if isinstance(self.position, bool):
            raise TypeError(
                "position must be an integer"
            )

        if self.position < 0:
            raise ValueError(
                "position must be zero or positive"
            )

        if not isinstance(self.cells, tuple):
            raise TypeError(
                "cells must be a tuple"
            )

        if any(
            not isinstance(
                cell,
                EurLexTableCell,
            )
            for cell in self.cells
        ):
            raise TypeError(
                "cells must contain "
                "EurLexTableCell values"
            )


@dataclass(frozen=True, slots=True)
class EurLexFormula:
    """Represent one formula without interpreting it."""

    content_id: str
    parent_node_id: str
    position: int
    source_element: str
    source_text: str | None = None
    mathml: str | None = None
    image_uri: str | None = None

    def __post_init__(self) -> None:
        for name in (
            "content_id",
            "parent_node_id",
            "source_element",
        ):
            object.__setattr__(
                self,
                name,
                _normalize_required_text(
                    getattr(self, name),
                    name=name,
                ),
            )

        if not isinstance(self.position, int):
            raise TypeError(
                "position must be an integer"
            )

        if isinstance(self.position, bool):
            raise TypeError(
                "position must be an integer"
            )

        if self.position < 0:
            raise ValueError(
                "position must be zero or positive"
            )

        for name in (
            "source_text",
            "image_uri",
        ):
            object.__setattr__(
                self,
                name,
                _normalize_optional_text(
                    getattr(self, name),
                    name=name,
                ),
            )

        if (
            self.mathml is not None
            and not isinstance(self.mathml, str)
        ):
            raise TypeError(
                "mathml must be a string or None"
            )

        if not any(
            (
                self.source_text,
                self.mathml,
                self.image_uri,
            )
        ):
            raise ValueError(
                "formula must preserve source_text, "
                "mathml, or image_uri"
            )


@dataclass(frozen=True, slots=True)
class EurLexFootnote:
    """Represent one footnote and its references."""

    content_id: str
    parent_node_id: str
    text: str
    position: int
    source_element: str
    marker: str | None = None
    referenced_from: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in (
            "content_id",
            "parent_node_id",
            "text",
            "source_element",
        ):
            object.__setattr__(
                self,
                name,
                _normalize_required_text(
                    getattr(self, name),
                    name=name,
                ),
            )

        object.__setattr__(
            self,
            "marker",
            _normalize_optional_text(
                self.marker,
                name="marker",
            ),
        )

        if not isinstance(self.position, int):
            raise TypeError(
                "position must be an integer"
            )

        if isinstance(self.position, bool):
            raise TypeError(
                "position must be an integer"
            )

        if self.position < 0:
            raise ValueError(
                "position must be zero or positive"
            )

        if any(
            not isinstance(
                node_id,
                str,
            )
            or not node_id.strip()
            for node_id in self.referenced_from
        ):
            raise TypeError(
                "referenced_from must contain "
                "non-empty strings"
            )

        object.__setattr__(
            self,
            "referenced_from",
            tuple(
                dict.fromkeys(
                    node_id.strip()
                    for node_id
                    in self.referenced_from
                )
            ),
        )


class EurLexVisualKind(StrEnum):
    """Canonical kinds of visual elements."""

    IMAGE = "IMAGE"
    DIAGRAM = "DIAGRAM"
    CHART = "CHART"
    MAP = "MAP"
    LOGO = "LOGO"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class EurLexVisualElement:
    """Represent one visual resource without OCR."""

    content_id: str
    parent_node_id: str
    kind: EurLexVisualKind
    position: int
    source_element: str
    caption: str | None = None
    alternative_text: str | None = None
    source_uri: str | None = None
    media_type: str | None = None

    def __post_init__(self) -> None:
        for name in (
            "content_id",
            "parent_node_id",
            "source_element",
        ):
            object.__setattr__(
                self,
                name,
                _normalize_required_text(
                    getattr(self, name),
                    name=name,
                ),
            )

        if not isinstance(
            self.kind,
            EurLexVisualKind,
        ):
            raise TypeError(
                "kind must be an EurLexVisualKind"
            )

        if not isinstance(self.position, int):
            raise TypeError(
                "position must be an integer"
            )

        if isinstance(self.position, bool):
            raise TypeError(
                "position must be an integer"
            )

        if self.position < 0:
            raise ValueError(
                "position must be zero or positive"
            )

        for name in (
            "caption",
            "alternative_text",
            "source_uri",
            "media_type",
        ):
            object.__setattr__(
                self,
                name,
                _normalize_optional_text(
                    getattr(self, name),
                    name=name,
                ),
            )


EurLexComplexContentItem = (
    EurLexTable
    | EurLexFormula
    | EurLexFootnote
    | EurLexVisualElement
)


@dataclass(frozen=True, slots=True)
class EurLexComplexDocumentContent:
    """Aggregate complex content extracted from one document."""

    tables: tuple[EurLexTable, ...] = ()
    formulas: tuple[EurLexFormula, ...] = ()
    footnotes: tuple[EurLexFootnote, ...] = ()
    visuals: tuple[EurLexVisualElement, ...] = ()

    def __post_init__(self) -> None:
        for name, expected_type in (
            ("tables", EurLexTable),
            ("formulas", EurLexFormula),
            ("footnotes", EurLexFootnote),
            ("visuals", EurLexVisualElement),
        ):
            values = getattr(self, name)

            if not isinstance(values, tuple):
                raise TypeError(
                    f"{name} must be a tuple"
                )

            if any(
                not isinstance(
                    value,
                    expected_type,
                )
                for value in values
            ):
                raise TypeError(
                    f"{name} contains invalid values"
                )

        content_ids = tuple(
            content.content_id
            for content in self._all_content_items()
        )

        if len(content_ids) != len(
            set(content_ids)
        ):
            raise ValueError(
                "content identifiers must be unique"
            )

    def _all_content_items(
        self,
    ) -> tuple[EurLexComplexContentItem, ...]:
        """Return all complex content in category order."""
        items: list[EurLexComplexContentItem] = []

        items.extend(self.tables)
        items.extend(self.formulas)
        items.extend(self.footnotes)
        items.extend(self.visuals)

        return tuple(items)

    def content_by_id(
        self,
        content_id: str,
    ) -> EurLexComplexContentItem | None:
        """Return one complex content item by identifier."""
        if not isinstance(content_id, str):
            raise TypeError(
                "content_id must be a string"
            )

        return next(
            (
                content
                for content
                in self._all_content_items()
                if content.content_id == content_id
            ),
            None,
        )