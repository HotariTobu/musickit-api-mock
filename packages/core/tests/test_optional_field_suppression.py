"""Optional-field ``None`` is suppressed from emitted attributes.

The schema layer runs every attribute dict through ``_strip_none`` so a
``None`` on an optional dataclass field does not surface as a JSON
``null``. Each test pairs a minimal resource (only required fields) with
``assert <key> not in attrs`` for the optional fields, exercising the
strip path uniformly across resource types.

The relationship-block suppression case (``Song.album_ids = None`` →
``relationships.albums`` is absent) is covered alongside in the same
file because the same ``None``-as-absent semantics drives both attribute
strip and relationship omission.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
from musickit_api_mock import (
    Account,
    AccountResponseSuccess,
    Album,
    Artist,
    Artwork,
    HlsChunk,
    HlsLayout,
    LibraryAlbum,
    LibraryArtist,
    LibraryPlaylist,
    LibrarySong,
    MusicKitApiMock,
    Request,
    Song,
    Storefront,
    StorefrontResponseSuccess,
)

if TYPE_CHECKING:
    from tests._apple_response import _AppleResponse


def _get(mock: MusicKitApiMock, url: str) -> _AppleResponse:
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


def _minimal_song() -> Song:
    return Song(
        title="T",
        artist="A",
        album="Al",
        duration_ms=1,
        artwork=Artwork(url="x", width=1, height=1),
        genres=[],
        has_lyrics=False,
        audio_locale="en-US",
        audio_traits=[],
        has_time_synced_lyrics=False,
        is_apple_digital_master=False,
        is_mastered_for_itunes=False,
        is_vocal_attenuation_allowed=False,
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
    )


def test_song_optional_fields_absent_when_none(bare_mock: MusicKitApiMock) -> None:
    bare_mock.data.songs = {"1": _minimal_song()}
    body = _get(bare_mock, "https://api.music.apple.com/v1/catalog/us/songs?ids=1")
    attrs = body["data"][0]["attributes"]
    assert "releaseDate" not in attrs
    assert "trackNumber" not in attrs
    assert "discNumber" not in attrs
    assert "composerName" not in attrs
    assert "isrc" not in attrs
    assert "contentRating" not in attrs


def test_song_relationships_absent_when_ids_none(bare_mock: MusicKitApiMock) -> None:
    """``Song.album_ids = None`` ⇒ ``relationships.albums`` is not emitted."""
    bare_mock.data.songs = {"1": _minimal_song()}
    body = _get(bare_mock, "https://api.music.apple.com/v1/catalog/us/songs/1")
    item = body["data"][0]
    rels = item.get("relationships", {})
    assert "albums" not in rels
    assert "artists" not in rels


def _minimal_album() -> Album:
    return Album(
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
    bare_mock.data.albums = {"a1": _minimal_album()}
    body = _get(bare_mock, "https://api.music.apple.com/v1/catalog/us/albums?ids=a1")
    attrs = body["data"][0]["attributes"]
    assert "releaseDate" not in attrs
    assert "copyright" not in attrs
    assert "recordLabel" not in attrs
    assert "upc" not in attrs
    assert "contentRating" not in attrs
    assert "editorialNotes" not in attrs


def test_album_relationships_absent_when_ids_none(bare_mock: MusicKitApiMock) -> None:
    bare_mock.data.albums = {"a1": _minimal_album()}
    body = _get(bare_mock, "https://api.music.apple.com/v1/catalog/us/albums?ids=a1")
    item = body["data"][0]
    rels = item.get("relationships", {})
    assert "tracks" not in rels
    assert "artists" not in rels


def test_artist_optional_artwork_absent_when_none(bare_mock: MusicKitApiMock) -> None:
    bare_mock.data.artists = {
        "ar1": Artist(name="A", genre_names=[], url="x", artwork=None)
    }
    body = _get(bare_mock, "https://api.music.apple.com/v1/catalog/us/artists?ids=ar1")
    attrs = body["data"][0]["attributes"]
    assert "artwork" not in attrs


def test_artist_relationships_absent_when_album_ids_none(
    bare_mock: MusicKitApiMock,
) -> None:
    bare_mock.data.artists = {
        "ar1": Artist(
            name="A",
            artwork=Artwork(url="x", width=1, height=1),
            genre_names=[],
            url="x",
        )
    }
    body = _get(bare_mock, "https://api.music.apple.com/v1/catalog/us/artists?ids=ar1")
    item = body["data"][0]
    assert "relationships" not in item or "albums" not in item.get("relationships", {})


def test_library_song_optional_fields_absent_when_none(
    bare_mock: MusicKitApiMock,
) -> None:
    """``LibrarySong``'s optional fields default to ``None`` and are stripped."""
    bare_mock.data.library_songs = {
        "i.s1": LibrarySong(
            name="N",
            artist_name="A",
            artwork=Artwork(url="x", width=1, height=1),
            duration_ms=1,
            genre_names=[],
            has_lyrics=False,
        )
    }
    body = _get(bare_mock, "https://api.music.apple.com/v1/me/library/songs/i.s1")
    attrs = body["data"][0]["attributes"]
    # albumName / discNumber / trackNumber / releaseDate are optional on
    # LibrarySong (default None).
    assert "albumName" not in attrs
    assert "discNumber" not in attrs
    assert "trackNumber" not in attrs
    assert "releaseDate" not in attrs


def test_library_album_optional_fields_absent_when_none(
    bare_mock: MusicKitApiMock,
) -> None:
    bare_mock.data.library_albums = {
        "l.a1": LibraryAlbum(
            name="N",
            artist_name="A",
            artwork=Artwork(url="x", width=1, height=1),
            genre_names=[],
            track_count=0,
        )
    }
    body = _get(bare_mock, "https://api.music.apple.com/v1/me/library/albums/l.a1")
    attrs = body["data"][0]["attributes"]
    # dateAdded / releaseDate are optional on LibraryAlbum (default None).
    assert "dateAdded" not in attrs
    assert "releaseDate" not in attrs


def test_library_album_relationships_absent_when_ids_none(
    bare_mock: MusicKitApiMock,
) -> None:
    bare_mock.data.library_albums = {
        "l.a1": LibraryAlbum(
            name="N",
            artist_name="A",
            artwork=Artwork(url="x", width=1, height=1),
            genre_names=[],
            track_count=0,
        )
    }
    # ``include=tracks,artists`` is requested but library_album.{track,artist}_ids
    # are None → no inline relationships.
    body = _get(
        bare_mock,
        "https://api.music.apple.com/v1/me/library/albums/l.a1?include=tracks,artists",
    )
    item = body["data"][0]
    rels = item.get("relationships", {})
    assert "tracks" not in rels
    assert "artists" not in rels


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
    attrs = body["data"][0]["attributes"]
    assert "artwork" not in attrs


def test_library_artist_minimal_emits_only_name(bare_mock: MusicKitApiMock) -> None:
    bare_mock.data.library_artists = {"r.ar1": LibraryArtist(name="A")}
    body = _get(bare_mock, "https://api.music.apple.com/v1/me/library/artists/r.ar1")
    attrs = body["data"][0]["attributes"]
    assert attrs == {"name": "A"}
