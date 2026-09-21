"""Coverage-gap tests for endpoints added in the v0.2 round.

Companion to ``test_new_relationships.py`` (per-endpoint smoke tests):
this file covers behavior axes the smoke tests skip — pagination,
limit-overflow 400 envelope, missing-target None branches, inline
``?include=<rel>`` variants, full attribute shape, and zero-test
endpoints that the smoke pass missed.
"""

from __future__ import annotations

import json
from dataclasses import replace

import pytest
from musickit_api_mock import (
    Artwork,
    CatalogAlbum,
    CatalogArtist,
    CatalogSong,
    Curator,
    Description,
    Genre,
    Grouping,
    LibraryArtist,
    MusicKitApiMock,
    MusicVideo,
    Playlist,
    RecordLabel,
    Request,
    Station,
    UploadedLibraryAlbum,
    UploadedLibraryArtist,
    UploadedLibrarySong,
)

from tests._expected import (
    ALBUM,
    ALBUM_ATTRIBUTES,
    ALBUM_REF,
    ARTIST_ATTRIBUTES,
    ARTIST_REF,
    CURATOR,
    CURATOR_ATTRIBUTES,
    CURATOR_REF,
    ERROR_ID,
    GENRE,
    GENRE_REF,
    GROUPING_REF,
    LIBRARY_ALBUM,
    LIBRARY_ARTIST,
    LIBRARY_MUSIC_VIDEO,
    LIBRARY_MUSIC_VIDEO_ATTRIBUTES,
    LIBRARY_MUSIC_VIDEO_REF,
    LIBRARY_PLAYLIST,
    LIBRARY_PLAYLIST_ATTRIBUTES,
    LIBRARY_PLAYLIST_REF,
    LIBRARY_SONG,
    LIBRARY_SONG_ATTRIBUTES,
    LIBRARY_SONG_REF,
    MUSIC_VIDEO,
    MUSIC_VIDEO_ATTRIBUTES,
    MUSIC_VIDEO_REF,
    NON_APPLE_CURATOR_ATTRIBUTES,
    NON_APPLE_CURATOR_REF,
    PERSONAL_RECOMMENDATION_ATTRIBUTES,
    PERSONAL_RECOMMENDATION_REF,
    PLAYLIST,
    PLAYLIST_ATTRIBUTES,
    PLAYLIST_REF,
    RECORD_LABEL_REF,
    SONG,
    SONG_ATTRIBUTES,
    SONG_REF,
    STATION,
    STATION_ATTRIBUTES,
    STATION_REF,
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

_ARTIST_ALBUMS_RELATIONSHIP = {
    "href": "/v1/catalog/us/artists/ar1/albums",
    "data": [ALBUM_REF],
}

_MUSIC_VIDEO_DEFAULT_RELATIONSHIPS = {
    "albums": {
        "href": "/v1/catalog/us/music-videos/mv1/albums",
        "data": [ALBUM_REF],
    },
    "artists": {
        "href": "/v1/catalog/us/music-videos/mv1/artists",
        "data": [ARTIST_REF],
    },
}

_CURATOR_RELATIONSHIPS = {
    "playlists": {
        "href": "/v1/catalog/us/apple-curators/cu1/playlists",
        "data": [PLAYLIST_REF],
    },
    "grouping": {
        "href": "/v1/catalog/us/apple-curators/cu1/grouping",
        "data": [GROUPING_REF],
    },
}

_NON_APPLE_CURATOR_BODY = {
    "data": [
        {
            **NON_APPLE_CURATOR_REF,
            "attributes": NON_APPLE_CURATOR_ATTRIBUTES,
            "relationships": {
                "playlists": {
                    "href": "/v1/catalog/us/curators/cu2/playlists",
                    "data": [PLAYLIST_REF],
                },
            },
        }
    ]
}

_EMPTY_BODY = {"data": []}

_NOT_FOUND_BODY = {
    "errors": [
        {
            "id": ERROR_ID,
            "title": "Not Found",
            "status": "404",
        }
    ]
}

_RESOURCE_NOT_FOUND_BODY = {
    "errors": [
        {
            "id": ERROR_ID,
            "title": "Resource Not Found",
            "detail": "Resource with requested id was not found",
            "status": "404",
            "code": "40400",
        }
    ]
}

_EMPTY_IDS_BODY = {
    "errors": [
        {
            "id": ERROR_ID,
            "title": "Invalid Parameter Value",
            "detail": "No id(s) supplied in the 'ids' query parameter",
            "status": "400",
            "code": "40005",
            "source": {"parameter": "ids"},
        }
    ]
}


def _invalid_language_tag_body(tag: str) -> dict[str, object]:
    return {
        "errors": [
            {
                "id": ERROR_ID,
                "title": "Invalid Parameter Value",
                "detail": f"Invalid language tag '{tag}'",
                "status": "400",
                "code": "40005",
                "source": {"parameter": "l"},
            }
        ]
    }


def _limit_overflow_body(cap: int, value: int) -> dict[str, object]:
    return {
        "errors": [
            {
                "id": ERROR_ID,
                "title": "Invalid Parameter Value",
                "detail": (
                    f"Value must be an integer less than or equal to {cap}, "
                    f"but was: {value}"
                ),
                "status": "400",
                "code": "40005",
                "source": {"parameter": "limit"},
            }
        ]
    }


def _stub_playlist(playlist_id: str) -> Playlist:
    return Playlist(
        name=playlist_id,
        playlist_type="editorial",
        curator_name="C",
        has_collaboration=False,
        is_chart=False,
        audio_traits=[],
        supports_sing=False,
        url=f"https://music.apple.com/us/playlist/{playlist_id}",
    )


def _expected_stub_playlist(playlist_id: str) -> dict[str, object]:
    return {
        "id": playlist_id,
        "type": "playlists",
        "href": f"/v1/catalog/us/playlists/{playlist_id}",
        "attributes": {
            "name": playlist_id,
            "audioTraits": [],
            "curatorName": "C",
            "hasCollaboration": False,
            "isChart": False,
            "playParams": {"id": playlist_id, "kind": "playlist"},
            "playlistType": "editorial",
            "supportsSing": False,
            "url": f"https://music.apple.com/us/playlist/{playlist_id}",
        },
    }


def _expected_song_clone(song_id: str) -> dict[str, object]:
    """The fixture song stored under another id: play params and preview follow the id."""
    return {
        "id": song_id,
        "type": "songs",
        "href": f"/v1/catalog/us/songs/{song_id}",
        "attributes": {
            **SONG_ATTRIBUTES,
            "playParams": {"id": song_id, "kind": "song"},
            "previews": [
                {"url": f"https://audio-ssl.itunes.apple.com/preview/{song_id}.m4a"}
            ],
        },
    }


def _get(mock: MusicKitApiMock, url: str) -> tuple[int, object]:
    resp = mock.handle_request(Request(method="GET", url=url, headers={}, body=None))
    assert resp is not None
    return resp.status, json.loads(resp.body)


def test_song_music_videos_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/songs/1/music-videos",
    )
    assert status == 200
    assert body == {"data": [MUSIC_VIDEO]}


