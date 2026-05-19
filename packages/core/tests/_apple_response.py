"""TypedDict shapes for Apple Music API responses parsed in tests.

Tests parse mock responses with ``json.loads`` and then read fields like
``body["data"][0]["attributes"]["name"]``. The recursive ``_JSONValue``
union is unsuitable for these chained subscripts because each step would
need union narrowing. These TypedDicts mirror Apple's uniform envelope
so that ``data`` / ``errors`` / ``relationships`` reads return concrete
types and chain naturally.

Attribute leaves remain ``_JSONValue`` because attributes vary per
resource; tests reading deeply into attributes (e.g. ``artwork["width"]``)
cast at the read site to the specific attribute shape they expect.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from musickit_api_mock.json_value import _JSONValue


class _AppleRelationshipBlock(TypedDict, total=False):
    data: list[_AppleResource]
    href: str
    next: str
    meta: dict[str, _JSONValue]


class _AppleResource(TypedDict, total=False):
    id: str
    type: str
    href: str
    attributes: dict[str, _JSONValue]
    relationships: dict[str, _AppleRelationshipBlock]
    meta: dict[str, _JSONValue]


class _AppleError(TypedDict, total=False):
    code: str
    title: str
    detail: str
    status: str
    id: str
    source: dict[str, _JSONValue]


class _AppleResponse(TypedDict, total=False):
    data: list[_AppleResource]
    errors: list[_AppleError]
    meta: dict[str, _JSONValue]
    next: str
    href: str
    results: dict[str, _JSONValue]


class _AppleArtwork(TypedDict, total=False):
    url: str
    width: int
    height: int
    bgColor: str
    textColor1: str
    textColor2: str
    textColor3: str
    textColor4: str
    hasP3: bool


class _ApplePreview(TypedDict, total=False):
    url: str


_LicenseResponseBody = TypedDict(
    "_LicenseResponseBody",
    {
        "license": str,
        "status": int,
        "errorCode": int,
        "stkn": str,
        "renew-after": int,
    },
    total=False,
)


class _WebPlaybackSongEntry(TypedDict, total=False):
    songId: str
    assets: list[dict[str, _JSONValue]]
    keyCert: str


class _WebPlaybackResponseBody(TypedDict, total=False):
    status: int
    songList: list[_WebPlaybackSongEntry]


class _AccountSubscription(TypedDict, total=False):
    active: bool
    storefront: str


class _AccountMeta(TypedDict, total=False):
    subscription: _AccountSubscription
