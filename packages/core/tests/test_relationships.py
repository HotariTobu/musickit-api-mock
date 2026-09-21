"""Standalone relationship endpoint smoke tests.

Each relationship endpoint backs the ``next`` URL emitted in a parent
resource's ``relationships`` block, plus the public methods MusicKit JS
exposes (e.g. ``albumRelationship``). One request per endpoint verifies
that the URL is matched, the handler resolves through the configured
data sources, and the full response body is what the parent's block
promised.
"""

from __future__ import annotations

import json

from musickit_api_mock import MusicKitApiMock, Request

from tests._expected import (
    ALBUM,
    ALBUM_REF,
    ARTIST_ATTRIBUTES,
    ARTIST_REF,
    LIBRARY_ALBUM,
    LIBRARY_ARTIST,
    LIBRARY_SONG,
    SONG,
)

_ARTIST_BODY = {
    "data": [
        {
            **ARTIST_REF,
            "attributes": ARTIST_ATTRIBUTES,
            "relationships": {
                "albums": {
                    "href": "/v1/catalog/us/artists/ar1/albums",
                    "data": [ALBUM_REF],
                },
            },
        }
    ]
}


def _get(mock: MusicKitApiMock, url: str) -> tuple[int, object]:
    resp = mock.handle_request(Request(method="GET", url=url, headers={}, body=None))
    assert resp is not None
    return resp.status, json.loads(resp.body)


def test_artist_albums_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/artists/ar1/albums"
    )
    assert status == 200
    assert body == {"data": [ALBUM]}


def test_album_artists_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/albums/a1/artists"
    )
    assert status == 200
    assert body == _ARTIST_BODY


def test_playlist_tracks_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/playlists/pl1/tracks"
    )
    assert status == 200
    assert body == {"data": [SONG]}


def test_song_artists_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs/1/artists"
    )
    assert status == 200
    assert body == _ARTIST_BODY


def test_song_composers_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs/1/composers"
    )
    assert status == 200
    assert body == _ARTIST_BODY


def test_library_album_tracks_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/albums/l.a1/tracks"
    )
    assert status == 200
    assert body == {"data": [LIBRARY_SONG], "meta": {"total": 1}}


def test_library_album_artists_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/albums/l.a1/artists"
    )
    assert status == 200
    assert body == {"data": [LIBRARY_ARTIST]}


def test_library_playlist_tracks_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/playlists/p.pl1/tracks"
    )
    assert status == 200
    assert body == {"data": [LIBRARY_SONG], "meta": {"total": 1}}


def test_library_music_video_albums_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/music-videos/i.mv1/albums"
    )
    assert status == 200
    assert body == {"data": [LIBRARY_ALBUM]}


def test_library_music_video_artists_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/music-videos/i.mv1/artists"
    )
    assert status == 200
    assert body == {"data": [LIBRARY_ARTIST]}


def test_music_video_albums_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/music-videos/mv1/albums"
    )
    assert status == 200
    assert body == {"data": [ALBUM]}


def test_music_video_artists_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/music-videos/mv1/artists"
    )
    assert status == 200
    assert body == _ARTIST_BODY