def test_album_genres_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/albums/a1/genres"
    )
    assert status == 200
    assert body == {"data": [GENRE]}


def test_artist_genres_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/artists/ar1/genres"
    )
    assert status == 200
    assert body == {"data": [GENRE]}


def test_music_video_genres_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/music-videos/mv1/genres",
    )
    assert status == 200
    assert body == {"data": [GENRE]}


def test_non_apple_curator_singular(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/curators/cu2")
    assert status == 200
    assert body == _NON_APPLE_CURATOR_BODY


def test_non_apple_curator_playlists_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/curators/cu2/playlists",
    )
    assert status == 200
    assert body == {"data": [PLAYLIST]}


def test_song_inline_include_station(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/songs/1?include=station",
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **SONG_REF,
                "attributes": SONG_ATTRIBUTES,
                "relationships": {
                    **_SONG_DEFAULT_RELATIONSHIPS,
                    "station": {
                        "href": "/v1/catalog/us/songs/1/station",
                        "data": [STATION],
                    },
                },
            }
        ]
    }


def test_song_inline_include_music_videos(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/songs/1?include=music-videos",
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **SONG_REF,
                "attributes": SONG_ATTRIBUTES,
                "relationships": {
                    **_SONG_DEFAULT_RELATIONSHIPS,
                    "music-videos": {
                        "href": "/v1/catalog/us/songs/1/music-videos",
                        "data": [MUSIC_VIDEO],
                    },
                },
            }
        ]
    }


def test_album_inline_include_genres(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/albums?ids=a1&include=genres",
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
                    "genres": {
                        "href": "/v1/catalog/us/albums/a1/genres",
                        "data": [GENRE],
                    },
                },
            }
        ]
    }


def test_artist_inline_include_genres(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/artists?ids=ar1&include=genres",
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **ARTIST_REF,
                "attributes": ARTIST_ATTRIBUTES,
                "relationships": {
                    "albums": _ARTIST_ALBUMS_RELATIONSHIP,
                    "genres": {
                        "href": "/v1/catalog/us/artists/ar1/genres",
                        "data": [GENRE],
                    },
                },
            }
        ]
    }


