"""Catalog-song play-assets family."""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class PlayAssetsCatalogSongContext:
    """Context for the catalog-song play-assets setter."""

    adam_id: str


@dataclass
class PlayAssetsCatalogSongAsset:
    """One catalog-song play-asset (URL plus DRM endpoints)."""

    url: str
    fair_play_key_certificate_url: str
    key_server_url: str
    widevine_key_certificate_url: str


@dataclass
class PlayAssetsCatalogSongResponseSuccess:
    """200 response carrying catalog-song assets."""

    assets: list[PlayAssetsCatalogSongAsset]


@dataclass
class PlayAssetsCatalogSongResponseContentUnavailable:
    """Any outcome MusicKit lumps into CONTENT_UNAVAILABLE.

    For the catalog-song path MusicKit does not branch on HTTP status: empty
    assets, missing ``results``, or any non-2xx body that parses as JSON all
    surface as CONTENT_UNAVAILABLE. The mock emits an empty assets body.
    """


PlayAssetsCatalogSongResponse = (
    PlayAssetsCatalogSongResponseSuccess
    | PlayAssetsCatalogSongResponseContentUnavailable
)


type PlayAssetsCatalogSongSetter = (
    PlayAssetsCatalogSongResponse
    | dict[str, PlayAssetsCatalogSongResponse]
    | Callable[[PlayAssetsCatalogSongContext], PlayAssetsCatalogSongResponse]
    | None
)
