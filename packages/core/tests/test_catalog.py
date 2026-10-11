from __future__ import annotations

import json

from musickit_api_mock import CatalogSong, MusicKitApiMock, Request

from tests._expected import (
    ALBUM,
    ALBUM_ATTRIBUTES,
    ALBUM_EDITORIAL_ARTWORK,
    ALBUM_REF,
    ARTIST,
    ARTIST_ATTRIBUTES,
    ARTIST_REF,
    CURATOR,
    CURATOR_REF,
    ERROR_ID,
    MUSIC_VIDEO_ATTRIBUTES,
    MUSIC_VIDEO_REF,
    PLAYLIST_ATTRIBUTES,
    PLAYLIST_REF,
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

_SONG_BODY = {
    "data": [
        {
            **SONG_REF,
            "attributes": SONG_ATTRIBUTES,
            "relationships": _SONG_DEFAULT_RELATIONSHIPS,
        }
    ]
}

_ALBUM_BODY = {
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

_PLAYLIST_BODY = {
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

_JP_ALBUM_BODY = {
    "data": [
        {
            "id": "a1",
            "type": "albums",
            "href": "/v1/catalog/jp/albums/a1",
            "attributes": ALBUM_ATTRIBUTES,
            "relationships": {
                "tracks": {
                    "href": "/v1/catalog/jp/albums/a1/tracks",
                    "data": [
                        {
                            "id": "1",
                            "type": "songs",
                            "href": "/v1/catalog/jp/songs/1",
                            "attributes": SONG_ATTRIBUTES,
                        }
                    ],
                },
                "artists": {
                    "href": "/v1/catalog/jp/albums/a1/artists",
                    "data": [
                        {
                            "id": "ar1",
                            "type": "artists",
                            "href": "/v1/catalog/jp/artists/ar1",
                        }
                    ],
                },
            },
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


def _get(mock: MusicKitApiMock, url: str) -> tuple[int, object]:
    resp = mock.handle_request(Request(method="GET", url=url, headers={}, body=None))
    assert resp is not None
    return resp.status, json.loads(resp.body)


def test_q01_song_batch_valid(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/songs?ids=1")
    assert status == 200
    assert body == _SONG_BODY


def test_q01_missing_id_resolves_to_empty(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/songs?ids=999")
    assert status == 200
    assert body == {"data": []}


def test_q01_mixed_valid_missing(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs?ids=1&ids=999"
    )
    assert status == 200
    assert body == _SONG_BODY


def test_q01_repeat_and_comma_ids_equivalent(mock: MusicKitApiMock) -> None:
    a_status, a_body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs?ids=1&ids=999"
    )
    b_status, b_body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs?ids=1,999"
    )
    assert a_status == b_status == 200
    assert a_body == _SONG_BODY
    assert b_body == _SONG_BODY


def test_q01_dedupe(mock: MusicKitApiMock, song: CatalogSong) -> None:
    mock.data.songs = {"1": song, "2": song}
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs?ids=2,1,2"
    )
    assert status == 200
    assert body == {
        "data": [
            {
                "id": "2",
                "type": "songs",
                "href": "/v1/catalog/us/songs/2",
                "attributes": {
                    **SONG_ATTRIBUTES,
                    "playParams": {"id": "2", "kind": "song"},
                    "previews": [
                        {"url": "https://audio-ssl.itunes.apple.com/preview/2.m4a"}
                    ],
                },
                "relationships": {
                    "albums": {
                        "href": "/v1/catalog/us/songs/2/albums",
                        "data": [ALBUM_REF],
                    },
                    "artists": {
                        "href": "/v1/catalog/us/songs/2/artists",
                        "data": [ARTIST_REF],
                    },
                },
            },
            {
                **SONG_REF,
                "attributes": SONG_ATTRIBUTES,
                "relationships": _SONG_DEFAULT_RELATIONSHIPS,
            },
        ]
    }


def test_q01_empty_ids_400(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/songs?ids=")
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


def test_q01_all_empty_ids_400(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/songs?ids=,,,")
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


def test_q01_no_ids_param_400(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/songs")
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


def test_q02_album_with_relationships(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/albums?ids=a1")
    assert status == 200
    assert body == _ALBUM_BODY


def test_q03_playlist_with_has_collaboration(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/playlists?ids=pl1"
    )
    assert status == 200
    assert body == _PLAYLIST_BODY


def test_q04_artist_with_albums(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/artists?ids=ar1"
    )
    assert status == 200
    assert body == _ARTIST_BODY


def test_q05_music_video_with_relationships(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/music-videos?ids=mv1"
    )
    assert status == 200
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


def test_q06_station(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/stations?ids=ra.978194965"
    )
    assert status == 200
    assert body == {"data": [STATION]}


def test_unsupported_kind_404(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/audio-books?ids=x"
    )
    assert status == 404
    assert body == {"errors": []}


def test_album_tracks_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/albums/a1/tracks"
    )
    assert status == 200
    assert body == {"data": [SONG]}


def test_invalid_language_tag_400(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/jp/albums?ids=a1&l=invalid-XX",
    )
    assert status == 400
    assert body == _invalid_language_tag_body("invalid-XX")


def test_valid_language_tag_passes(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/jp/albums?ids=a1&l=ja-JP",
    )
    assert status == 200
    assert body == _JP_ALBUM_BODY


def test_empty_language_tag_treated_as_absent(mock: MusicKitApiMock) -> None:
    """``?l=`` with empty value matches Apple's silent-absent treatment."""
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/jp/albums?ids=a1&l="
    )
    assert status == 200
    assert body == _JP_ALBUM_BODY


def test_trailing_hyphen_language_tag_passes(mock: MusicKitApiMock) -> None:
    """``?l=ja-`` (trailing hyphen, empty subtag) is silently accepted by Apple."""
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/jp/albums?ids=a1&l=ja-"
    )
    assert status == 200
    assert body == _JP_ALBUM_BODY


def test_three_letter_primary_language_tag_400(mock: MusicKitApiMock) -> None:
    """``?l=jpn`` (3-letter primary) is rejected — Apple whitelists 2-alpha only."""
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/jp/albums?ids=a1&l=jpn"
    )
    assert status == 400
    assert body == _invalid_language_tag_body("jpn")


def test_non_whitelisted_two_alpha_primary_language_tag_400(
    mock: MusicKitApiMock,
) -> None:
    """``?l=ab`` (valid ISO 639-1 but outside Apple's whitelist) is rejected."""
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/jp/albums?ids=a1&l=ab"
    )
    assert status == 400
    assert body == _invalid_language_tag_body("ab")


def test_three_segment_non_whitelisted_primary_language_tag_400(
    mock: MusicKitApiMock,
) -> None:
    """``?l=ab-cd-ef`` is rejected because ``ab`` isn't whitelisted, not for grammar."""
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/jp/albums?ids=a1&l=ab-cd-ef"
    )
    assert status == 400
    assert body == _invalid_language_tag_body("ab-cd-ef")


def test_underscore_language_tag_treated_as_absent(mock: MusicKitApiMock) -> None:
    """``?l=ja_jp`` (underscore) is silently treated as absent by Apple."""
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/jp/albums?ids=a1&l=ja_jp"
    )
    assert status == 200
    assert body == _JP_ALBUM_BODY


def test_uppercase_primary_language_tag_passes(mock: MusicKitApiMock) -> None:
    """Primary subtag whitelist lookup is case-insensitive."""
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/jp/albums?ids=a1&l=JA-JP"
    )
    assert status == 200
    assert body == _JP_ALBUM_BODY


def test_script_subtag_language_tag_passes(mock: MusicKitApiMock) -> None:
    """Subtags after a whitelisted primary pass regardless of shape (script/region/length)."""
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/jp/albums?ids=a1&l=zh-Hans-CN"
    )
    assert status == 200
    assert body == _JP_ALBUM_BODY