def test_artist_inline_include_music_videos(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/artists?ids=ar1&include=music-videos",
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **ARTIST_REF,
                "attributes": ARTIST_ATTRIBUTES,
                "relationships": {
                    "albums": _ARTIST_ALBUMS_RELATIONSHIP,
                    "music-videos": {
                        "href": "/v1/catalog/us/artists/ar1/music-videos",
                        "data": [MUSIC_VIDEO],
                    },
                },
            }
        ]
    }


def test_artist_inline_include_playlists(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/artists?ids=ar1&include=playlists",
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **ARTIST_REF,
                "attributes": ARTIST_ATTRIBUTES,
                "relationships": {
                    "albums": _ARTIST_ALBUMS_RELATIONSHIP,
                    "playlists": {
                        "href": "/v1/catalog/us/artists/ar1/playlists",
                        "data": [PLAYLIST],
                    },
                },
            }
        ]
    }


def test_artist_inline_include_station(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/artists?ids=ar1&include=station",
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **ARTIST_REF,
                "attributes": ARTIST_ATTRIBUTES,
                "relationships": {
                    "albums": _ARTIST_ALBUMS_RELATIONSHIP,
                    "station": {
                        "href": "/v1/catalog/us/artists/ar1/station",
                        "data": [STATION],
                    },
                },
            }
        ]
    }


def test_music_video_inline_include_genres(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/music-videos?ids=mv1&include=genres",
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **MUSIC_VIDEO_REF,
                "attributes": MUSIC_VIDEO_ATTRIBUTES,
                "relationships": {
                    **_MUSIC_VIDEO_DEFAULT_RELATIONSHIPS,
                    "genres": {
                        "href": "/v1/catalog/us/music-videos/mv1/genres",
                        "data": [GENRE],
                    },
                },
            }
        ]
    }


def test_music_video_inline_include_songs(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/music-videos?ids=mv1&include=songs",
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **MUSIC_VIDEO_REF,
                "attributes": MUSIC_VIDEO_ATTRIBUTES,
                "relationships": {
                    **_MUSIC_VIDEO_DEFAULT_RELATIONSHIPS,
                    "songs": {
                        "href": "/v1/catalog/us/music-videos/mv1/songs",
                        "data": [SONG],
                    },
                },
            }
        ]
    }


def test_music_video_inline_include_library(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/music-videos?ids=mv1&include=library",
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **MUSIC_VIDEO_REF,
                "attributes": MUSIC_VIDEO_ATTRIBUTES,
                "relationships": {
                    **_MUSIC_VIDEO_DEFAULT_RELATIONSHIPS,
                    "library": {
                        "href": "/v1/catalog/us/music-videos/mv1/library",
                        "data": [LIBRARY_MUSIC_VIDEO],
                    },
                },
            }
        ]
    }


def test_playlist_inline_include_library(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/playlists?ids=pl1&include=library",
    )
    assert status == 200
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
                    "library": {
                        "href": "/v1/catalog/us/playlists/pl1/library",
                        "data": [LIBRARY_PLAYLIST],
                    },
                },
            }
        ]
    }


def test_library_song_inline_include_artists(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/songs/i.s1?include=artists",
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **LIBRARY_SONG_REF,
                "attributes": LIBRARY_SONG_ATTRIBUTES,
                "relationships": {
                    "artists": {
                        "href": "/v1/me/library/songs/i.s1/artists",
                        "data": [LIBRARY_ARTIST],
                    },
                },
            }
        ]
    }


def test_library_song_inline_include_catalog(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/songs/i.s1?include=catalog",
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **LIBRARY_SONG_REF,
                "attributes": LIBRARY_SONG_ATTRIBUTES,
                "relationships": {
                    "catalog": {
                        "href": "/v1/me/library/songs/i.s1/catalog",
                        "data": [SONG],
                    },
                },
            }
        ]
    }


def test_library_music_video_inline_include_catalog(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/music-videos/i.mv1?include=catalog",
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **LIBRARY_MUSIC_VIDEO_REF,
                "attributes": LIBRARY_MUSIC_VIDEO_ATTRIBUTES,
                "relationships": {
                    "catalog": {
                        "href": "/v1/me/library/music-videos/i.mv1/catalog",
                        "data": [MUSIC_VIDEO],
                    },
                },
            }
        ]
    }


def test_library_playlist_inline_include_catalog(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/playlists/p.pl1?include=catalog",
    )
    assert status == 200
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
                    "catalog": {
                        "href": "/v1/me/library/playlists/p.pl1/catalog",
                        "data": [PLAYLIST],
                    },
                },
            }
        ]
    }


def test_apple_curator_inline_include_playlists(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/apple-curators/cu1?include=playlists",
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **CURATOR_REF,
                "attributes": CURATOR_ATTRIBUTES,
                "relationships": {
                    **_CURATOR_RELATIONSHIPS,
                    "playlists": {
                        "href": "/v1/catalog/us/apple-curators/cu1/playlists",
                        "data": [PLAYLIST],
                    },
                },
            }
        ]
    }


