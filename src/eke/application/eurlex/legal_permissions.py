"""Explicit English legal permissions extracted from EUR-Lex content."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from eke.domain.localization import LanguageCode


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


class EurLexLegalPermissionKind(StrEnum):
    """Canonical explicit permission markers."""

    MAY = "MAY"
    ENTITLED_TO = "ENTITLED_TO"
    AUTHORISED_TO = "AUTHORISED_TO"
    ALLOWED_TO = "ALLOWED_TO"


@dataclass(frozen=True, slots=True)
class EurLexLegalPermission:
    """Represent one explicit source-backed permission."""

    subject: str
    action: str
    kind: EurLexLegalPermissionKind
    source_node_id: str
    source_text: str
    language: LanguageCode
    article_node_id: str | None = None
    paragraph_node_id: str | None = None

    def __post_init__(self) -> None:
        for name in (
            "subject",
            "action",
            "source_node_id",
            "source_text",
        ):
            object.__setattr__(
                self,
                name,
                _normalize_required_text(
                    getattr(self, name),
                    name=name,
                ),
            )

        for name in (
            "article_node_id",
            "paragraph_node_id",
        ):
            object.__setattr__(
                self,
                name,
                _normalize_optional_text(
                    getattr(self, name),
                    name=name,
                ),
            )

        if not isinstance(
            self.kind,
            EurLexLegalPermissionKind,
        ):
            raise TypeError(
                "kind must be an "
                "EurLexLegalPermissionKind"
            )

        if not isinstance(
            self.language,
            LanguageCode,
        ):
            raise TypeError(
                "language must be a LanguageCode"
            )

        if self.language != LanguageCode("en"):
            raise ValueError(
                "legal permissions must be English"
            )

    @property
    def normalized_subject(self) -> str:
        """Return a case-insensitive subject key."""
        return self.subject.casefold()


@dataclass(frozen=True, slots=True)
class EurLexLegalPermissions:
    """Contain explicit permissions from one document."""

    permissions: tuple[
        EurLexLegalPermission,
        ...,
    ] = ()

    def __post_init__(self) -> None:
        if not isinstance(
            self.permissions,
            tuple,
        ):
            raise TypeError(
                "permissions must be a tuple"
            )

        if any(
            not isinstance(
                permission,
                EurLexLegalPermission,
            )
            for permission in self.permissions
        ):
            raise TypeError(
                "permissions must contain "
                "EurLexLegalPermission values"
            )

    def permissions_for_article(
        self,
        article_node_id: str,
    ) -> tuple[EurLexLegalPermission, ...]:
        """Return permissions attached to one article."""
        normalized = _normalize_required_text(
            article_node_id,
            name="article_node_id",
        )

        return tuple(
            permission
            for permission in self.permissions
            if permission.article_node_id
            == normalized
        )

    def permissions_for_subject(
        self,
        subject: str,
    ) -> tuple[EurLexLegalPermission, ...]:
        """Return permissions for an exact normalized subject."""
        normalized = _normalize_required_text(
            subject,
            name="subject",
        ).casefold()

        return tuple(
            permission
            for permission in self.permissions
            if permission.normalized_subject
            == normalized
        )


def normalize_legal_permissions(
    permissions: tuple[
        EurLexLegalPermission,
        ...,
    ],
) -> EurLexLegalPermissions:
    """Deduplicate permissions while preserving source order."""
    if not isinstance(permissions, tuple):
        raise TypeError(
            "permissions must be a tuple"
        )

    if any(
        not isinstance(
            permission,
            EurLexLegalPermission,
        )
        for permission in permissions
    ):
        raise TypeError(
            "permissions must contain "
            "EurLexLegalPermission values"
        )

    return EurLexLegalPermissions(
        permissions=tuple(
            dict.fromkeys(permissions)
        )
    )
