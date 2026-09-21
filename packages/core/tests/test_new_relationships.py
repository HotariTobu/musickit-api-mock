"""Smoke tests for relationships and base resources added in the v0.2 round.

Covers: catalog/library cross-rels (songs/library, library-songs/catalog, etc.),
catalog/{songs,albums,artists,music-videos}/genres, album/record-labels,
artist/playlists, music-video/songs, station/radio-show, the apple-curators /
curators / personal-recommendation surfaces, and the apple-curators/grouping
relationship into the groupings resource.
"""

from __future__ import annotations

import json

from musickit_api_mock import MusicKitApiMock, Request

from tests._expected import (
    ALBUM,
    ALBUM_ATTRIBUTES,
    ALBUM_REF,
    ARTIST,
    ARTIST_REF,
    CURATOR,
    CURATOR_ATTRIBUTES,
    CURATOR_REF,
    GENRE,
    GROUPING,
    GROUPING_REF,
    LIBRARY_ALBUM,
    LIBRARY_ARTIST,
    LIBRARY_ARTIST_ATTRIBUTES,
    LIBRARY_ARTIST_REF,
    LIBRARY_MUSIC_VIDEO,
    LIBRARY_PLAYLIST,
    LIBRARY_SONG,
    LIBRARY_SONG_ATTRIBUTES,
    LIBRARY_SONG_REF,
    MUSIC_VIDEO,
    PERSONAL_RECOMMENDATION_ATTRIBUTES,
    PERSONAL_RECOMMENDATION_REF,
    PLAYLIST,
    PLAYLIST_REF,
    RECORD_LABEL,
    SONG,
    SONG_ATTRIBUTES,
    SONG_REF,
    STATION,
)

_SONG_DEFAULT_RELATIONSHIPS = {
    "albums": {
        "href": "/v1/catalog/us/songs/1/albums",
        "data": [ALBUM_REF],
    },
    "artists": {
        "href": "/v1/catalog/us/songs/1/artists",
        "data": [ARTIST_REF],
    },
}

_CURATOR_PLAYLISTS_RELATIONSHIP = {
    "href": "/v1/catalog/us/apple-curators/cu1/playlists",
    "data": [PLAYLIST_REF],
}

_RECOMMENDATION_BODY = {
    "data": [
        {
            **PERSONAL_RECOMMENDATION_REF,
            "attributes": PERSONAL_RECOMMENDATION_ATTRIBUTES,
            "relationships": {
                "contents": {
                    "href": "/v1/me/recommendations/rec1/contents",
                    "data": [PLAYLIST],
                },
            },
        }
    ]
}


def _get(mock: MusicKitApiMock, url: str) -> tuple[int, object]:
    resp = mock.handle_request(Request(method="GET", url=url, headers={}, body=None))
    assert resp is not None
    return resp.status, json.loads(resp.body)


# Phase B: catalog -> library (singular)


def test_catalog_song_library_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs/1/library"
    )
    assert status == 200
    assert body == {"data": [LIBRARY_SONG]}


def test_catalog_album_library_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/albums/a1/library"
    )
    assert status == 200
    assert body == {"data": [LIBRARY_ALBUM]}


def test_catalog_music_video_library_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/music-videos/mv1/library",
    )
    assert status == 200
    assert body == {"data": [LIBRARY_MUSIC_VIDEO]}


def test_catalog_playlist_library_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/playlists/pl1/library"
    )
    assert status == 200
    assert body == {"data": [LIBRARY_PLAYLIST]}


def test_catalog_song_inline_library_include(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/songs/1?include=library",
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **SONG_REF,
                "attributes": SONG_ATTRIBUTES,
                "relationships": {
                    **_SONG_DEFAULT_RELATIONSHIPS,
                    "library": {
                        "href": "/v1/catalog/us/songs/1/library",
                        "data": [LIBRARY_SONG],
                    },
                },
            }
        ]
    }


# Phase B: library -> catalog (singular)


def test_library_song_catalog_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/songs/i.s1/catalog"
    )
    assert status == 200
    assert body == {"data": [SONG]}


def test_library_album_catalog_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/albums/l.a1/catalog"
    )
    assert status == 200
    assert body == {"data": [ALBUM]}


def test_library_music_video_catalog_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/music-videos/i.mv1/catalog",
    )
    assert status == 200
    assert body == {"data": [MUSIC_VIDEO]}


def test_library_playlist_catalog_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/playlists/p.pl1/catalog",
    )
    assert status == 200
    assert body == {"data": [PLAYLIST]}


def test_library_artist_catalog_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/artists/r.ar1/catalog",
    )
    assert status == 200
    assert body == {"data": [ARTIST]}


# Phase B: library -> library (paginated)


def test_library_song_albums_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/songs/i.s1/albums"
    )
    assert status == 200
    assert body == {"data": [LIBRARY_ALBUM]}


def test_library_song_artists_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/songs/i.s1/artists"
    )
    assert status == 200
    assert body == {"data": [LIBRARY_ARTIST]}


def test_library_artist_albums_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/artists/r.ar1/albums"
    )
    assert status == 200
    assert body == {"data": [LIBRARY_ALBUM]}