def test_artist_playlists_limit_overflow_returns_400(
    mock: MusicKitApiMock,
) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/artists/ar1/playlists?limit=99",
    )
    assert status == 400
    assert body == _limit_overflow_body(10, 99)


def test_artist_albums_limit_overflow_paginated(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/artists/r.ar1/albums?limit=999",
    )
    assert status == 400
    assert body == _limit_overflow_body(100, 999)


def test_artist_playlists_paginated_with_offset(
    mock: MusicKitApiMock, artist: CatalogArtist
) -> None:
    # 12 playlists, page_size=10 default, offset=10 returns last 2
    pl_ids = [f"pl{i}" for i in range(1, 13)]
    mock.data.playlists = {pid: _stub_playlist(pid) for pid in pl_ids}
    mock.data.artists = {"ar1": replace(artist, playlist_ids=pl_ids)}
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/artists/ar1/playlists?offset=10",
    )
    assert status == 200
    assert body == {
        "data": [_expected_stub_playlist("pl11"), _expected_stub_playlist("pl12")]
    }


def test_artist_playlists_emits_next_link_when_more(
    mock: MusicKitApiMock, artist: CatalogArtist
) -> None:
    pl_ids = [f"pl{i}" for i in range(1, 13)]
    mock.data.playlists = {pid: _stub_playlist(pid) for pid in pl_ids}
    mock.data.artists = {"ar1": replace(artist, playlist_ids=pl_ids)}
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/artists/ar1/playlists",
    )
    assert status == 200
    assert body == {
        "data": [_expected_stub_playlist(pid) for pid in pl_ids[:10]],
        "next": "/v1/catalog/us/artists/ar1/playlists?offset=10",
    }


def test_library_artist_albums_accepts_inline_limit(
    mock: MusicKitApiMock,
) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/artists/r.ar1/albums?limit=50",
    )
    assert status == 200
    assert body == {"data": [LIBRARY_ALBUM]}


def test_song_library_returns_empty_when_library_song_id_is_none(
    mock: MusicKitApiMock, song: CatalogSong
) -> None:
    mock.data.songs = {"1": replace(song, library_song_id=None)}
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs/1/library"
    )
    assert status == 200
    assert body == _EMPTY_BODY


def test_song_station_returns_empty_when_station_id_is_none(
    mock: MusicKitApiMock, song: CatalogSong
) -> None:
    mock.data.songs = {"1": replace(song, station_id=None)}
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs/1/station"
    )
    assert status == 200
    assert body == _EMPTY_BODY


def test_album_library_returns_empty_when_library_album_id_is_none(
    mock: MusicKitApiMock, album: CatalogAlbum
) -> None:
    mock.data.albums = {"a1": replace(album, library_album_id=None)}
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/albums/a1/library"
    )
    assert status == 200
    assert body == _EMPTY_BODY


def test_artist_station_returns_empty_when_station_id_is_none(
    mock: MusicKitApiMock, artist: CatalogArtist
) -> None:
    mock.data.artists = {"ar1": replace(artist, station_id=None)}
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/artists/ar1/station"
    )
    assert status == 200
    assert body == _EMPTY_BODY


def test_music_video_library_returns_empty_when_id_is_none(
    mock: MusicKitApiMock, music_video: MusicVideo
) -> None:
    mock.data.music_videos = {"mv1": replace(music_video, library_music_video_id=None)}
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/music-videos/mv1/library",
    )
    assert status == 200
    assert body == _EMPTY_BODY


def test_station_radio_show_returns_empty_when_id_is_none(
    mock: MusicKitApiMock, station: Station
) -> None:
    mock.data.stations = {"ra.978194965": replace(station, radio_show_id=None)}
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/stations/ra.978194965/radio-show",
    )
    assert status == 200
    assert body == _EMPTY_BODY


def test_apple_curator_grouping_empty_when_grouping_id_is_none(
    mock: MusicKitApiMock, curator: Curator
) -> None:
    mock.data.curators = {"cu1": replace(curator, grouping_id=None), "cu2": curator}
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/apple-curators/cu1/grouping",
    )
    assert status == 200
    assert body == _EMPTY_BODY


def test_library_artist_albums_empty_when_album_ids_none(
    mock: MusicKitApiMock, library_artist: LibraryArtist
) -> None:
    mock.data.library_artists = {"r.ar1": replace(library_artist, album_ids=None)}
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/artists/r.ar1/albums"
    )
    assert status == 200
    assert body == _EMPTY_BODY


def test_library_artist_catalog_404_for_uploaded_artist(
    mock: MusicKitApiMock,
) -> None:
    mock.data.library_artists = {"r.ar1": UploadedLibraryArtist(name="Uploaded")}
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/artists/r.ar1/catalog"
    )
    assert status == 404
    assert body == _NOT_FOUND_BODY


