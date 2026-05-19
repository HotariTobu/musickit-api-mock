"""Smoke tests for relationships and base resources added in the v0.2 round.

Covers: catalog/library cross-rels (songs/library, library-songs/catalog, etc.),
catalog/{songs,albums,artists,music-videos}/genres, album/record-labels,
artist/playlists, music-video/songs, station/radio-show, the apple-curators /
curators / personal-recommendation surfaces, and the apple-curators/grouping
relationship into the groupings resource.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, cast

from musickit_api_mock import MusicKitApiMock, Request

if TYPE_CHECKING:
    from musickit_api_mock.json_value import _JSONValue

    from tests._apple_response import _AppleResponse


def _get(mock: MusicKitApiMock, url: str) -> tuple[int, _AppleResponse]:
    resp = mock.handle_request(Request(method="GET", url=url, headers={}, body=None))
    assert resp is not None
    return resp.status, json.loads(resp.body)


# Phase B: catalog -> library (singular)


def test_catalog_song_library_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs/1/library"
    )
    assert status == 200
    assert body["data"][0]["type"] == "library-songs"
    assert body["data"][0]["id"] == "i.s1"


def test_catalog_album_library_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/albums/a1/library"
    )
    assert status == 200
    assert body["data"][0]["type"] == "library-albums"
    assert body["data"][0]["id"] == "l.a1"


def test_catalog_music_video_library_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/music-videos/mv1/library",
    )
    assert status == 200
    assert body["data"][0]["type"] == "library-music-videos"
    assert body["data"][0]["id"] == "i.mv1"


def test_catalog_playlist_library_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/playlists/pl1/library"
    )
    assert status == 200
    assert body["data"][0]["type"] == "library-playlists"
    assert body["data"][0]["id"] == "p.pl1"


def test_catalog_song_inline_library_include(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/songs/1?include=library",
    )
    assert status == 200
    rels = body["data"][0]["relationships"]
    assert rels["library"]["data"][0]["type"] == "library-songs"
    assert rels["library"]["data"][0]["id"] == "i.s1"


# Phase B: library -> catalog (singular)


def test_library_song_catalog_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/songs/i.s1/catalog"
    )
    assert status == 200
    assert body["data"][0]["type"] == "songs"
    assert body["data"][0]["id"] == "1"


def test_library_album_catalog_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/albums/l.a1/catalog"
    )
    assert status == 200
    assert body["data"][0]["type"] == "albums"
    assert body["data"][0]["id"] == "a1"


def test_library_music_video_catalog_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/music-videos/i.mv1/catalog",
    )
    assert status == 200
    assert body["data"][0]["type"] == "music-videos"
    assert body["data"][0]["id"] == "mv1"


def test_library_playlist_catalog_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/playlists/p.pl1/catalog",
    )
    assert status == 200
    assert body["data"][0]["type"] == "playlists"
    assert body["data"][0]["id"] == "pl1"


def test_library_artist_catalog_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/artists/r.ar1/catalog",
    )
    assert status == 200
    assert body["data"][0]["type"] == "artists"
    assert body["data"][0]["id"] == "ar1"


# Phase B: library -> library (paginated)


def test_library_song_albums_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/songs/i.s1/albums"
    )
    assert status == 200
    assert [x["id"] for x in body["data"]] == ["l.a1"]
    assert body["data"][0]["type"] == "library-albums"


def test_library_song_artists_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/songs/i.s1/artists"
    )
    assert status == 200
    assert [x["id"] for x in body["data"]] == ["r.ar1"]
    assert body["data"][0]["type"] == "library-artists"


def test_library_artist_albums_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/artists/r.ar1/albums"
    )
    assert status == 200
    assert [x["id"] for x in body["data"]] == ["l.a1"]
    assert body["data"][0]["type"] == "library-albums"


def test_library_song_inline_include_albums(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/songs/i.s1?include=albums",
    )
    assert status == 200
    rels = body["data"][0]["relationships"]
    assert [x["id"] for x in rels["albums"]["data"]] == ["l.a1"]


def test_library_artist_inline_include_catalog(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/artists/r.ar1?include=catalog",
    )
    assert status == 200
    rels = body["data"][0]["relationships"]
    assert rels["catalog"]["data"][0]["type"] == "artists"
    assert rels["catalog"]["data"][0]["id"] == "ar1"


# Phase C: new base resources via relationships


def test_song_genres_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs/1/genres"
    )
    assert status == 200
    assert body["data"][0]["type"] == "genres"
    assert body["data"][0]["id"] == "20"
    assert body["data"][0]["attributes"]["name"] == "Pop"


def test_song_genres_inline_include(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs/1?include=genres"
    )
    assert status == 200
    rels = body["data"][0]["relationships"]
    assert rels["genres"]["data"][0]["type"] == "genres"
    assert rels["genres"]["data"][0]["id"] == "20"


def test_album_record_labels_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/albums/a1/record-labels",
    )
    assert status == 200
    assert body["data"][0]["type"] == "record-labels"
    assert body["data"][0]["id"] == "rl1"


def test_album_record_labels_inline_include(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/albums?ids=a1&include=record-labels",
    )
    assert status == 200
    rels = body["data"][0]["relationships"]
    assert rels["record-labels"]["data"][0]["id"] == "rl1"


def test_artist_playlists_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/artists/ar1/playlists"
    )
    assert status == 200
    assert [x["id"] for x in body["data"]] == ["pl1"]
    assert body["data"][0]["type"] == "playlists"


def test_artist_station_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/artists/ar1/station"
    )
    assert status == 200
    assert body["data"][0]["type"] == "stations"
    assert body["data"][0]["id"] == "ra.978194965"


def test_song_station_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs/1/station"
    )
    assert status == 200
    assert body["data"][0]["type"] == "stations"
    assert body["data"][0]["id"] == "ra.978194965"


def test_artist_music_videos_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/artists/ar1/music-videos",
    )
    assert status == 200
    assert [x["id"] for x in body["data"]] == ["mv1"]
    assert body["data"][0]["type"] == "music-videos"


def test_music_video_songs_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/music-videos/mv1/songs",
    )
    assert status == 200
    assert [x["id"] for x in body["data"]] == ["1"]
    assert body["data"][0]["type"] == "songs"


def test_station_radio_show_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/stations/ra.978194965/radio-show",
    )
    assert status == 200
    assert body["data"][0]["type"] == "apple-curators"
    assert body["data"][0]["id"] == "cu1"


# Phase C: curators (singular base resource + playlists + grouping)


def test_apple_curator_singular(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/apple-curators/cu1",
    )
    assert status == 200
    assert body["data"][0]["type"] == "apple-curators"
    assert body["data"][0]["id"] == "cu1"
    rels = body["data"][0]["relationships"]
    assert rels["playlists"]["data"][0]["id"] == "pl1"
    assert rels["grouping"]["data"][0]["type"] == "groupings"
    assert rels["grouping"]["data"][0]["id"] == "gp1"


def test_apple_curator_playlists_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/apple-curators/cu1/playlists",
    )
    assert status == 200
    assert [x["id"] for x in body["data"]] == ["pl1"]
    assert body["data"][0]["type"] == "playlists"


def test_apple_curator_grouping_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/apple-curators/cu1/grouping",
    )
    assert status == 200
    assert body["data"][0]["type"] == "groupings"
    assert body["data"][0]["id"] == "gp1"
    assert body["data"][0]["attributes"]["name"] == "Curators"


def test_apple_curator_include_grouping(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/apple-curators/cu1?include=grouping",
    )
    assert status == 200
    rels = body["data"][0]["relationships"]
    assert rels["grouping"]["data"][0]["type"] == "groupings"
    assert rels["grouping"]["data"][0]["attributes"]["name"] == "Curators"


# Phase C: personal-recommendation surface


def test_recommendation_singular_default_contents(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/me/recommendations/rec1")
    assert status == 200
    assert body["data"][0]["type"] == "personal-recommendation"
    assert body["data"][0]["id"] == "rec1"
    title = cast("dict[str, _JSONValue]", body["data"][0]["attributes"]["title"])
    assert title["stringForDisplay"] == "Recommended Playlists"
    rels = body["data"][0]["relationships"]
    assert rels["contents"]["data"][0]["type"] == "playlists"
    assert rels["contents"]["data"][0]["id"] == "pl1"


# Phase A: direct-GET singular base resource + batch list endpoints


def test_genre_singular_endpoint(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/genres/20")
    assert status == 200
    assert body["data"][0]["type"] == "genres"
    assert body["data"][0]["id"] == "20"
    assert body["data"][0]["attributes"]["name"] == "Pop"


def test_genres_batch_with_ids(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/genres?ids=20")
    assert status == 200
    assert [x["id"] for x in body["data"]] == ["20"]
    assert body["data"][0]["type"] == "genres"


def test_genres_batch_no_ids_lists_all(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/genres")
    assert status == 200
    assert sorted(x["id"] for x in body["data"]) == ["20"]


def test_recommendations_batch_no_ids_lists_all(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/me/recommendations")
    assert status == 200
    assert [x["id"] for x in body["data"]] == ["rec1"]
    assert body["data"][0]["type"] == "personal-recommendation"
    assert "contents" in body["data"][0]["relationships"]


def test_recommendations_batch_with_ids(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/recommendations?ids=rec1"
    )
    assert status == 200
    assert [x["id"] for x in body["data"]] == ["rec1"]


def test_record_label_singular_endpoint(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/record-labels/rl1"
    )
    assert status == 200
    assert body["data"][0]["type"] == "record-labels"
    assert body["data"][0]["id"] == "rl1"
    assert body["data"][0]["attributes"]["name"] == "Indie"


def test_record_labels_batch_with_ids(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/record-labels?ids=rl1",
    )
    assert status == 200
    assert [x["id"] for x in body["data"]] == ["rl1"]


def test_record_labels_batch_no_ids_lists_all(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/record-labels")
    assert status == 200
    assert sorted(x["id"] for x in body["data"]) == ["rl1"]
