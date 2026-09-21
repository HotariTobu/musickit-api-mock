from __future__ import annotations

import json

from musickit_api_mock import MusicKitApiMock, Request, UploadedLibrarySong

from tests._expected import (
    ALBUM,
    ERROR_ID,
    LIBRARY_ALBUM,
    LIBRARY_ALBUM_ATTRIBUTES,
    LIBRARY_ALBUM_REF,
    LIBRARY_ARTIST,
    LIBRARY_MUSIC_VIDEO,
    LIBRARY_MUSIC_VIDEO_ATTRIBUTES,
    LIBRARY_MUSIC_VIDEO_REF,
    LIBRARY_PLAYLIST_ATTRIBUTES,
    LIBRARY_PLAYLIST_REF,
    LIBRARY_SONG,
    LIBRARY_SONG_ATTRIBUTES,
    LIBRARY_SONG_REF,
    SONG,
)

_LIBRARY_ALBUM_TRACKS_RELATIONSHIP = {
    "href": "/v1/me/library/albums/l.a1/tracks",
    "data": [LIBRARY_SONG],
    "meta": {"total": 1},
}

_LIBRARY_ALBUM_BODY = {
    "data": [
        {
            **LIBRARY_ALBUM_REF,
            "attributes": LIBRARY_ALBUM_ATTRIBUTES,
            "relationships": {"tracks": _LIBRARY_ALBUM_TRACKS_RELATIONSHIP},
        }
    ]
}

