"""Live-audio play-assets family (radio family)."""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class PlayAssetsLiveAudioContext:
    """Context for the live-audio play-assets setter.

    Attributes:
        station_id: Catalog station id the live-audio play-asset is for.
    """

    station_id: str


@dataclass
class PlayAssetsLiveAudioAsset:
    """One live-audio play-asset (URL plus DRM endpoints).

    Attributes:
        url: URL of the live-audio media.
        fair_play_key_certificate_url: FairPlay certificate endpoint.
        key_server_url: License-acquisition endpoint.
        widevine_key_certificate_url: Widevine certificate endpoint.
    """

    url: str
    fair_play_key_certificate_url: str
    key_server_url: str
    widevine_key_certificate_url: str


@dataclass
class PlayAssetsLiveAudioResponseSuccess:
    """200 response carrying live-audio assets.

    Attributes:
        assets: Live-audio play-assets returned to the caller.
    """

    assets: list[PlayAssetsLiveAudioAsset]


@dataclass
class PlayAssetsLiveAudioResponseEmptyAssets:
    """200 with an empty asset list that triggers CONTENT_UNAVAILABLE."""


@dataclass
class PlayAssetsLiveAudioResponseServerError:
    """500 response that triggers SERVER_ERROR."""


@dataclass
class PlayAssetsLiveAudioResponseSubscriptionError:
    """403 with body ``errors[0].code = "40303"`` that triggers SUBSCRIPTION_ERROR."""


@dataclass
class PlayAssetsLiveAudioResponseAccessDenied:
    """403 with body ``errors[0].code != "40303"`` that triggers ACCESS_DENIED."""


@dataclass
class PlayAssetsLiveAudioResponseContentUnavailable:
    """Other non-2xx response, lumped by MusicKit as CONTENT_UNAVAILABLE."""


PlayAssetsLiveAudioResponse = (
    PlayAssetsLiveAudioResponseSuccess
    | PlayAssetsLiveAudioResponseEmptyAssets
    | PlayAssetsLiveAudioResponseServerError
    | PlayAssetsLiveAudioResponseSubscriptionError
    | PlayAssetsLiveAudioResponseAccessDenied
    | PlayAssetsLiveAudioResponseContentUnavailable
)


type PlayAssetsLiveAudioSetter = (
    PlayAssetsLiveAudioResponse
    | dict[str, PlayAssetsLiveAudioResponse]
    | Callable[[PlayAssetsLiveAudioContext], PlayAssetsLiveAudioResponse]
    | None
)
