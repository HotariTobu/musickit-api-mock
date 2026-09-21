"""Per-resource attribute emit verification.

Each resource (CatalogSong, CatalogAlbum, CatalogArtist, Playlist, MusicVideo, Station, plus
their library counterparts) carries a documented Apple Music API
attribute set. The tests below pin the full response body the schema
layer emits for the conftest fixture of each resource, so a regression in
any one builder surfaces as a single targeted failure rather than only
being caught by the few golden-path tests.

Brittleness: each assertion binds to (a) the Apple-documented attribute
names and (b) the conftest fixture values. Both are stable contract
points: the attribute names are the public API surface MusicKit JS and
user code observe; the fixture values are owned by ``conftest.py`` so
their reuse is intentional.
"""

from __future__ import annotations

import json

from musickit_api_mock import MusicKitApiMock, Request

from tests._expected import (
    ALBUM_ATTRIBUTES,
    ALBUM_REF,
    ARTIST_ATTRIBUTES,
    ARTIST_REF,
    CURATOR_REF,
    LIBRARY_ALBUM_ATTRIBUTES,
    LIBRARY_ALBUM_REF,
    LIBRARY_ARTIST,
    LIBRARY_MUSIC_VIDEO,
    LIBRARY_PLAYLIST_ATTRIBUTES,
    LIBRARY_PLAYLIST_REF,
    LIBRARY_SONG,
    MUSIC_VIDEO_ATTRIBUTES,
    MUSIC_VIDEO_REF,
    PLAYLIST_ATTRIBUTES,
    PLAYLIST_REF,
    SONG,
    SONG_ATTRIBUTES,
    SONG_REF,
    STATION,
)


def _get(mock: MusicKitApiMock, url: str) -> object:
    resp = mock.handle_request(Request(method="GET", url=url, headers={}, body=None))
    assert resp is not None
    assert resp.status == 200
    return json.loads(resp.body)


def test_song_attributes_emit_configured_fields(mock: MusicKitApiMock) -> None:
    body = _get(mock, "https://api.music.apple.com/v1/catalog/us/songs?ids=1")
    assert body == {
        "data": [
            {
                **SONG_REF,
                "attributes": SONG_ATTRIBUTES,
                "relationships": {
                    "albums": {
                        "href": "/v1/catalog/us/songs/1/albums",
                        "data": [ALBUM_REF],
                    },
                    "artists": {
                        "href": "/v1/catalog/us/songs/1/artists",
                        "data": [ARTIST_REF],
                    },
                },
            }
        ]
    }


def test_album_attributes_emit_configured_fields(mock: MusicKitApiMock) -> None:
    body = _get(mock, "https://api.music.apple.com/v1/catalog/us/albums?ids=a1")
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
                },
            }
        ]
    }


def test_artist_attributes_emit_configured_fields(mock: MusicKitApiMock) -> None:
    body = _get(mock, "https://api.music.apple.com/v1/catalog/us/artists?ids=ar1")
    assert body == {
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


def test_playlist_attributes_emit_configured_fields(mock: MusicKitApiMock) -> None:
    body = _get(mock, "https://api.music.apple.com/v1/catalog/us/playlists?ids=pl1")
    assert body == {
        "data": [
            {
                **PLAYLIST_REF,
                "attributes": PLAYLIST_ATTRIBUTES,
                "relationships": {
                    "tracks": {
                        "href": "/v1/catalog/us/playlists/pl1/tracks",
                        "data": [SONG],
                    },
                    "curator": {
                        "href": "/v1/catalog/us/playlists/pl1/curator",
                        "data": [CURATOR_REF],
                    },
                },
            }
        ]
    }


def test_music_video_attributes_emit_configured_fields(mock: MusicKitApiMock) -> None:
    body = _get(mock, "https://api.music.apple.com/v1/catalog/us/music-videos?ids=mv1")
    assert body == {
        "data": [
            {
                **MUSIC_VIDEO_REF,
                "attributes": MUSIC_VIDEO_ATTRIBUTES,
                "relationships": {
                    "albums": {
                        "href": "/v1/catalog/us/music-videos/mv1/albums",
                        "data": [ALBUM_REF],
                    },
                    "artists": {
                        "href": "/v1/catalog/us/music-videos/mv1/artists",
                        "data": [ARTIST_REF],
                    },
                },
            }
        ]
    }


def test_station_attributes_emit_configured_fields(mock: MusicKitApiMock) -> None:
    body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/stations?ids=ra.978194965",
    )
    # has_drm=True surfaces as the documented supportedDrms triple.
    assert body == {"data": [STATION]}


def test_library_song_attributes_emit_configured_fields(mock: MusicKitApiMock) -> None:
    body = _get(mock, "https://api.music.apple.com/v1/me/library/songs/i.s1")
    assert body == {"data": [LIBRARY_SONG]}


def test_library_album_attributes_emit_configured_fields(mock: MusicKitApiMock) -> None:
    body = _get(mock, "https://api.music.apple.com/v1/me/library/albums/l.a1")
    assert body == {
        "data": [
            {
                **LIBRARY_ALBUM_REF,
                "attributes": LIBRARY_ALBUM_ATTRIBUTES,
                "relationships": {
                    "tracks": {
                        "href": "/v1/me/library/albums/l.a1/tracks",
                        "data": [LIBRARY_SONG],
                        "meta": {"total": 1},
                    },
                },
            }
        ]
    }


def test_library_artist_attributes_emit_only_name(mock: MusicKitApiMock) -> None:
    """LibraryArtist's API surface is just ``{name}`` per Apple."""
    body = _get(mock, "https://api.music.apple.com/v1/me/library/artists/r.ar1")
    assert body == {"data": [LIBRARY_ARTIST]}


def test_library_playlist_attributes_emit_configured_fields(
    mock: MusicKitApiMock,
) -> None:
    body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/playlists/p.pl1?include=tracks",
    )
    assert body == {
        "data": [
            {
                **LIBRARY_PLAYLIST_REF,
                "attributes": LIBRARY_PLAYLIST_ATTRIBUTES,
                "relationships": {
                    "tracks": {
                        "href": "/v1/me/library/playlists/p.pl1/tracks",
                        "data": [LIBRARY_SONG],
                        "meta": {"total": 1},
                    },
                },
            }
        ]
    }


def test_library_music_video_attributes_emit_configured_fields(
    mock: MusicKitApiMock,
) -> None:
    body = _get(mock, "https://api.music.apple.com/v1/me/library/music-videos/i.mv1")
    assert body == {"data": [LIBRARY_MUSIC_VIDEO]}