def test_library_album_catalog_404_for_uploaded_album(
    mock: MusicKitApiMock, artwork_library: Artwork
) -> None:
    mock.data.library_albums = {
        "l.a1": UploadedLibraryAlbum(
            name="Uploaded",
            artist_name="Uploaded",
            artwork=artwork_library,
            genre_names=[],
            track_count=1,
        )
    }
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/albums/l.a1/catalog"
    )
    assert status == 404
    assert body == _NOT_FOUND_BODY


def test_library_song_catalog_404_for_uploaded_song(
    mock: MusicKitApiMock, artwork_library: Artwork
) -> None:
    mock.data.library_songs = {
        "i.s1": UploadedLibrarySong(
            name="Uploaded",
            artist_name="Uploaded",
            artwork=artwork_library,
            duration_ms=1000,
            genre_names=[],
            has_lyrics=False,
            audio=b"",
            disc_number=0,
            track_number=0,
        )
    }
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/songs/i.s1/catalog"
    )
    assert status == 404
    assert body == _NOT_FOUND_BODY


@pytest.mark.parametrize(
    ("kind", "library_id", "url"),
    [
        ("songs", "i.s1", "https://api.music.apple.com/v1/me/library/songs/i.s1"),
        ("albums", "l.a1", "https://api.music.apple.com/v1/me/library/albums/l.a1"),
        ("artists", "r.ar1", "https://api.music.apple.com/v1/me/library/artists/r.ar1"),
    ],
)
@pytest.mark.parametrize(
    "suffix", ["", "?include=albums", "?include=catalog", "/catalog"]
)
def test_library_catalog_id_without_catalog_entry_raises(
    mock: MusicKitApiMock, kind: str, library_id: str, url: str, suffix: str
) -> None:
    source = getattr(mock.data, f"library_{kind}")
    item = replace(source[library_id], catalog_id="missing")
    setattr(mock.data, f"library_{kind}", {library_id: item})
    with pytest.raises(
        ValueError,
        match=rf"data\.library_{kind}\['{library_id}'\]\.catalog_id 'missing' has no entry in data\.{kind}",
    ):
        _get(mock, url + suffix)


def test_song_genres_empty_when_genre_ids_none(
    mock: MusicKitApiMock, song: CatalogSong
) -> None:
    mock.data.songs = {"1": replace(song, genre_ids=None)}
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs/1/genres"
    )
    assert status == 200
    assert body == _EMPTY_BODY


def test_song_library_missing_parent_song_returns_empty(
    mock: MusicKitApiMock,
) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs/nonexistent/library"
    )
    assert status == 200
    assert body == _EMPTY_BODY


def test_recommendation_singular_missing_returns_empty(
    mock: MusicKitApiMock,
) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/recommendations/nonexistent"
    )
    assert status == 200
    assert body == _EMPTY_BODY


def test_genres_batch_missing_id_filtered_out(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/genres?ids=20,nonexistent",
    )
    assert status == 200
    assert body == {"data": [GENRE]}


def test_genre_attributes_full_shape(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/genres/20")
    assert status == 200
    assert body == {"data": [GENRE]}


def test_genre_attributes_omit_optional_when_none(mock: MusicKitApiMock) -> None:
    mock.data.genres = {"5": Genre(name="X", url="https://music.apple.com/us/genre/5")}
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/genres/5")
    assert status == 200
    assert body == {
        "data": [
            {
                "id": "5",
                "type": "genres",
                "href": "/v1/catalog/us/genres/5",
                "attributes": {
                    "name": "X",
                    "url": "https://music.apple.com/us/genre/5",
                },
            }
        ]
    }


def test_record_label_full_attributes(mock: MusicKitApiMock) -> None:
    art = Artwork(url="https://example.com/rl.jpg", width=400, height=400)
    desc = Description(standard="A great label.", short="A label")
    mock.data.record_labels = {
        "rl1": RecordLabel(
            name="Indie",
            url="https://music.apple.com/us/record-label/rl1",
            artwork=art,
            description=desc,
        )
    }
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/record-labels/rl1"
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **RECORD_LABEL_REF,
                "attributes": {
                    "name": "Indie",
                    "artwork": {
                        "url": "https://example.com/rl.jpg",
                        "width": 400,
                        "height": 400,
                    },
                    "description": {
                        "standard": "A great label.",
                        "short": "A label",
                    },
                    "url": "https://music.apple.com/us/record-label/rl1",
                },
            }
        ]
    }


