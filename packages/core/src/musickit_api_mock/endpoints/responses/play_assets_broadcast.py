"""Broadcast play-assets family (radio family)."""

from collections.abc import Callable
from dataclasses import dataclass

from musickit_api_mock.json_value import _JSONValue


@dataclass
class PlayAssetsBroadcastContext:
    """Context for the broadcast play-assets setter."""

    station_id: str


@dataclass
class PlayAssetsBroadcastAsset:
    """One broadcast play-asset (URL only; broadcast plays unencrypted)."""

    url: str


@dataclass
class PlayAssetsBroadcastResponseSuccess:
    """200 response carrying broadcast assets and optional ``track-info`` payload."""

    assets: list[PlayAssetsBroadcastAsset]
    track_info: dict[str, _JSONValue] | None = None


@dataclass
class PlayAssetsBroadcastResponseEmptyAssets:
    """200 with an empty asset list → CONTENT_UNAVAILABLE."""


@dataclass
class PlayAssetsBroadcastResponseServerError:
    """500 response → SERVER_ERROR."""


@dataclass
class PlayAssetsBroadcastResponseSubscriptionError:
    """403 with body ``errors[0].code = "40303"`` → SUBSCRIPTION_ERROR."""


@dataclass
class PlayAssetsBroadcastResponseAccessDenied:
    """403 with body ``errors[0].code != "40303"`` → ACCESS_DENIED."""


@dataclass
class PlayAssetsBroadcastResponseContentUnavailable:
    """Other non-2xx (lumped by MusicKit as CONTENT_UNAVAILABLE)."""


PlayAssetsBroadcastResponse = (
    PlayAssetsBroadcastResponseSuccess
    | PlayAssetsBroadcastResponseEmptyAssets
    | PlayAssetsBroadcastResponseServerError
    | PlayAssetsBroadcastResponseSubscriptionError
    | PlayAssetsBroadcastResponseAccessDenied
    | PlayAssetsBroadcastResponseContentUnavailable
)


type PlayAssetsBroadcastSetter = (
    PlayAssetsBroadcastResponse
    | dict[str, PlayAssetsBroadcastResponse]
    | Callable[[PlayAssetsBroadcastContext], PlayAssetsBroadcastResponse]
    | None
)
