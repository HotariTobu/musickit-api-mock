"""Web-playback success / unsupported / failure body builders."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.endpoints.schema.builders import _strip_none

if TYPE_CHECKING:
    from musickit_api_mock.endpoints.responses.web_playback import (
        WebPlaybackAsset,
        WebPlaybackResponseSuccess,
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


def _web_playback_success_body(
    resp: WebPlaybackResponseSuccess,
) -> dict[str, _JSONValue]:
    songs: list[dict[str, _JSONValue]] = [
        _strip_none(
            {
                "songId": s.song_id,
                "hls-key-cert-url": s.hls_key_cert_url,
                "hls-key-server-url": s.hls_key_server_url,
                "widevine-cert-url": s.widevine_cert_url,
                "hls-playlist-url": s.hls_playlist_url,
                "assets": [_web_playback_asset(a) for a in s.assets],
            }
        )
        for s in resp.song_list
    ]
    return {"songList": songs, "status": 0}


def _web_playback_unsupported_body() -> dict[str, _JSONValue]:
    """Empty-songList success shape for the unsupported-error variant."""
    return {"songList": [], "status": 0}


def _web_playback_failure_body(code: int) -> dict[str, _JSONValue]:
    """Failure body keyed by Apple ``failureType`` numeric code."""
    return {"failureType": code, "status": code}