def test_grouping_with_artwork_emits_artwork(mock: MusicKitApiMock) -> None:
    art = Artwork(url="https://example.com/gp.jpg", width=300, height=300)
    mock.data.groupings = {
        "gp1": Grouping(
            name="Curators",
            url="https://music.apple.com/us/grouping/gp1",
            artwork=art,
        )
    }
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/apple-curators/cu1/grouping",
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **GROUPING_REF,
                "attributes": {
                    "name": "Curators",
                    "artwork": {
                        "url": "https://example.com/gp.jpg",
                        "width": 300,
                        "height": 300,
                    },
                    "url": "https://music.apple.com/us/grouping/gp1",
                },
            }
        ]
    }


def test_curator_attributes_emit_kind_and_short_name(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/apple-curators/cu1"
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **CURATOR_REF,
                "attributes": CURATOR_ATTRIBUTES,
                "relationships": _CURATOR_RELATIONSHIPS,
            }
        ]
    }


def test_non_apple_curator_omits_short_name_and_kind(
    mock: MusicKitApiMock,
) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/curators/cu2")
    assert status == 200
    assert body == _NON_APPLE_CURATOR_BODY


def test_song_library_response_uses_singular_data_shape(
    mock: MusicKitApiMock,
) -> None:
    """Singular cross-rel returns ``{data: [single_item]}`` — 1-entry list, no next/meta."""
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs/1/library"
    )
    assert status == 200
    assert body == {"data": [LIBRARY_SONG]}


def test_paginated_endpoint_has_data_array(mock: MusicKitApiMock) -> None:
    """Paginated rel endpoint returns ``{data: [items], next?: str}`` shape."""
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs/1/genres"
    )
    assert status == 200
    assert body == {"data": [GENRE]}


# F. Locale (?l=) handling for new endpoints


def test_song_library_invalid_language_tag_400(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/songs/1/library?l=invalid-XX",
    )
    assert status == 400
    assert body == _invalid_language_tag_body("invalid-XX")


def test_song_genres_valid_language_tag_passes(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/songs/1/genres?l=ja-JP",
    )
    assert status == 200
    assert body == {"data": [GENRE]}


def test_apple_curator_singular_invalid_language_tag_400(
    mock: MusicKitApiMock,
) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/apple-curators/cu1?l=bogus",
    )
    assert status == 400
    assert body == _invalid_language_tag_body("bogus")


def test_recommendation_singular_invalid_language_tag_400(
    mock: MusicKitApiMock,
) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/recommendations/rec1?l=zz-ZZ-bogus",
    )
    assert status == 400
    assert body == _invalid_language_tag_body("zz-ZZ-bogus")


def test_genres_batch_invalid_language_tag_400(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/genres?l=invalid-XX",
    )
    assert status == 400
    assert body == _invalid_language_tag_body("invalid-XX")


def test_library_song_albums_invalid_language_tag_400(
    mock: MusicKitApiMock,
) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/songs/i.s1/albums?l=invalid-XX",
    )
    assert status == 400
    assert body == _invalid_language_tag_body("invalid-XX")


def test_song_genres_callable_resolver_threads_locale(
    mock: MusicKitApiMock,
) -> None:
    from musickit_api_mock import LookupContext

    seen: list[str | None] = []

    def genre_callable(ctx: LookupContext) -> Genre | None:
        seen.append(ctx.locale)
        if ctx.id != "20":
            return None
        return Genre(name="Pop", url="https://music.apple.com/us/genre/20")

    mock.data.genres = genre_callable
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/songs/1/genres?l=ja-JP",
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **GENRE_REF,
                "attributes": {
                    "name": "Pop",
                    "url": "https://music.apple.com/us/genre/20",
                },
            }
        ]
    }
    assert "ja-JP" in seen


# G. Callable source variant for new resources


def test_genre_singular_works_with_callable_source(
    mock: MusicKitApiMock,
) -> None:
    from musickit_api_mock import LookupContext

    def callable_source(ctx: LookupContext) -> Genre | None:
        if ctx.id != "99":
            return None
        return Genre(name="Jazz", url="https://music.apple.com/us/genre/99")

    mock.data.genres = callable_source
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/genres/99")
    assert status == 200
    assert body == {
        "data": [
            {
                "id": "99",
                "type": "genres",
                "href": "/v1/catalog/us/genres/99",
                "attributes": {
                    "name": "Jazz",
                    "url": "https://music.apple.com/us/genre/99",
                },
            }
        ]
    }


def test_record_label_singular_works_with_callable_source(
    mock: MusicKitApiMock,
) -> None:
    from musickit_api_mock import LookupContext

    def callable_source(ctx: LookupContext) -> RecordLabel | None:
        if ctx.id != "rl99":
            return None
        return RecordLabel(
            name="Big",
            url="https://music.apple.com/us/record-label/rl99",
        )

    mock.data.record_labels = callable_source
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/record-labels/rl99"
    )
    assert status == 200
    assert body == {
        "data": [
            {
                "id": "rl99",
                "type": "record-labels",
                "href": "/v1/catalog/us/record-labels/rl99",
                "attributes": {
                    "name": "Big",
                    "url": "https://music.apple.com/us/record-label/rl99",
                },
            }
        ]
    }