def test_song_singular_default_relationships(mock: MusicKitApiMock) -> None:
    """Catalog song singular endpoint emits relationships.albums + .artists by default."""
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/songs/1")
    assert status == 200
    assert body == _SONG_BODY


def test_song_singular_include_composers(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs/1?include=composers"
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **SONG_REF,
                "attributes": SONG_ATTRIBUTES,
                "relationships": {
                    **_SONG_DEFAULT_RELATIONSHIPS,
                    "composers": {
                        "href": "/v1/catalog/us/songs/1/composers",
                        "data": [ARTIST],
                    },
                },
            }
        ]
    }


def test_song_batch_include_albums_deep_emit(mock: MusicKitApiMock) -> None:
    """``?include=albums`` on song output emits full album attrs inline."""
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs?ids=1&include=albums"
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **SONG_REF,
                "attributes": SONG_ATTRIBUTES,
                "relationships": {
                    "albums": {
                        "href": "/v1/catalog/us/songs/1/albums",
                        "data": [ALBUM],
                    },
                    "artists": {
                        "href": "/v1/catalog/us/songs/1/artists",
                        "data": [ARTIST_REF],
                    },
                },
            }
        ]
    }


def test_song_relationship_albums_endpoint(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs/1/albums"
    )
    assert status == 200
    assert body == {"data": [ALBUM]}


