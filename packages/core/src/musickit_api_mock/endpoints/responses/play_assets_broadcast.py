"""Broadcast play-assets family (radio family)."""

from collections.abc import Callable
from dataclasses import dataclass

from musickit_api_mock.json_value import _JSONValue


@dataclass
class PlayAssetsBroadcastContext:
    """Context for the broadcast play-assets setter.

    Attributes:
        station_id: Catalog station id the broadcast play-asset is for.
    """

    station_id: str


@dataclass
class PlayAssetsBroadcastAsset:
    """One broadcast play-asset (URL only; broadcast plays unencrypted).

    Attributes:
        url: URL of the broadcast media.
    """

    url: str


@dataclass
class PlayAssetsBroadcastResponseSuccess:
    """200 response carrying broadcast assets and optional track-info payload.

    Attributes:
        assets: Broadcast play-assets returned to the caller.
        track_info: Optional ``track-info`` payload Apple emits alongside
            broadcast assets.
    """

    assets: list[PlayAssetsBroadcastAsset]
    track_info: dict[str, _JSONValue] | None = None


@dataclass
class PlayAssetsBroadcastResponseEmptyAssets:
    """200 with an empty asset list that triggers CONTENT_UNAVAILABLE."""


@dataclass
class PlayAssetsBroadcastResponseServerError:
    """500 response that triggers SERVER_ERROR."""


@dataclass
class PlayAssetsBroadcastResponseSubscriptionError:
    """403 with body ``errors[0].code = "40303"`` that triggers SUBSCRIPTION_ERROR."""


@dataclass
class PlayAssetsBroadcastResponseAccessDenied:
    """403 with body ``errors[0].code != "40303"`` that triggers ACCESS_DENIED."""


@dataclass
class PlayAssetsBroadcastResponseContentUnavailable:
    """Other non-2xx response, lumped by MusicKit as CONTENT_UNAVAILABLE."""


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
