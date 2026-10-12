"""Storefront-aware language tags for Apple Music response links."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, cast
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from musickit_api_mock.endpoints.query import _LanguageTagValid, _parse_language_tag
from musickit_api_mock.endpoints.responses.storefront import StorefrontResponseSuccess
from musickit_api_mock.endpoints.storefront_languages import (
    _OBSERVED_ALIASES,
    _STOREFRONT_LANGUAGES,
)
from musickit_api_mock.transport.http import Response

if TYPE_CHECKING:
    from musickit_api_mock.json_value import _JSONValue
    from musickit_api_mock.mock import MusicKitApiMock
    from musickit_api_mock.transport.http import Request


def _normalize_response_language(
    tag: str, storefront: str | None, *, languages: Sequence[str] | None = None
) -> str:
    slug = storefront.lower() if storefront is not None else ""
    key = tag.lower()
    if observed := _OBSERVED_ALIASES.get(slug, {}).get(key):
        return observed
    profile = languages or _STOREFRONT_LANGUAGES.get(slug)
    if not profile:
        return tag
    return next((item for item in profile if item.lower() == key), profile[0])


def _language_link(link: str, tag: str) -> str:
    parsed = urlsplit(link)
    # Preserve existing query bytes (including repeated keys and encodings).
    query = "&".join(
        part
        for part in parsed.query.split("&")
        if part
        and not any(key == "l" for key, _ in parse_qsl(part, keep_blank_values=True))
    )
    language = urlencode({"l": tag})
    return urlunsplit(
        parsed._replace(query=f"{language}&{query}" if query else language)
    )


def _localize_links(value: _JSONValue, tag: str) -> _JSONValue:
    if isinstance(value, Mapping):
        return {
            key: _language_link(item, tag)
            if key in {"href", "next"} and isinstance(item, str)
            else _localize_links(item, tag)
            for key, item in value.items()
        }
    if isinstance(value, Sequence) and not isinstance(value, str):
        return [_localize_links(item, tag) for item in value]
    return value


def _has_links(value: _JSONValue) -> bool:
    if isinstance(value, Mapping):
        return any(
            (key in {"href", "next"} and isinstance(item, str)) or _has_links(item)
            for key, item in value.items()
        )
    if isinstance(value, Sequence) and not isinstance(value, str):
        return any(_has_links(item) for item in value)
    return False


def _response_language(mock: MusicKitApiMock, req: Request, resp: Response) -> Response:
    parsed = urlsplit(req.url)
    tag = _parse_language_tag(req.url)
    if (
        parsed.hostname != "api.music.apple.com"
        or not parsed.path.startswith(("/v1/catalog/", "/v1/me/"))
        or not isinstance(tag, _LanguageTagValid)
        or not 200 <= resp.status < 300
        or not resp.headers.get("Content-Type", "").startswith("application/json")
        or not resp.body
    ):
        return resp
    body = cast("_JSONValue", json.loads(resp.body))
    if not _has_links(body):
        return resp
    storefront: str | None = None
    languages: Sequence[str] | None = None
    if parsed.path.startswith("/v1/catalog/"):
        storefront = parsed.path.split("/")[3]
    elif parsed.path == "/v1/me/storefront" and isinstance(body, Mapping):
        data = body.get("data")
        if isinstance(data, list) and data and isinstance(data[0], dict):
            storefront = cast("str", data[0]["id"])
            if storefront.lower() not in _STOREFRONT_LANGUAGES:
                attributes = cast("Mapping[str, _JSONValue]", data[0]["attributes"])
                languages = [
                    cast("str", attributes["defaultLanguageTag"]),
                    *cast("Sequence[str]", attributes["supportedLanguageTags"]),
                ]
    elif mock.endpoints.storefront is not None:
        configured = mock._endpoint_resolver.storefront()
        if isinstance(configured, StorefrontResponseSuccess):
            storefront = configured.storefront.id
            if storefront.lower() not in _STOREFRONT_LANGUAGES:
                languages = [
                    configured.storefront.default_language_tag,
                    *configured.storefront.supported_language_tags,
                ]
    normalized = _normalize_response_language(
        tag.locale, storefront, languages=languages
    )
    return Response(
        status=resp.status,
        headers=resp.headers,
        body=json.dumps(
            _localize_links(body, normalized), separators=(",", ":")
        ).encode(),
    )