def test_song_relationship_artists_endpoint(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs/1/artists"
    )
    assert status == 200
    assert body == _ARTIST_BODY


def test_song_relationship_composers_endpoint(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs/1/composers"
    )
    assert status == 200
    assert body == _ARTIST_BODY


def test_song_relationship_overflow_400(mock: MusicKitApiMock) -> None:
    """``?limit=999`` on /songs/<id>/albums (cap=10) returns 400 envelope."""
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/songs/1/albums?limit=999",
    )
    assert status == 400
    assert body == {
        "errors": [
            {
                "id": ERROR_ID,
                "title": "Invalid Parameter Value",
                "detail": "Value must be an integer less than or equal to 10, but was: 999",
                "status": "400",
                "code": "40005",
                "source": {"parameter": "limit"},
            }
        ]
    }


def test_album_extend_editorial_artwork(mock: MusicKitApiMock) -> None:
    """``?extend=editorialArtwork`` adds CatalogAlbum.editorial_artwork dict to attrs."""
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/albums?ids=a1&extend=editorialArtwork",
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **ALBUM_REF,
                "attributes": {
                    **ALBUM_ATTRIBUTES,
                    "editorialArtwork": ALBUM_EDITORIAL_ARTWORK,
                },
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


def test_album_no_extend_no_editorial_artwork(mock: MusicKitApiMock) -> None:
    """Without ``?extend=``, ``editorialArtwork`` is not emitted."""
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/albums?ids=a1")
    assert status == 200
    assert body == _ALBUM_BODY


def test_playlist_curator_auto_emit_shallow(mock: MusicKitApiMock) -> None:
    """Default catalog playlist response auto-emits relationships.curator (shallow)."""
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/playlists?ids=pl1"
    )
    assert status == 200
    assert body == _PLAYLIST_BODY


def test_playlist_include_curator_deep_emit(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/playlists?ids=pl1&include=curator",
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
                        "data": [CURATOR],
                    },
                },
            }
        ]
    }


def test_inline_limit_tracks_slices_relationships(mock: MusicKitApiMock) -> None:
    """``?limit[tracks]=N`` controls inline relationship slice size."""
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/albums?ids=a1&limit[tracks]=1",
    )
    assert status == 200
    assert body == _ALBUM_BODY


def test_inline_limit_overflow_400(mock: MusicKitApiMock) -> None:
    """``?limit[tracks]=N`` past cap → 400 with source.parameter='limit'."""
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/albums?ids=a1&limit[tracks]=99999",
    )
    assert status == 400
    assert body == {
        "errors": [
            {
                "id": ERROR_ID,
                "title": "Invalid Parameter Value",
                "detail": (
                    "Value must be an integer less than or equal to 300, but was: 99999"
                ),
                "status": "400",
                "code": "40005",
                "source": {"parameter": "limit"},
            }
        ]
    }