def test_recommendation_singular_works_with_callable_source(
    mock: MusicKitApiMock,
) -> None:
    from musickit_api_mock import LookupContext, PersonalRecommendation

    def callable_source(
        ctx: LookupContext,
    ) -> PersonalRecommendation | None:
        if ctx.id != "rec99":
            return None
        return PersonalRecommendation(
            title="From Callable",
            is_group_recommendation=False,
            kind="music-recommendations",
        )

    mock.data.personal_recommendations = callable_source
    status, body = _get(mock, "https://api.music.apple.com/v1/me/recommendations/rec99")
    assert status == 200
    assert body == {
        "data": [
            {
                "id": "rec99",
                "type": "personal-recommendation",
                "href": "/v1/me/recommendations/rec99",
                "attributes": {
                    "title": {"stringForDisplay": "From Callable"},
                    "isGroupRecommendation": False,
                    "kind": "music-recommendations",
                },
            }
        ]
    }


def test_recommendations_batch_with_callable_source_raises_on_list_all(
    mock: MusicKitApiMock,
) -> None:
    from musickit_api_mock import LookupContext, PersonalRecommendation

    def callable_source(
        _ctx: LookupContext,
    ) -> PersonalRecommendation | None:
        return None

    mock.data.personal_recommendations = callable_source
    with pytest.raises(ValueError, match="callable source"):
        _get(mock, "https://api.music.apple.com/v1/me/recommendations")


def test_genres_batch_with_callable_source_raises_on_list_all(
    mock: MusicKitApiMock,
) -> None:
    from musickit_api_mock import LookupContext

    def callable_source(_ctx: LookupContext) -> Genre | None:
        return None

    mock.data.genres = callable_source
    with pytest.raises(ValueError, match="callable source"):
        _get(mock, "https://api.music.apple.com/v1/catalog/us/genres")


def test_apple_curator_works_with_callable_source(mock: MusicKitApiMock) -> None:
    from musickit_api_mock import LookupContext

    def callable_source(ctx: LookupContext) -> Curator | None:
        if ctx.id != "cu99":
            return None
        return Curator(
            name="From Callable",
            type="apple-curators",
            url="https://music.apple.com/us/curator/from-callable/cu99",
            artwork=Artwork(url="https://example.com/c.jpg", width=300, height=300),
            playlist_ids=["pl1"],
        )

    mock.data.curators = callable_source
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/apple-curators/cu99"
    )
    assert status == 200
    assert body == {
        "data": [
            {
                "id": "cu99",
                "type": "apple-curators",
                "href": "/v1/catalog/us/apple-curators/cu99",
                "attributes": {
                    "name": "From Callable",
                    "artwork": {
                        "url": "https://example.com/c.jpg",
                        "width": 300,
                        "height": 300,
                    },
                    "url": "https://music.apple.com/us/curator/from-callable/cu99",
                },
                "relationships": {
                    "playlists": {
                        "href": "/v1/catalog/us/apple-curators/cu99/playlists",
                        "data": [PLAYLIST_REF],
                    },
                },
            }
        ]
    }


def test_grouping_works_with_callable_source(mock: MusicKitApiMock) -> None:
    from musickit_api_mock import LookupContext

    def grouping_source(ctx: LookupContext) -> Grouping | None:
        if ctx.id != "gp1":
            return None
        return Grouping(
            name="GroupedCallable",
            url="https://music.apple.com/us/grouping/gp1",
        )

    mock.data.groupings = grouping_source
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/apple-curators/cu1/grouping",
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **GROUPING_REF,
                "attributes": {
                    "name": "GroupedCallable",
                    "url": "https://music.apple.com/us/grouping/gp1",
                },
            }
        ]
    }


def test_recommendations_batch_empty_ids_returns_400(
    mock: MusicKitApiMock,
) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/me/recommendations?ids=")
    assert status == 400
    assert body == _EMPTY_IDS_BODY


def test_genres_batch_empty_ids_returns_400(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/genres?ids=")
    assert status == 400
    assert body == _EMPTY_IDS_BODY


def test_record_labels_batch_empty_ids_returns_400(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/record-labels?ids="
    )
    assert status == 400
    assert body == _EMPTY_IDS_BODY


def test_apple_curator_singular_type_mismatch_returns_404(
    mock: MusicKitApiMock,
) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/apple-curators/cu2"
    )
    assert status == 404
    assert body == _RESOURCE_NOT_FOUND_BODY


