"""Responses for the storefront (``/v1/me/storefront``) endpoint."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal


@dataclass
class Storefront:
    """One Apple Music storefront's identity and language config."""

    id: str
    name: str
    default_language_tag: str
    supported_language_tags: list[str]
    explicit_content_policy: Literal["allowed", "opt-in", "opt-out"]


@dataclass
class StorefrontResponseSuccess:
    """200 success carrying the active storefront."""

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
