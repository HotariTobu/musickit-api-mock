"""Responses, asset shapes, and context for the web-playback endpoint.

The web-playback endpoint is body-driven: MusicKit ignores the HTTP status and
maps the body's failure code to one of 14 distinct reasons. The unsupported-error
variant is triggered by an empty ``songList``; the other 13 carry a numeric
``failureType`` matching MKError.Reason.
"""

from collections.abc import Callable
from dataclasses import dataclass

from musickit_api_mock.json_value import _JSONValue


@dataclass
class WebPlaybackAsset:
    """One playback asset variant (URL plus optional metadata).

    Attributes:
        flavor: Apple-defined flavor tag describing the asset bitrate or
            codec (e.g. ``28:ctrp256``).
        url: URL of the asset media.
        metadata: Optional metadata payload Apple emits alongside the asset.
        artwork_url: Optional artwork URL specific to this asset variant.
    """

    flavor: str
    url: str
    metadata: dict[str, _JSONValue] | None = None
    artwork_url: str | None = None


@dataclass
class WebPlaybackSong:
    """Per-song web-playback payload (DRM URLs, asset list, optional HLS).

    Attributes:
        hls_key_cert_url: FairPlay certificate endpoint for HLS playback.
        hls_key_server_url: License-acquisition endpoint for HLS playback.
        widevine_cert_url: Widevine certificate endpoint.
        assets: Per-variant playback assets for the song.
        song_id: Catalog song id the payload is for.
        hls_playlist_url: Optional HLS master-playlist URL when an HLS
            rendition is available alongside the asset variants.
    """

    hls_key_cert_url: str
    hls_key_server_url: str
    widevine_cert_url: str
    assets: list[WebPlaybackAsset]
    song_id: str
    hls_playlist_url: str | None = None


@dataclass
class WebPlaybackResponseSuccess:
    """200 response carrying one or more song payloads.

    Attributes:
        song_list: Per-song web-playback payloads returned to the caller.
    """

    song_list: list[WebPlaybackSong]


@dataclass
class WebPlaybackResponseUnsupportedError:
    """Empty ``songList`` body that triggers UNSUPPORTED_ERROR."""


@dataclass
class WebPlaybackResponseMediaLicense:
    """``failureType=-1003`` body that triggers MEDIA_LICENSE."""


@dataclass
class WebPlaybackResponseDeviceLimit:
    """``failureType`` body that triggers DEVICE_LIMIT (mock emits the canonical code)."""


@dataclass
class WebPlaybackResponseGeoBlock:
    """``failureType=-1017`` body that triggers GEO_BLOCK."""


@dataclass
class WebPlaybackResponseNotFound:
    """``failureType=1010`` body that triggers NOT_FOUND."""


@dataclass
class WebPlaybackResponseAuthorizationError:
    """``failureType=2002`` body that triggers AUTHORIZATION_ERROR (revoke)."""


@dataclass
class WebPlaybackResponseTokenExpired:
    """``failureType=2034`` body that triggers TOKEN_EXPIRED (renew + retry)."""


@dataclass
class WebPlaybackResponseSubscriptionError:
    """``failureType=3063`` body that triggers SUBSCRIPTION_ERROR."""


@dataclass
class WebPlaybackResponseContentUnavailable:
    """``failureType=3076`` body that triggers CONTENT_UNAVAILABLE."""


@dataclass
class WebPlaybackResponseContentRestricted:
    """``failureType=3082`` body that triggers CONTENT_RESTRICTED."""


@dataclass
class WebPlaybackResponseStreamUpsell:
    """``failureType=3084`` body that triggers STREAM_UPSELL."""


@dataclass
class WebPlaybackResponseServerError:
    """``failureType=5002`` body that triggers SERVER_ERROR."""


@dataclass
class WebPlaybackResponsePlayReadyCbcEncryptionError:
    """``failureType=180202`` body for PlayReady CBC encryption error."""


@dataclass
class WebPlaybackResponseWidevineCdmExpired:
    """``failureType=190121`` body for Widevine CDM expired."""


WebPlaybackResponse = (
    WebPlaybackResponseSuccess
    | WebPlaybackResponseUnsupportedError
    | WebPlaybackResponseMediaLicense
    | WebPlaybackResponseDeviceLimit
    | WebPlaybackResponseGeoBlock
    | WebPlaybackResponseNotFound
    | WebPlaybackResponseAuthorizationError
    | WebPlaybackResponseTokenExpired
    | WebPlaybackResponseSubscriptionError
    | WebPlaybackResponseContentUnavailable
    | WebPlaybackResponseContentRestricted
    | WebPlaybackResponseStreamUpsell
    | WebPlaybackResponseServerError
    | WebPlaybackResponsePlayReadyCbcEncryptionError
    | WebPlaybackResponseWidevineCdmExpired
)


@dataclass
class WebPlaybackContext:
    """Context for the web-playback setter.

    Attributes:
        salable_adam_id: Salable adam id the web-playback request is for.
    """

    salable_adam_id: str


type WebPlaybackSetter = (
    WebPlaybackResponse
    | dict[str, WebPlaybackResponse]
    | Callable[[WebPlaybackContext], WebPlaybackResponse]
    | None
)