_LIBRARY_PLAYLIST_BODY = {
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

_INVALID_LANGUAGE_TAG_BODY = {
    "errors": [
        {
            "id": ERROR_ID,
            "title": "Invalid Parameter Value",
            "detail": "Invalid language tag 'invalid-XX'",
            "status": "400",
            "code": "40005",
            "source": {"parameter": "l"},
        }
    ]
}


def _get(mock: MusicKitApiMock, url: str) -> tuple[int, object]:
    resp = mock.handle_request(Request(method="GET", url=url, headers={}, body=None))
    assert resp is not None
    return resp.status, json.loads(resp.body)


def test_q07_library_songs_batch(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/songs?ids=i.s1"
    )
    assert status == 200
    assert body == {"data": [LIBRARY_SONG]}


def test_q07_trailing_slash_form(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/songs/?ids=i.s1"
    )
    assert status == 200
    assert body == {"data": [LIBRARY_SONG]}


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
    assert body == {
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


def test_q07_library_no_ids_param_400(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/me/library/songs")
    assert status == 400
    assert body == {
        "errors": [
            {
                "id": ERROR_ID,
                "title": "Missing Parameter",
                "detail": "No id(s) supplied on the request",
                "status": "400",
                "code": "40003",
                "source": {"parameter": "ids"},
            }
        ]
    }


def test_q08_dead_path_returns_400(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/library-songs/i.s1"
    )
    assert status == 400
    assert body == {
        "errors": [
            {
                "id": ERROR_ID,
                "title": "Invalid Path Value",
                "detail": "Unknown library resource type 'library-songs'",
                "status": "400",
                "code": "40008",
            }
        ]
    }


def test_q08_prime_singular_path(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/me/library/songs/i.s1")
    assert status == 200
    assert body == {"data": [LIBRARY_SONG]}


def test_q09_library_album_with_tracks(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/albums/l.a1?include=tracks",
    )
    assert status == 200
    assert body == _LIBRARY_ALBUM_BODY


def test_q10_library_playlist_with_tracks(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/playlists/p.pl1?include=tracks&extend=hasCollaboration",
    )
    assert status == 200
    assert body == _LIBRARY_PLAYLIST_BODY


def test_q11_library_artist_minimal(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/me/library/artists/r.ar1")
    assert status == 200
    assert body == {"data": [LIBRARY_ARTIST]}


def test_q12_library_music_video(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/music-videos/i.mv1"
    )
    assert status == 200
    assert body == {"data": [LIBRARY_MUSIC_VIDEO]}


def test_q12_library_music_video_with_relationships(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/music-videos/i.mv1?include=albums,artists",
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **LIBRARY_MUSIC_VIDEO_REF,
                "attributes": LIBRARY_MUSIC_VIDEO_ATTRIBUTES,
                "relationships": {
                    "albums": {
                        "href": "/v1/me/library/music-videos/i.mv1/albums",
                        "data": [LIBRARY_ALBUM],
                    },
                    "artists": {
                        "href": "/v1/me/library/music-videos/i.mv1/artists",
                        "data": [LIBRARY_ARTIST],
                    },
                },
            }
        ]
    }


def test_q09_library_album_include_artists(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/albums/l.a1?include=artists",
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **LIBRARY_ALBUM_REF,
                "attributes": LIBRARY_ALBUM_ATTRIBUTES,
                "relationships": {
                    "tracks": _LIBRARY_ALBUM_TRACKS_RELATIONSHIP,
                    "artists": {
                        "href": "/v1/me/library/albums/l.a1/artists",
                        "data": [LIBRARY_ARTIST],
                    },
                },
            }
        ]
    }


def test_q09_library_album_no_include_artists(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/albums/l.a1",
    )
    assert status == 200
    assert body == _LIBRARY_ALBUM_BODY


def test_library_playlist_extends_has_collaboration(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/playlists/p.pl1?include=tracks&extend=hasCollaboration",
    )
    assert status == 200
    assert body == _LIBRARY_PLAYLIST_BODY


def test_library_playlist_has_collaboration_default(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/playlists/p.pl1?include=tracks"
    )
    assert status == 200
    assert body == _LIBRARY_PLAYLIST_BODY


def test_library_song_include_catalog(mock: MusicKitApiMock) -> None:
    """``?include=catalog`` resolves LibrarySong.catalog_id to the catalog song."""
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


def test_uploaded_library_song_omits_unset_attributes(mock: MusicKitApiMock) -> None:
    mock.data.library_songs = {
        "i.up1": UploadedLibrarySong(
            name="Upload",
            artist_name=None,
            artwork=None,
            duration_ms=1000,
            genre_names=[""],
            has_lyrics=False,
            audio=b"",
            disc_number=0,
            track_number=0,
        )
    }
    status, body = _get(mock, "https://api.music.apple.com/v1/me/library/songs/i.up1")
    assert status == 200
    assert body == {
        "data": [
            {
                "id": "i.up1",
                "type": "library-songs",
                "href": "/v1/me/library/songs/i.up1",
                "attributes": {
                    "name": "Upload",
                    "discNumber": 0,
                    "durationInMillis": 1000,
                    "genreNames": [""],
                    "hasLyrics": False,
                    "playParams": {
                        "id": "i.up1",
                        "kind": "song",
                        "isLibrary": True,
                        "reporting": False,
                    },
                    "trackNumber": 0,
                },
            }
        ]
    }


def test_library_song_no_include_no_catalog(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/me/library/songs/i.s1")
    assert status == 200
    assert body == {"data": [LIBRARY_SONG]}


def test_library_album_include_catalog(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/albums/l.a1?include=catalog",
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **LIBRARY_ALBUM_REF,
                "attributes": LIBRARY_ALBUM_ATTRIBUTES,
                "relationships": {
                    "tracks": _LIBRARY_ALBUM_TRACKS_RELATIONSHIP,
                    "catalog": {
                        "href": "/v1/me/library/albums/l.a1/catalog",
                        "data": [ALBUM],
                    },
                },
            }
        ]
    }


def test_library_invalid_language_tag_400(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/songs?ids=i.s1&l=invalid-XX",
    )
    assert status == 400
    assert body == _INVALID_LANGUAGE_TAG_BODY


def test_library_album_invalid_language_tag_400(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/albums/l.a1?l=invalid-XX",
    )
    assert status == 400
    assert body == _INVALID_LANGUAGE_TAG_BODY


def test_library_album_valid_language_tag_passes(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/albums/l.a1?l=ja-JP",
    )
    assert status == 200
    assert body == _LIBRARY_ALBUM_BODY


def test_library_playlist_invalid_language_tag_400(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/playlists/p.pl1?l=invalid-XX",
    )
    assert status == 400
    assert body == _INVALID_LANGUAGE_TAG_BODY


def test_library_music_video_valid_language_tag_passes(
    mock: MusicKitApiMock,
) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/music-videos/i.mv1?l=en-US",
    )
    assert status == 200
    assert body == {"data": [LIBRARY_MUSIC_VIDEO]}


def test_library_album_tracks_relationship_invalid_language_tag_400(
    mock: MusicKitApiMock,
) -> None:
    """Library relationship endpoints honor ``?l=`` validation too."""
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/albums/l.a1/tracks?l=invalid-XX",
    )
    assert status == 400
    assert body == _INVALID_LANGUAGE_TAG_BODY
