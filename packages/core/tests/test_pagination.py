"""Pagination flow: ``next`` cursor presence + offset traversal.

The test exercises the user-observable contract:

- a ``next`` key appears when the resolved id list exceeds the page size,
- following the offset advances the slice without overlap and without
  losses,
- once all ids have been returned, ``next`` is absent.
"""

from __future__ import annotations

import json

from musickit_api_mock import (
    Artwork,
    CatalogAlbum,
    CatalogSong,
    MusicKitApiMock,
    Request,
)

from tests._expected import ALBUM


def _get(mock: MusicKitApiMock, url: str) -> object:
    resp = mock.handle_request(Request(method="GET", url=url, headers={}, body=None))
    assert resp is not None
    assert resp.status == 200
    return json.loads(resp.body)


def _stub_album(name: str) -> CatalogAlbum:
    return CatalogAlbum(
        name=name,
        artist_name="A",
        artwork=Artwork(url="x", width=1, height=1),
        genre_names=[],
        release_date="2020-01-01",
        track_count=0,
        is_compilation=False,
        is_complete=True,
        is_mastered_for_itunes=False,
        is_single=True,
        is_prerelease=False,
        audio_traits=[],
        url="x",
    )


def _expected_stub_album(album_id: str) -> dict[str, object]:
    return {
        "id": album_id,
        "type": "albums",
        "href": f"/v1/catalog/us/albums/{album_id}",
        "attributes": {
            "name": f"Album {album_id}",
            "artistName": "A",
            "artwork": {"url": "x", "width": 1, "height": 1},
            "audioTraits": [],
            "genreNames": [],
            "isCompilation": False,
            "isComplete": True,
            "isMasteredForItunes": False,
            "isPrerelease": False,
            "isSingle": True,
            "playParams": {"id": album_id, "kind": "album"},
            "releaseDate": "2020-01-01",
            "trackCount": 0,
            "url": "x",
        },
    }


def test_song_albums_pagination_emits_next_when_overflowing(
    mock: MusicKitApiMock, song: CatalogSong
) -> None:
    """``/songs/<id>/albums`` (page_size=10): 11 ids → first page + ``next``."""
    album_ids = [f"a{i}" for i in range(11)]
    mock.data.songs = {
        "1": CatalogSong(
            title=song.title,
            artist=song.artist,
            album=song.album,
            duration_ms=song.duration_ms,
            artwork=song.artwork,
            genres=song.genres,
            release_date=song.release_date,
            track_number=song.track_number,
            disc_number=song.disc_number,
            composer=song.composer,
            isrc=song.isrc,
            has_lyrics=song.has_lyrics,
            is_apple_digital_master=song.is_apple_digital_master,
            url=song.url,
            hls_layout=song.hls_layout,
            hls_segment=song.hls_segment,
            preview_audio=song.preview_audio,
            bitrate=song.bitrate,
            sample_rate=song.sample_rate,
            file_size=song.file_size,
            album_ids=album_ids,
            artist_ids=song.artist_ids,
            composer_ids=song.composer_ids,
        )
    }
    mock.data.albums = lambda ctx: _stub_album(f"Album {ctx.id}")

    body = _get(mock, "https://api.music.apple.com/v1/catalog/us/songs/1/albums")
    assert body == {
        "data": [_expected_stub_album(f"a{i}") for i in range(10)],
        "next": "/v1/catalog/us/songs/1/albums?offset=10",
    }

    body2 = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs/1/albums?offset=10"
    )
    assert body2 == {"data": [_expected_stub_album("a10")]}


def test_song_albums_no_next_when_below_page_size(mock: MusicKitApiMock) -> None:
    """Single-page result has no ``next`` key (fixture: 1 album)."""
    body = _get(mock, "https://api.music.apple.com/v1/catalog/us/songs/1/albums")
    assert body == {"data": [ALBUM]}
