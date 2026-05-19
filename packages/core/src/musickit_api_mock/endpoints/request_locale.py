"""Request locale resolution for the ``?l=`` request flow.

The mock threads the BCP 47 locale tag from the URL's ``?l=`` value into
the lookup context so user data sources can return locale-specific
resources. When ``?l=`` is absent, the mock does not fabricate a locale
from the storefront slug or any other source — the locale field is
``None`` and the user's data resolver decides how to handle the absence.

For library / me endpoints (no slug in the URL), the locale falls back to
the user storefront's ``default_language_tag`` only when that value is
user-provided via ``mock.endpoints.storefront`` — that is user data, not a
mock invention.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.endpoints.query import (
    _LanguageTagAbsent,
    _LanguageTagInvalid,
    _LanguageTagValid,
    _parse_language_tag,
)
from musickit_api_mock.endpoints.schema import _invalid_language_tag_envelope
from musickit_api_mock.transport.response_builders import _json_response

if TYPE_CHECKING:
    from musickit_api_mock.endpoints.query import _LanguageTag
    from musickit_api_mock.mock import MusicKitApiMock
    from musickit_api_mock.transport.http import Request, Response


def _resolve_locale(
    tag: _LanguageTag,
    *,
    storefront_slug: str | None,
    mock: MusicKitApiMock | None = None,
) -> str | None:
    """Resolve the effective request locale.

    - Valid tag → use the tag's locale directly.
    - Absent tag + ``storefront_slug`` → ``None`` (the mock does not derive
      locale from slug).
    - Absent tag + no slug (library / me endpoints) → the user's configured
      storefront's ``default_language_tag``. ``mock`` is required to read
      the user storefront in this branch.

    Invalid tags must be rejected with a 400 by the caller before reaching
    this function.
    """
    if isinstance(tag, _LanguageTagValid):
        return tag.locale
    if not isinstance(tag, _LanguageTagAbsent):
        raise TypeError(f"unexpected tag: {type(tag).__name__}")
    if storefront_slug is not None:
        return None
    if mock is None:
        raise ValueError("a mock instance is required when storefront_slug is None")
    from musickit_api_mock.endpoints.responses.storefront import (
        StorefrontResponseSuccess,
    )

    resp = mock._endpoint_resolver.storefront()
    if isinstance(resp, StorefrontResponseSuccess):
        return resp.storefront.default_language_tag
    raise ValueError("user storefront is not in a success state")


def _check_language_tag(req: Request) -> Response | None:
    """Validate ``?l=`` syntax. Returns 400 ``Response`` on malformed, else ``None``.

    For endpoints that don't need the resolved locale (``/v1/me/storefront``
    and ``/v1/me/account`` are response-shape-only). Endpoints that need
    the locale should use the check-and-resolve helper instead.
    """
    tag = _parse_language_tag(req.url)
    if isinstance(tag, _LanguageTagInvalid):
        return _json_response(_invalid_language_tag_envelope(tag.raw), status=400)
    return None


def _check_and_resolve_locale(
    req: Request,
    *,
    storefront_slug: str | None,
    mock: MusicKitApiMock | None = None,
) -> tuple[str | None, Response | None]:
    """Parse + validate ``?l=``, then resolve the request locale.

    Returns ``(locale, err)``: ``err`` is a 400 ``Response`` when ``?l=``
    is malformed, ``None`` otherwise. The single parse covers both the
    syntactic check and the locale lookup, so handlers don't re-parse.
    """
    tag = _parse_language_tag(req.url)
    if isinstance(tag, _LanguageTagInvalid):
        return None, _json_response(_invalid_language_tag_envelope(tag.raw), status=400)
    return _resolve_locale(tag, storefront_slug=storefront_slug, mock=mock), None