def test_inline_limit_zero_400(mock: MusicKitApiMock) -> None:
    """``?limit[tracks]=0`` → 400 with source.parameter='limit[tracks]'."""
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/albums?ids=a1&limit[tracks]=0",
    )
    assert status == 400
    assert body == {
        "errors": [
            {
                "id": ERROR_ID,
                "title": "Invalid Parameter Value",
                "detail": "Value must be an integer greater than or equal to 1",
                "status": "400",
                "code": "40005",
                "source": {"parameter": "limit[tracks]"},
            }
        ]
    }


def test_inline_limit_non_integer_400(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/albums?ids=a1&limit[tracks]=abc",
    )
    assert status == 400
    assert body == {
        "errors": [
            {
                "id": ERROR_ID,
                "title": "Invalid Parameter Value",
                "detail": "Value must be an integer",
                "status": "400",
                "code": "40005",
                "source": {"parameter": "limit[tracks]"},
            }
        ]
    }


def _bare_mock_with_storefront() -> MusicKitApiMock:
    from musickit_api_mock import (
        Account,
        AccountResponseSuccess,
        MusicKitApiMock,
        Storefront,
        StorefrontResponseSuccess,
    )

    m = MusicKitApiMock()
    m.endpoints.storefront = StorefrontResponseSuccess(
        storefront=Storefront(
            id="us",
            name="US",
            default_language_tag="en-US",
            supported_language_tags=["en-US"],
            explicit_content_policy="allowed",
        )
    )
    m.endpoints.account = AccountResponseSuccess(
        account=Account(subscription_active=True, subscription_storefront="us")
    )
    return m


def test_data_songs_callable_resolves_per_id() -> None:
    """``data.songs`` accepts ``Callable[[LookupContext], CatalogSong | None]``."""
    from musickit_api_mock import (
        Artwork,
        CatalogSong,
        HlsChunk,
        HlsLayout,
        LookupContext,
    )

    seen_ids: list[str] = []

    def song_resolver(ctx: LookupContext) -> CatalogSong | None:
        seen_ids.append(ctx.id)
        if ctx.id != "song-x":
            return None
        return CatalogSong(
            title=f"Title for {ctx.id}",
            artist="A",
            album="Al",
            duration_ms=1,
            artwork=Artwork(url="x", width=1, height=1),
            genres=[],
            release_date="2020-01-01",
            track_number=1,
            disc_number=1,
            composer="C",
            isrc="USABC1234567",
            has_lyrics=False,
            is_apple_digital_master=False,
            url="x",
            hls_layout=HlsLayout(
                target_duration_sec=1,
                init_byte_offset=0,
                init_byte_length=0,
                chunks=(HlsChunk(duration_sec=1.0, byte_offset=0, byte_length=0),),
            ),
            hls_segment=b"",
            preview_audio=b"",
            bitrate=1,
            sample_rate=1,
            file_size=1,
            album_ids=None,
            artist_ids=None,
            composer_ids=None,
        )

    m = _bare_mock_with_storefront()
    m.data.songs = song_resolver

    status, body = _get(m, "https://api.music.apple.com/v1/catalog/us/songs?ids=song-x")
    assert status == 200
    assert body == {
        "data": [
            {
                "id": "song-x",
                "type": "songs",
                "href": "/v1/catalog/us/songs/song-x",
                "attributes": {
                    "name": "Title for song-x",
                    "artistName": "A",
                    "albumName": "Al",
                    "artwork": {"url": "x", "width": 1, "height": 1},
                    "durationInMillis": 1,
                    "genreNames": [],
                    "releaseDate": "2020-01-01",
                    "trackNumber": 1,
                    "discNumber": 1,
                    "composerName": "C",
                    "hasLyrics": False,
                    "isAppleDigitalMaster": False,
                    "isrc": "USABC1234567",
                    "playParams": {"id": "song-x", "kind": "song"},
                    "previews": [
                        {"url": "https://audio-ssl.itunes.apple.com/preview/song-x.m4a"}
                    ],
                    "url": "x",
                },
            }
        ]
    }
    assert "song-x" in seen_ids


