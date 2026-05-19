"""Standalone relationship endpoint smoke tests.

Each relationship endpoint backs the ``next`` URL emitted in a parent
resource's ``relationships`` block, plus the public methods MusicKit JS
exposes (e.g. ``albumRelationship``). One request per endpoint verifies
that the URL is matched, the handler resolves through the configured
data sources, and the expected ids surface in ``data[]``.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from musickit_api_mock import MusicKitApiMock, Request

if TYPE_CHECKING:
    from tests._apple_response import _AppleResponse


def _get(mock: MusicKitApiMock, url: str) -> tuple[int, _AppleResponse]:
    resp = mock.handle_request(Request(method="GET", url=url, headers={}, body=None))
    assert resp is not None
    return resp.status, json.loads(resp.body)


def test_artist_albums_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/artists/ar1/albums"
    )
    assert status == 200
    assert [x["id"] for x in body["data"]] == ["a1"]
    assert body["data"][0]["type"] == "albums"


def test_album_artists_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/albums/a1/artists"
    )
    assert status == 200
    assert [x["id"] for x in body["data"]] == ["ar1"]
    assert body["data"][0]["type"] == "artists"


def test_playlist_tracks_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/playlists/pl1/tracks"
    )
    assert status == 200
    assert [x["id"] for x in body["data"]] == ["1"]


def test_song_artists_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs/1/artists"
    )
    assert status == 200
    assert [x["id"] for x in body["data"]] == ["ar1"]


def test_song_composers_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs/1/composers"
    )
    assert status == 200
    assert [x["id"] for x in body["data"]] == ["ar1"]


def test_library_album_tracks_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/albums/l.a1/tracks"
    )
    assert status == 200
    assert [x["id"] for x in body["data"]] == ["i.s1"]
    assert body["meta"]["total"] == 1


def test_library_album_artists_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/albums/l.a1/artists"
    )
    assert status == 200
    assert [x["id"] for x in body["data"]] == ["r.ar1"]
    assert body["data"][0]["type"] == "library-artists"


def test_library_playlist_tracks_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/playlists/p.pl1/tracks"
    )
    assert status == 200
    assert [x["id"] for x in body["data"]] == ["i.s1"]


def test_library_music_video_albums_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/music-videos/i.mv1/albums"
    )
    assert status == 200
    assert [x["id"] for x in body["data"]] == ["l.a1"]


def test_library_music_video_artists_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/music-videos/i.mv1/artists"
    )
    assert status == 200
    assert [x["id"] for x in body["data"]] == ["r.ar1"]


def test_music_video_albums_standalone(mock: MusicKitApiMock) -> None:
    status, _body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/music-videos/mv1/albums"
    )
    # mv has no album_ids configured in fixture; missing ids resolve to empty data.
    assert status == 200


def test_music_video_artists_standalone(mock: MusicKitApiMock) -> None:
    status, _body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/music-videos/mv1/artists"
    )
    assert status == 200