def test_library_song_inline_include_albums(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/songs/i.s1?include=albums",
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **LIBRARY_SONG_REF,
                "attributes": LIBRARY_SONG_ATTRIBUTES,
                "relationships": {
                    "albums": {
                        "href": "/v1/me/library/songs/i.s1/albums",
                        "data": [LIBRARY_ALBUM],
                    },
                },
            }
        ]
    }


def test_library_artist_inline_include_catalog(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/artists/r.ar1?include=catalog",
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **LIBRARY_ARTIST_REF,
                "attributes": LIBRARY_ARTIST_ATTRIBUTES,
                "relationships": {
                    "catalog": {
                        "href": "/v1/me/library/artists/r.ar1/catalog",
                        "data": [ARTIST],
                    },
                },
            }
        ]
    }


# Phase C: new base resources via relationships


def test_song_genres_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs/1/genres"
    )
    assert status == 200
    assert body == {"data": [GENRE]}


def test_song_genres_inline_include(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs/1?include=genres"
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **SONG_REF,
                "attributes": SONG_ATTRIBUTES,
                "relationships": {
                    **_SONG_DEFAULT_RELATIONSHIPS,
                    "genres": {
                        "href": "/v1/catalog/us/songs/1/genres",
                        "data": [GENRE],
                    },
                },
            }
        ]
    }


def test_album_record_labels_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/albums/a1/record-labels",
    )
    assert status == 200
    assert body == {"data": [RECORD_LABEL]}


def test_album_record_labels_inline_include(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/albums?ids=a1&include=record-labels",
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **ALBUM_REF,
                "attributes": ALBUM_ATTRIBUTES,
                "relationships": {
                    "tracks": {
                        "href": "/v1/catalog/us/albums/a1/tracks",
                        "data": [SONG],
                    },
                    "artists": {
                        "href": "/v1/catalog/us/albums/a1/artists",
                        "data": [ARTIST_REF],
                    },
                    "record-labels": {
                        "href": "/v1/catalog/us/albums/a1/record-labels",
                        "data": [RECORD_LABEL],
                    },
                },
            }
        ]
    }


def test_artist_playlists_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/artists/ar1/playlists"
    )
    assert status == 200
    assert body == {"data": [PLAYLIST]}


def test_artist_station_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/artists/ar1/station"
    )
    assert status == 200
    assert body == {"data": [STATION]}


def test_song_station_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs/1/station"
    )
    assert status == 200
    assert body == {"data": [STATION]}


def test_artist_music_videos_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/artists/ar1/music-videos",
    )
    assert status == 200
    assert body == {"data": [MUSIC_VIDEO]}


def test_music_video_songs_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/music-videos/mv1/songs",
    )
    assert status == 200
    assert body == {"data": [SONG]}


def test_station_radio_show_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/stations/ra.978194965/radio-show",
    )
    assert status == 200
    assert body == {"data": [CURATOR]}


# Phase C: curators (singular base resource + playlists + grouping)


def test_apple_curator_singular(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/apple-curators/cu1",
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **CURATOR_REF,
                "attributes": CURATOR_ATTRIBUTES,
                "relationships": {
                    "playlists": _CURATOR_PLAYLISTS_RELATIONSHIP,
                    "grouping": {
                        "href": "/v1/catalog/us/apple-curators/cu1/grouping",
                        "data": [GROUPING_REF],
                    },
                },
            }
        ]
    }


def test_apple_curator_playlists_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/apple-curators/cu1/playlists",
    )
    assert status == 200
    assert body == {"data": [PLAYLIST]}


def test_apple_curator_grouping_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/apple-curators/cu1/grouping",
    )
    assert status == 200
    assert body == {"data": [GROUPING]}


def test_apple_curator_include_grouping(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/apple-curators/cu1?include=grouping",
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **CURATOR_REF,
                "attributes": CURATOR_ATTRIBUTES,
                "relationships": {
                    "playlists": _CURATOR_PLAYLISTS_RELATIONSHIP,
                    "grouping": {
                        "href": "/v1/catalog/us/apple-curators/cu1/grouping",
                        "data": [GROUPING],
                    },
                },
            }
        ]
    }


# Phase C: personal-recommendation surface


def test_recommendation_singular_default_contents(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/me/recommendations/rec1")
    assert status == 200
    assert body == _RECOMMENDATION_BODY


# Phase A: direct-GET singular base resource + batch list endpoints


def test_genre_singular_endpoint(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/genres/20")
    assert status == 200
    assert body == {"data": [GENRE]}


def test_genres_batch_with_ids(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/genres?ids=20")
    assert status == 200
    assert body == {"data": [GENRE]}


def test_genres_batch_no_ids_lists_all(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/genres")
    assert status == 200
    assert body == {"data": [GENRE]}


def test_recommendations_batch_no_ids_lists_all(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/me/recommendations")
    assert status == 200
    assert body == _RECOMMENDATION_BODY


def test_recommendations_batch_with_ids(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/recommendations?ids=rec1"
    )
    assert status == 200
    assert body == _RECOMMENDATION_BODY


def test_record_label_singular_endpoint(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/record-labels/rl1"
    )
    assert status == 200
    assert body == {"data": [RECORD_LABEL]}


def test_record_labels_batch_with_ids(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/record-labels?ids=rl1",
    )
    assert status == 200
    assert body == {"data": [RECORD_LABEL]}


def test_record_labels_batch_no_ids_lists_all(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/record-labels")
    assert status == 200
    assert body == {"data": [RECORD_LABEL]}
