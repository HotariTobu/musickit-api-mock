"""Live-audio play-assets family (radio family)."""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class PlayAssetsLiveAudioContext:
    """Context for the live-audio play-assets setter."""

    station_id: str


@dataclass
class PlayAssetsLiveAudioAsset:
    """One live-audio play-asset (URL plus DRM endpoints)."""

    url: str
    fair_play_key_certificate_url: str
    key_server_url: str
    widevine_key_certificate_url: str


@dataclass
class PlayAssetsLiveAudioResponseSuccess:
    """200 response carrying live-audio assets."""

    assets: list[PlayAssetsLiveAudioAsset]


@dataclass
class PlayAssetsLiveAudioResponseEmptyAssets:
    """200 with an empty asset list → CONTENT_UNAVAILABLE."""


@dataclass
class PlayAssetsLiveAudioResponseServerError:
    """500 response → SERVER_ERROR."""


@dataclass
class PlayAssetsLiveAudioResponseSubscriptionError:
    """403 with body ``errors[0].code = "40303"`` → SUBSCRIPTION_ERROR."""


@dataclass
class PlayAssetsLiveAudioResponseAccessDenied:
    """403 with body ``errors[0].code != "40303"`` → ACCESS_DENIED."""


@dataclass
class PlayAssetsLiveAudioResponseContentUnavailable:
    """Other non-2xx (lumped by MusicKit as CONTENT_UNAVAILABLE)."""


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
