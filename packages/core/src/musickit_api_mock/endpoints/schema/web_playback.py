"""Web-playback success / unsupported / failure body builders."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.endpoints.responses.web_playback import (
    WebPlaybackCatalogLibrarySong,
    WebPlaybackUploadedLibrarySong,
)
from musickit_api_mock.endpoints.schema.builders import _strip_none

if TYPE_CHECKING:
    from musickit_api_mock.endpoints.responses.web_playback import (
        WebPlaybackAsset,
        WebPlaybackResponseSuccess,
        WebPlaybackSong,
        WebPlaybackUploadedLibraryAsset,
        WebPlaybackUploadedLibraryAssetMetadata,
    )
    from musickit_api_mock.json_value import _JSONValue


def _web_playback_asset(a: WebPlaybackAsset) -> dict[str, _JSONValue]:
    return _strip_none(
        {
            "flavor": a.flavor,
            "URL": a.url,
            "metadata": a.metadata,
            "artworkURL": a.artwork_url,
        }
    )


def _web_playback_uploaded_metadata(
    m: WebPlaybackUploadedLibraryAssetMetadata,
) -> dict[str, _JSONValue]:
    return _strip_none(
        {
            "itemName": m.item_name,
            "artistName": m.artist_name,
            "playlistName": m.playlist_name,
            "duration": m.duration,
            "kind": m.kind,
            "trackNumber": m.track_number,
            "discNumber": m.disc_number,
            "genre": m.genre,
            "composerName": m.composer_name,
            "explicit": m.explicit,
            "releaseDate": m.release_date,
            "cloud-id": m.cloud_id,
            "xid": m.xid,
        }
    )


def _web_playback_uploaded_asset(
    a: WebPlaybackUploadedLibraryAsset,
) -> dict[str, _JSONValue]:
    return {"URL": a.url, "metadata": _web_playback_uploaded_metadata(a.metadata)}


def _web_playback_song(s: WebPlaybackSong) -> dict[str, _JSONValue]:
    if isinstance(s, WebPlaybackUploadedLibrarySong):
        return _strip_none(
            {
                "songId": -1,
                "needsPlaybackReporting": False,
                "artworkURL": s.artwork_url,
                "assets": [_web_playback_uploaded_asset(s.asset)],
            }
        )
    out: dict[str, _JSONValue] = {
        "songId": s.song_id,
        "hls-key-cert-url": s.hls_key_cert_url,
        "hls-key-server-url": s.hls_key_server_url,
        "widevine-cert-url": s.widevine_cert_url,
        "hls-playlist-url": s.hls_playlist_url,
        "assets": [_web_playback_asset(a) for a in s.assets],
    }
    if isinstance(s, WebPlaybackCatalogLibrarySong):
        out["needsPlaybackReporting"] = True
    return _strip_none(out)


def _web_playback_success_body(
    resp: WebPlaybackResponseSuccess,
) -> dict[str, _JSONValue]:
    return {"songList": [_web_playback_song(s) for s in resp.song_list], "status": 0}


def _web_playback_unsupported_body() -> dict[str, _JSONValue]:
    """Empty-songList success shape for the unsupported-error variant."""
    return {"songList": [], "status": 0}


def _web_playback_failure_body(code: int) -> dict[str, _JSONValue]:
    """Failure body keyed by Apple ``failureType`` numeric code."""
    return {"failureType": code, "status": code}