def test_curator_singular_type_mismatch_returns_404(
    mock: MusicKitApiMock,
) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/curators/cu1")
    assert status == 404
    assert body == _RESOURCE_NOT_FOUND_BODY


def test_apple_curator_singular_missing_id_returns_404(
    mock: MusicKitApiMock,
) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/apple-curators/nonexistent",
    )
    assert status == 404
    assert body == _RESOURCE_NOT_FOUND_BODY


def test_station_singular_bare_emits_no_relationships(
    mock: MusicKitApiMock,
) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/stations/ra.978194965"
    )
    assert status == 200
    assert body == {"data": [STATION]}


def test_station_singular_include_radio_show_emits_relationships_block(
    mock: MusicKitApiMock,
) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/stations/ra.978194965?include=radio-show",
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **STATION_REF,
                "attributes": STATION_ATTRIBUTES,
                "relationships": {
                    "radio-show": {
                        "href": "/v1/catalog/us/stations/ra.978194965/radio-show",
                        "data": [CURATOR],
                    },
                },
            }
        ]
    }


def test_station_singular_include_radio_show_empty_when_show_missing(
    mock: MusicKitApiMock, station: Station
) -> None:
    mock.data.stations = {"ra.978194965": replace(station, radio_show_id=None)}
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/stations/ra.978194965?include=radio-show",
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **STATION_REF,
                "attributes": STATION_ATTRIBUTES,
                "relationships": {
                    "radio-show": {
                        "href": "/v1/catalog/us/stations/ra.978194965/radio-show",
                        "data": [],
                    },
                },
            }
        ]
    }


def test_recommendation_contents_mix_types(mock: MusicKitApiMock) -> None:
    """A single recommendation row can mix content types (probe-confirmed)."""
    from musickit_api_mock import (
        PersonalRecommendation,
        PersonalRecommendationContent,
    )

    mock.data.personal_recommendations = {
        "mixed": PersonalRecommendation(
            title="Recently Played",
            is_group_recommendation=False,
            kind="recently-played",
            contents=[
                PersonalRecommendationContent(type="playlists", id="pl1"),
                PersonalRecommendationContent(type="albums", id="a1"),
                PersonalRecommendationContent(type="stations", id="ra.978194965"),
            ],
        )
    }
    status, body = _get(mock, "https://api.music.apple.com/v1/me/recommendations/mixed")
    assert status == 200
    assert body == {
        "data": [
            {
                "id": "mixed",
                "type": "personal-recommendation",
                "href": "/v1/me/recommendations/mixed",
                "attributes": {
                    "title": {"stringForDisplay": "Recently Played"},
                    "isGroupRecommendation": False,
                    "kind": "recently-played",
                },
                "relationships": {
                    "contents": {
                        "href": "/v1/me/recommendations/mixed/contents",
                        "data": [PLAYLIST, ALBUM, STATION],
                    },
                },
            }
        ]
    }


def test_recommendation_emits_display_attrs(mock: MusicKitApiMock) -> None:
    """display / hasSeeAll / version surface in attributes when set."""
    status, body = _get(mock, "https://api.music.apple.com/v1/me/recommendations/rec1")
    assert status == 200
    assert body == {
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


def test_recommendation_kind_recently_played_accepted(
    mock: MusicKitApiMock,
) -> None:
    """``kind="recently-played"`` is accepted (probe-confirmed value)."""
    from musickit_api_mock import PersonalRecommendation

    mock.data.personal_recommendations = {
        "rec1": PersonalRecommendation(
            title="Recently",
            is_group_recommendation=False,
            kind="recently-played",
        )
    }
    status, body = _get(mock, "https://api.music.apple.com/v1/me/recommendations/rec1")
    assert status == 200
    assert body == {
        "data": [
            {
                **PERSONAL_RECOMMENDATION_REF,
                "attributes": {
                    "title": {"stringForDisplay": "Recently"},
                    "isGroupRecommendation": False,
                    "kind": "recently-played",
                },
            }
        ]
    }


def test_repeated_limit_param_uses_last_value(
    mock: MusicKitApiMock, music_video: MusicVideo, song: CatalogSong
) -> None:
    """Apple applies the last-occurrence value when ``?limit=`` is repeated."""
    mock.data.music_videos = {
        "mv1": replace(music_video, song_ids=["1", "2", "3", "4", "5"]),
    }
    mock.data.songs = {
        sid: replace(song, library_song_id=None) for sid in ["1", "2", "3", "4", "5"]
    }
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/music-videos/mv1/songs?limit=1&limit=3",
    )
    assert status == 200
    assert body == {
        "data": [SONG, _expected_song_clone("2"), _expected_song_clone("3")],
        "next": "/v1/catalog/us/music-videos/mv1/songs?offset=3",
    }
