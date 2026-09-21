"""TypedDict shapes for the JSON bodies the schema builders emit.

Apple's uniform envelope — ``data`` / ``errors`` / ``meta`` / ``next`` /
``results``, plus the resource and relationship blocks nested inside it —
is identical across every catalog and library endpoint, so it is named
once here rather than re-derived per builder. ``results`` is the union of
the keys the endpoints that use that slot emit, since an endpoint returns
either its own ``results`` block or the shared errors envelope.

Resource ``attributes`` stay ``_JSONValue``: they vary per resource type
and the envelope carries them opaquely. The leaf shapes that land in an
attribute slot are still named here, so a reader narrowing an attribute
back to a concrete shape has one definition to point at.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, NotRequired, TypedDict

if TYPE_CHECKING:
    from musickit_api_mock.json_value import _JSONValue


class AppleArtwork(TypedDict):
    """Artwork leaf an attribute slot carries."""

    url: str
    width: int
    height: int
    bgColor: NotRequired[str]
    textColor1: NotRequired[str]
    textColor2: NotRequired[str]
    textColor3: NotRequired[str]
    textColor4: NotRequired[str]
    hasP3: NotRequired[bool]


class ApplePreview(TypedDict):
    """Preview leaf a song or music-video attribute slot carries."""

    url: str
    hlsUrl: NotRequired[str]
    artwork: NotRequired[AppleArtwork]


class AppleRelationshipBlock(TypedDict):
    """One entry of a resource's ``relationships`` map."""

    href: str
    data: list[AppleResource]
    next: NotRequired[str]
    meta: NotRequired[dict[str, _JSONValue]]


class AppleResource(TypedDict):
    """A resource object: a shallow ref, or a full resource with attributes."""

    id: str
    type: str
    href: str
    attributes: NotRequired[dict[str, _JSONValue]]
    relationships: NotRequired[dict[str, AppleRelationshipBlock]]


class AppleError(TypedDict):
    """One entry of an ``errors`` envelope."""

    id: str
    title: str
    status: str
    code: NotRequired[str]
    detail: NotRequired[str]
    source: NotRequired[dict[str, _JSONValue]]


class PlayAssetsEntry(TypedDict):
    """One entry of ``results.assets`` on the play-assets endpoints."""

    url: str
    fairPlayKeyCertificateUrl: NotRequired[str]
    keyServerUrl: NotRequired[str]
    widevineKeyCertificateUrl: NotRequired[str]


AppleResults = TypedDict(
    "AppleResults",
    {
        "station": AppleResource,
        "tracks": list[AppleResource],
        "assets": list[PlayAssetsEntry],
        "track-info": "dict[str, _JSONValue]",
    },
    total=False,
)


class AppleResponse(TypedDict, total=False):
    """The envelope catalog, library, and play endpoints return."""

    data: list[AppleResource]
    errors: list[AppleError]
    meta: dict[str, _JSONValue]
    next: str
    results: AppleResults


class AccountSubscription(TypedDict):
    """``meta.subscription`` block of the account envelope."""

    active: bool
    storefront: str


class AccountChallenge(TypedDict):
    """``meta.challenge`` block of the account envelope."""

    subscriptionCapabilities: list[str]


class AccountMeta(TypedDict, total=False):
    """``meta`` block of the account envelope."""

    challenge: AccountChallenge
    subscription: AccountSubscription


LicenseBody = TypedDict(
    "LicenseBody",
    {
        "license": str,
        "status": int,
        "errorCode": int,
        "renew-after": NotRequired[int],
        "stkn": NotRequired[str],
    },
)


class WebPlaybackAssetEntry(TypedDict):
    """One entry of a web-playback song's ``assets``."""

    URL: str
    flavor: NotRequired[str]
    metadata: NotRequired[dict[str, _JSONValue]]
    artworkURL: NotRequired[str]


WebPlaybackSongEntry = TypedDict(
    "WebPlaybackSongEntry",
    {
        "songId": str | int,
        "assets": list[WebPlaybackAssetEntry],
        "hls-key-cert-url": NotRequired[str],
        "hls-key-server-url": NotRequired[str],
        "widevine-cert-url": NotRequired[str],
        "hls-playlist-url": NotRequired[str],
        "needsPlaybackReporting": NotRequired[bool],
        "artworkURL": NotRequired[str],
    },
)


class WebPlaybackBody(TypedDict):
    """Body of the web-playback endpoint, success or failure."""

    status: int
    songList: NotRequired[list[WebPlaybackSongEntry]]
    failureType: NotRequired[int]


class LogoutBody(TypedDict):
    """Body of the web-player logout endpoint."""

    status: int


RenewTokenBody = TypedDict("RenewTokenBody", {"music-token": NotRequired[str]})


class RenewTokenErrorBody(TypedDict):
    """401 body of the renew-music-token endpoint."""

    error: str
    error_description: str