def test_data_artists_callable_resolves_per_id() -> None:
    """``data.artists`` accepts ``Callable[[LookupContext], CatalogArtist | None]``."""
    from musickit_api_mock import Artwork, CatalogArtist, LookupContext

    def artist_resolver(ctx: LookupContext) -> CatalogArtist | None:
        if ctx.id != "ar-x":
            return None
        return CatalogArtist(
            name=f"Artist {ctx.id}",
            artwork=Artwork(url="x", width=1, height=1),
            genre_names=[],
            url="x",
        )

    m = _bare_mock_with_storefront()
    m.data.artists = artist_resolver

    status, body = _get(m, "https://api.music.apple.com/v1/catalog/us/artists?ids=ar-x")
    assert status == 200
    assert body == {
        "data": [
            {
                "id": "ar-x",
                "type": "artists",
                "href": "/v1/catalog/us/artists/ar-x",
                "attributes": {
                    "name": "Artist ar-x",
                    "artwork": {"url": "x", "width": 1, "height": 1},
                    "genreNames": [],
                    "url": "x",
                },
            }
        ]
    }


def test_locale_callable_resolver_receives_request_locale() -> None:
    """``?l=`` is threaded into ``Callable[[LookupContext], T | None]`` data sources; absent ``?l=`` becomes ``None``."""
    from musickit_api_mock import (
        AccountResponseSuccess,
        Artwork,
        CatalogAlbum,
        LookupContext,
        MusicKitApiMock,
        StorefrontResponseSuccess,
    )

    seen_locales: list[str | None] = []

    def album_resolver(ctx: LookupContext) -> CatalogAlbum | None:
        seen_locales.append(ctx.locale)
        if ctx.id != "a1":
            return None
        name = (
            "Test (en)"
            if ctx.locale is not None and ctx.locale.startswith("en")
            else "Test (default)"
        )
        return CatalogAlbum(
            name=name,
            artist_name="Artist",
            artwork=Artwork(url="x", width=1, height=1),
            genre_names=[],
            track_count=0,
            is_compilation=False,
            is_complete=True,
            is_mastered_for_itunes=False,
            is_single=True,
            is_prerelease=False,
            audio_traits=[],
            url="x",
        )

    def expected_body(name: str) -> dict[str, object]:
        return {
            "data": [
                {
                    "id": "a1",
                    "type": "albums",
                    "href": "/v1/catalog/jp/albums/a1",
                    "attributes": {
                        "name": name,
                        "artistName": "Artist",
                        "artwork": {"url": "x", "width": 1, "height": 1},
                        "audioTraits": [],
                        "genreNames": [],
                        "isCompilation": False,
                        "isComplete": True,
                        "isMasteredForItunes": False,
                        "isPrerelease": False,
                        "isSingle": True,
                        "playParams": {"id": "a1", "kind": "album"},
                        "trackCount": 0,
                        "url": "x",
                    },
                }
            ]
        }

    m = MusicKitApiMock()
    m.data.albums = album_resolver
    m.endpoints.storefront = StorefrontResponseSuccess(
        storefront=__import__("musickit_api_mock").Storefront(
            id="us",
            name="US",
            default_language_tag="en-US",
            supported_language_tags=["en-US"],
            explicit_content_policy="allowed",
        )
    )
    m.endpoints.account = AccountResponseSuccess(
        account=__import__("musickit_api_mock").Account(
            subscription_active=True, subscription_storefront="us"
        )
    )
    status_default, body_default = _get(
        m, "https://api.music.apple.com/v1/catalog/jp/albums?ids=a1"
    )
    status_en, body_en = _get(
        m, "https://api.music.apple.com/v1/catalog/jp/albums?ids=a1&l=en-US"
    )
    assert status_default == 200
    assert status_en == 200
    assert body_default == expected_body("Test (default)")
    assert body_en == expected_body("Test (en)")
    assert seen_locales[0] is None
    assert seen_locales[1] == "en-US"
