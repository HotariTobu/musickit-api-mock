"""Responses for the storefront (``/v1/me/storefront``) endpoint."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal


@dataclass
class Storefront:
    """One Apple Music storefront's identity and language config.

    Attributes:
        id: Storefront identifier (typically a two-letter country code).
        name: Display name of the storefront.
        default_language_tag: BCP-47 default language for the storefront.
        supported_language_tags: BCP-47 language tags the storefront serves.
        explicit_content_policy: Storefront-level explicit-content policy —
            one of ``allowed``, ``opt-in``, or ``opt-out``.
    """

    id: str
    name: str
    default_language_tag: str
    supported_language_tags: list[str]
    explicit_content_policy: Literal["allowed", "opt-in", "opt-out"]


@dataclass
class StorefrontResponseSuccess:
    """200 success carrying the active storefront.

    Attributes:
        storefront: The active storefront returned to the caller.
    """

    storefront: Storefront


@dataclass
class StorefrontResponseSessionExpired:
    """Auth-rejected response that triggers MusicKit's session reset."""


@dataclass
class StorefrontResponseFailure:
    """Generic non-2xx failure that MusicKit rejects without state change."""


StorefrontResponse = (
    StorefrontResponseSuccess
    | StorefrontResponseSessionExpired
    | StorefrontResponseFailure
)


type StorefrontSetter = StorefrontResponse | Callable[[], StorefrontResponse] | None
