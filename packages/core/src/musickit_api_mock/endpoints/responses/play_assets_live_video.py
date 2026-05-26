"""Live-video play-assets family (radio family)."""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class PlayAssetsLiveVideoContext:
    """Context for the live-video play-assets setter.

    Attributes:
        station_id: Catalog station id the live-video play-asset is for.
    """

    station_id: str


@dataclass
class PlayAssetsLiveVideoAsset:
    """One live-video play-asset (URL plus DRM endpoints).

    Attributes:
        url: URL of the live-video media.
        fair_play_key_certificate_url: FairPlay certificate endpoint.
        key_server_url: License-acquisition endpoint.
        widevine_key_certificate_url: Widevine certificate endpoint.
    """

    url: str
    fair_play_key_certificate_url: str
    key_server_url: str
    widevine_key_certificate_url: str


@dataclass
class PlayAssetsLiveVideoResponseSuccess:
    """200 response carrying live-video assets.

    Attributes:
        assets: Live-video play-assets returned to the caller.
    """

    assets: list[PlayAssetsLiveVideoAsset]


@dataclass
class PlayAssetsLiveVideoResponseEmptyAssets:
    """200 with an empty asset list that triggers CONTENT_UNAVAILABLE."""


@dataclass
class PlayAssetsLiveVideoResponseServerError:
    """500 response that triggers SERVER_ERROR."""


@dataclass
class PlayAssetsLiveVideoResponseSubscriptionError:
    """403 with body ``errors[0].code = "40303"`` that triggers SUBSCRIPTION_ERROR."""


@dataclass
class PlayAssetsLiveVideoResponseAccessDenied:
    """403 with body ``errors[0].code != "40303"`` that triggers ACCESS_DENIED."""


@dataclass
class PlayAssetsLiveVideoResponseContentUnavailable:
    """Other non-2xx response, lumped by MusicKit as CONTENT_UNAVAILABLE."""


PlayAssetsLiveVideoResponse = (
    PlayAssetsLiveVideoResponseSuccess
    | PlayAssetsLiveVideoResponseEmptyAssets
    | PlayAssetsLiveVideoResponseServerError
    | PlayAssetsLiveVideoResponseSubscriptionError
    | PlayAssetsLiveVideoResponseAccessDenied
    | PlayAssetsLiveVideoResponseContentUnavailable
)


type PlayAssetsLiveVideoSetter = (
    PlayAssetsLiveVideoResponse
    | dict[str, PlayAssetsLiveVideoResponse]
    | Callable[[PlayAssetsLiveVideoContext], PlayAssetsLiveVideoResponse]
    | None
)
