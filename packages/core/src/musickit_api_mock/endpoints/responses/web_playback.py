"""Responses, asset shapes, and context for the web-playback endpoint.

The web-playback endpoint is body-driven: MusicKit ignores the HTTP status and
maps the body's failure code to one of 14 distinct reasons. The unsupported-error
variant is triggered by an empty ``songList``; the other 13 carry a numeric
``failureType`` matching MKError.Reason.
"""

from collections.abc import Callable, Mapping
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
class WebPlaybackCatalogSong:
    """Web-playback payload for a catalog song (DRM URLs, asset list, optional HLS).

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
class WebPlaybackCatalogLibrarySong:
    """Web-playback payload for a library song that plays through its catalog song.

    Carries the catalog song's DRM URLs and assets; the mock marks the
    payload as needing playback reporting, as Apple does for library items.

    Attributes:
        hls_key_cert_url: FairPlay certificate endpoint for HLS playback.
        hls_key_server_url: License-acquisition endpoint for HLS playback.
        widevine_cert_url: Widevine certificate endpoint.
        assets: Per-variant playback assets for the song.
        song_id: Catalog song id the library song plays through.
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
class WebPlaybackUploadedLibraryAssetMetadata:
    """Tag metadata Apple attaches to an uploaded library song's asset.

    MusicKit copies these onto the playing media item.

    Attributes:
        item_name: Song title.
        artist_name: Primary artist name.
        playlist_name: Album name.
        duration: Duration in milliseconds.
        kind: Media kind (``song``).
        track_number: Track number within the album.
        disc_number: Disc number within the album.
        genre: Genre name.
        composer_name: Composer name.
        explicit: ``1`` for explicit content, ``0`` otherwise.
        release_date: ISO-8601 release date.
        cloud_id: Cloud library id of the upload.
        xid: Vendor-qualified ISRC (``<vendor>:isrc:<code>``).
    """

    item_name: str
    artist_name: str
    playlist_name: str
    duration: int
    kind: str
    track_number: int | None = None
    disc_number: int | None = None
    genre: str | None = None
    composer_name: str | None = None
    explicit: int | None = None
    release_date: str | None = None
    cloud_id: int | None = None
    xid: str | None = None


@dataclass
class WebPlaybackUploadedLibraryAsset:
    """The single raw-file asset of an uploaded library song.

    Attributes:
        url: URL of the audio file.
        metadata: Tag metadata for the file.
    """

    url: str
    metadata: WebPlaybackUploadedLibraryAssetMetadata


@dataclass
class WebPlaybackUploadedLibrarySong:
    """Web-playback payload for an uploaded library song (raw file, no DRM).

    The mock emits ``songId: -1`` and marks the payload as not needing
    playback reporting, as Apple does for uploads.

    Attributes:
        asset: The song's raw-file asset.
        artwork_url: Artwork URL for the song, when it has artwork.
    """

    asset: WebPlaybackUploadedLibraryAsset
    artwork_url: str | None = None


WebPlaybackSong = (
    WebPlaybackCatalogSong
    | WebPlaybackCatalogLibrarySong
    | WebPlaybackUploadedLibrarySong
)


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
class WebPlaybackCatalogItemContext:
    """Context for a web-playback request MusicKit makes for a catalog item.

    Attributes:
        salable_adam_id: Salable adam id the web-playback request is for.
    """

    salable_adam_id: str


@dataclass
class WebPlaybackLibraryItemContext:
    """Context for a web-playback request MusicKit makes for a library item.

    MusicKit omits each field from the request body when the library item
    has no value for it.

    Attributes:
        subscription_adam_id: Catalog song adam id the library item plays
            through.
        universal_library_id: Library id of the item.
        purchase_adam_id: Purchased adam id of the item.
    """

    subscription_adam_id: str | None
    universal_library_id: str | None
    purchase_adam_id: str | None


WebPlaybackContext = WebPlaybackCatalogItemContext | WebPlaybackLibraryItemContext


type WebPlaybackSetter = (
    WebPlaybackResponse
    | Mapping[str, WebPlaybackResponse]
    | Callable[[WebPlaybackContext], WebPlaybackResponse]
    | None
)
