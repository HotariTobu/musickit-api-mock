"""Optional-field ``None`` is suppressed from emitted attributes.

The schema layer runs every attribute dict through ``_strip_none`` so a
``None`` on an optional dataclass field does not surface as a JSON
``null``. Each test pairs a minimal resource (only required fields) with
the full body it emits, so any optional field that stopped being stripped
shows up as an extra key.

The relationship-block suppression case (``CatalogSong.album_ids = None`` →
``relationships.albums`` is absent) is covered alongside in the same
file because the same ``None``-as-absent semantics drives both attribute
strip and relationship omission.
"""

from __future__ import annotations

import json

import pytest
from musickit_api_mock import (
    Account,
    AccountResponseSuccess,
    Artwork,
    CatalogAlbum,
    CatalogArtist,
    CatalogLibraryAlbum,
    CatalogLibraryArtist,
    CatalogLibrarySong,
    CatalogSong,
    HlsChunk,
    HlsLayout,
    LibraryPlaylist,
    MusicKitApiMock,
    Request,
    Storefront,
    StorefrontResponseSuccess,
)

from tests._expected import (
    ALBUM_REF,
    ARTIST_REF,
    LIBRARY_ALBUM_REF,
    LIBRARY_ARTIST_REF,
    LIBRARY_PLAYLIST_REF,
    LIBRARY_SONG_REF,
    SONG_REF,
)

_MINIMAL_ARTWORK = {"url": "x", "width": 1, "height": 1}

_MINIMAL_SONG_BODY = {
    "data": [
        {
            **SONG_REF,
            "attributes": {
                "name": "T",
                "artistName": "A",
                "albumName": "Al",
                "artwork": _MINIMAL_ARTWORK,
                "durationInMillis": 1,
                "genreNames": [],
                "releaseDate": "2020-01-01",
                "trackNumber": 1,
                "discNumber": 1,
                "isrc": "USABC1234567",
                "playParams": {"id": "1", "kind": "song"},
                "previews": [
                    {"url": "https://audio-ssl.itunes.apple.com/preview/1.m4a"}
                ],
            },
        }
    ]
}

