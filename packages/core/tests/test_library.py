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


def test_q07_library_songs_batch(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/songs?ids=i.s1"
    )
    assert status == 200
    assert body["data"][0]["type"] == "library-songs"
    assert body["data"][0]["id"] == "i.s1"


def test_q07_trailing_slash_form(mock: MusicKitApiMock) -> None:
    status, _body = _get(
        mock, "https://api.music.apple.com/v1/me/library/songs/?ids=i.s1"
    )
    assert status == 200


def test_q07_format_violating_id_misses_silently(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/songs?ids=12345",
    )
    assert status == 200
    assert body == {"data": []}


def test_q07_library_empty_ids_400(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/me/library/songs?ids=")
    assert status == 400
    err = body["errors"][0]
    assert err["code"] == "40005"
    assert err["title"] == "Invalid Parameter Value"


def test_q07_library_no_ids_param_400(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/me/library/songs")
    assert status == 400
    err = body["errors"][0]
    assert err["code"] == "40003"
    assert err["title"] == "Missing Parameter"


def test_q08_dead_path_returns_400(mock: MusicKitApiMock) -> None:
    status, _body = _get(
        mock, "https://api.music.apple.com/v1/me/library/library-songs/i.s1"
    )
    assert status == 400


def test_q08_prime_singular_path(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/me/library/songs/i.s1")
    assert status == 200
    assert body["data"][0]["id"] == "i.s1"


def test_q09_library_album_with_tracks(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/albums/l.a1?include=tracks",
    )
    assert status == 200
    rel = body["data"][0]["relationships"]
    assert rel["tracks"]["data"][0]["id"] == "i.s1"


def test_q10_library_playlist_with_tracks(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/playlists/p.pl1?include=tracks&extend=hasCollaboration",
    )
    assert status == 200
    attrs = body["data"][0]["attributes"]
    assert attrs["hasCollaboration"] is False


def test_q11_library_artist_minimal(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/me/library/artists/r.ar1")
    assert status == 200
    attrs = body["data"][0]["attributes"]
    assert attrs == {"name": "Lib Artist"}


def test_q12_library_music_video(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/music-videos/i.mv1"
    )
    assert status == 200
    assert body["data"][0]["type"] == "library-music-videos"
    assert "relationships" not in body["data"][0]


def test_q12_library_music_video_with_relationships(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/music-videos/i.mv1?include=albums,artists",
    )
    assert status == 200
    rel = body["data"][0]["relationships"]
    assert rel["albums"]["data"][0]["id"] == "l.a1"
    assert rel["albums"]["data"][0]["type"] == "library-albums"
    assert rel["artists"]["data"][0]["id"] == "r.ar1"
    assert rel["artists"]["data"][0]["type"] == "library-artists"


def test_q09_library_album_include_artists(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/albums/l.a1?include=artists",
    )
    assert status == 200
    rels = body["data"][0]["relationships"]
    assert "artists" in rels
    assert rels["artists"]["data"][0]["id"] == "r.ar1"
    assert rels["artists"]["data"][0]["type"] == "library-artists"


def test_q09_library_album_no_include_artists(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/albums/l.a1",
    )
    assert status == 200
    rels = body["data"][0]["relationships"]
    assert "artists" not in rels


def test_library_playlist_extends_has_collaboration(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/playlists/p.pl1?include=tracks&extend=hasCollaboration",
    )
    assert status == 200
    assert "hasCollaboration" in body["data"][0]["attributes"]


def test_library_playlist_has_collaboration_default(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/playlists/p.pl1?include=tracks"
    )
    assert status == 200
    assert "hasCollaboration" in body["data"][0]["attributes"]


def test_library_song_include_catalog(mock: MusicKitApiMock) -> None:
    """``?include=catalog`` resolves LibrarySong.catalog_id to the catalog song."""
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/songs/i.s1?include=catalog",
    )
    assert status == 200
    rels = body["data"][0]["relationships"]
    assert "catalog" in rels
    catalog_data = rels["catalog"]["data"][0]
    assert catalog_data["id"] == "1"
    assert catalog_data["type"] == "songs"
    assert catalog_data["attributes"]["name"] == "Test Song"


def test_library_song_no_include_no_catalog(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/me/library/songs/i.s1")
    assert status == 200
    rels = body["data"][0].get("relationships")
    assert rels is None or "catalog" not in rels


def test_library_album_include_catalog(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/albums/l.a1?include=catalog",
    )
    assert status == 200
    rels = body["data"][0]["relationships"]
    assert "catalog" in rels
    catalog_data = rels["catalog"]["data"][0]
    assert catalog_data["id"] == "a1"
    assert catalog_data["type"] == "albums"
    assert catalog_data["attributes"]["name"] == "Test Album"


def test_library_invalid_language_tag_400(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/songs?ids=i.s1&l=invalid-XX",
    )
    assert status == 400
    err = body["errors"][0]
    assert err["code"] == "40005"
    assert err["source"] == {"parameter": "l"}


def test_library_album_invalid_language_tag_400(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/albums/l.a1?l=invalid-XX",
    )
    assert status == 400
    err = body["errors"][0]
    assert err["source"] == {"parameter": "l"}


def test_library_album_valid_language_tag_passes(mock: MusicKitApiMock) -> None:
    status, _body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/albums/l.a1?l=ja-JP",
    )
    assert status == 200


def test_library_playlist_invalid_language_tag_400(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/playlists/p.pl1?l=invalid-XX",
    )
    assert status == 400
    err = body["errors"][0]
    assert err["source"] == {"parameter": "l"}


def test_library_music_video_valid_language_tag_passes(
    mock: MusicKitApiMock,
) -> None:
    status, _body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/music-videos/i.mv1?l=en-US",
    )
    assert status == 200


def test_library_album_tracks_relationship_invalid_language_tag_400(
    mock: MusicKitApiMock,
) -> None:
    """Library relationship endpoints honor ``?l=`` validation too."""
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/albums/l.a1/tracks?l=invalid-XX",
    )
    assert status == 400
    err = body["errors"][0]
    assert err["source"] == {"parameter": "l"}