_MINIMAL_ALBUM_BODY = {
    "data": [
        {
            **ALBUM_REF,
            "attributes": {
                "name": "Al",
                "artistName": "A",
                "artwork": _MINIMAL_ARTWORK,
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

_MINIMAL_LIBRARY_ALBUM_BODY = {
    "data": [
        {
            **LIBRARY_ALBUM_REF,
            "attributes": {
                "name": "N",
                "artistName": "A",
                "artwork": _MINIMAL_ARTWORK,
                "genreNames": [],
                "playParams": {
                    "id": "l.a1",
                    "kind": "album",
                    "isLibrary": True,
                    "reporting": False,
                    "reportingId": "587fae15d89d3ff1",
                },
                "trackCount": 0,
            },
        }
    ]
}


def _get(mock: MusicKitApiMock, url: str) -> object:
    resp = mock.handle_request(Request(method="GET", url=url, headers={}, body=None))
    assert resp is not None
    assert resp.status == 200
    return json.loads(resp.body)


@pytest.fixture
def bare_mock() -> MusicKitApiMock:
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


def _minimal_song() -> CatalogSong:
    return CatalogSong(
        title="T",
        artist="A",
        album="Al",
        duration_ms=1,
        artwork=Artwork(url="x", width=1, height=1),
        genres=[],
        isrc="USABC1234567",
        track_number=1,
        disc_number=1,
        release_date="2020-01-01",
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
    )


def test_song_optional_fields_absent_when_none(bare_mock: MusicKitApiMock) -> None:
    """hasLyrics / isAppleDigitalMaster / url / composerName / contentRating stay out."""
    bare_mock.data.songs = {"1": _minimal_song()}
    body = _get(bare_mock, "https://api.music.apple.com/v1/catalog/us/songs?ids=1")
    assert body == _MINIMAL_SONG_BODY


def test_song_relationships_absent_when_ids_none(bare_mock: MusicKitApiMock) -> None:
    """``CatalogSong.album_ids = None`` ⇒ ``relationships.albums`` is not emitted."""
    bare_mock.data.songs = {"1": _minimal_song()}
    body = _get(bare_mock, "https://api.music.apple.com/v1/catalog/us/songs/1")
    assert body == _MINIMAL_SONG_BODY


def _minimal_album() -> CatalogAlbum:
    return CatalogAlbum(
        name="Al",
        artist_name="A",
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


def test_album_optional_fields_absent_when_none(bare_mock: MusicKitApiMock) -> None:
    """releaseDate / copyright / recordLabel / upc / contentRating / editorialNotes stay out."""
    bare_mock.data.albums = {"a1": _minimal_album()}
    body = _get(bare_mock, "https://api.music.apple.com/v1/catalog/us/albums?ids=a1")
    assert body == _MINIMAL_ALBUM_BODY


def test_album_relationships_absent_when_ids_none(bare_mock: MusicKitApiMock) -> None:
    bare_mock.data.albums = {"a1": _minimal_album()}
    body = _get(bare_mock, "https://api.music.apple.com/v1/catalog/us/albums?ids=a1")
    assert body == _MINIMAL_ALBUM_BODY


def test_artist_optional_artwork_absent_when_none(bare_mock: MusicKitApiMock) -> None:
    bare_mock.data.artists = {
        "ar1": CatalogArtist(name="A", genre_names=[], url="x", artwork=None)
    }
    body = _get(bare_mock, "https://api.music.apple.com/v1/catalog/us/artists?ids=ar1")
    assert body == {
        "data": [
            {
                **ARTIST_REF,
                "attributes": {"name": "A", "genreNames": [], "url": "x"},
            }
        ]
    }


def test_artist_relationships_absent_when_album_ids_none(
    bare_mock: MusicKitApiMock,
) -> None:
    bare_mock.data.artists = {
        "ar1": CatalogArtist(
            name="A",
            artwork=Artwork(url="x", width=1, height=1),
            genre_names=[],
            url="x",
        )
    }
    body = _get(bare_mock, "https://api.music.apple.com/v1/catalog/us/artists?ids=ar1")
    assert body == {
        "data": [
            {
                **ARTIST_REF,
                "attributes": {
                    "name": "A",
                    "artwork": _MINIMAL_ARTWORK,
                    "genreNames": [],
                    "url": "x",
                },
            }
        ]
    }


def test_library_song_optional_fields_absent_when_none(
    mock: MusicKitApiMock,
) -> None:
    """``LibrarySong``'s optional fields default to ``None`` and are stripped."""
    mock.data.library_songs = {
        "i.s1": CatalogLibrarySong(
            name="N",
            artist_name="A",
            artwork=Artwork(url="x", width=1, height=1),
            duration_ms=1,
            genre_names=[],
            has_lyrics=False,
            catalog_id="1",
        )
    }
    body = _get(mock, "https://api.music.apple.com/v1/me/library/songs/i.s1")
    # albumName / discNumber / trackNumber / releaseDate are optional on
    # LibrarySong (default None).
    assert body == {
        "data": [
            {
                **LIBRARY_SONG_REF,
                "attributes": {
                    "name": "N",
                    "artistName": "A",
                    "artwork": _MINIMAL_ARTWORK,
                    "durationInMillis": 1,
                    "genreNames": [],
                    "hasLyrics": False,
                    "playParams": {
                        "id": "i.s1",
                        "kind": "song",
                        "isLibrary": True,
                        "reporting": True,
                        "reportingId": "1",
                        "catalogId": "1",
                    },
                },
            }
        ]
    }


def _minimal_library_album() -> CatalogLibraryAlbum:
    return CatalogLibraryAlbum(
        name="N",
        artist_name="A",
        artwork=Artwork(url="x", width=1, height=1),
        genre_names=[],
        track_count=0,
        catalog_id="a1",
    )


def test_library_album_optional_fields_absent_when_none(
    mock: MusicKitApiMock,
) -> None:
    """dateAdded / releaseDate are optional on LibraryAlbum (default None)."""
    mock.data.library_albums = {"l.a1": _minimal_library_album()}
    body = _get(mock, "https://api.music.apple.com/v1/me/library/albums/l.a1")
    assert body == _MINIMAL_LIBRARY_ALBUM_BODY


def test_library_album_relationships_absent_when_ids_none(
    mock: MusicKitApiMock,
) -> None:
    mock.data.library_albums = {"l.a1": _minimal_library_album()}
    # ``include=tracks,artists`` is requested but library_album.{track,artist}_ids
    # are None → no inline relationships.
    body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/albums/l.a1?include=tracks,artists",
    )
    assert body == _MINIMAL_LIBRARY_ALBUM_BODY


def test_library_playlist_optional_fields_absent_when_none(
    bare_mock: MusicKitApiMock,
) -> None:
    bare_mock.data.library_playlists = {
        "p.pl1": LibraryPlaylist(
            name="N",
            can_delete=True,
            can_edit=True,
            is_public=False,
            date_added="2024-01-01",
            last_modified_date="2024-01-02",
            has_catalog=False,
            has_collaboration=False,
        )
    }
    body = _get(bare_mock, "https://api.music.apple.com/v1/me/library/playlists/p.pl1")
    assert body == {
        "data": [
            {
                **LIBRARY_PLAYLIST_REF,
                "attributes": {
                    "name": "N",
                    "canDelete": True,
                    "canEdit": True,
                    "isPublic": False,
                    "dateAdded": "2024-01-01",
                    "lastModifiedDate": "2024-01-02",
                    "hasCatalog": False,
                    "hasCollaboration": False,
                    "playParams": {
                        "id": "p.pl1",
                        "kind": "playlist",
                        "isLibrary": True,
                        "reporting": False,
                        "reportingId": "9e55d62727073344",
                    },
                },
            }
        ]
    }


def test_library_artist_minimal_emits_only_name(mock: MusicKitApiMock) -> None:
    mock.data.library_artists = {
        "r.ar1": CatalogLibraryArtist(name="A", catalog_id="ar1")
    }
    body = _get(mock, "https://api.music.apple.com/v1/me/library/artists/r.ar1")
    assert body == {"data": [{**LIBRARY_ARTIST_REF, "attributes": {"name": "A"}}]}
