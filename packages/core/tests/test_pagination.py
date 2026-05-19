"""Pagination flow: ``next`` cursor presence + offset traversal.

The test exercises the user-observable contract:

- a ``next`` key appears when the resolved id list exceeds the page size,
- following the offset advances the slice without overlap and without
  losses,
- once all ids have been returned, ``next`` is absent.

Nothing is asserted about the literal ``next`` URL string — that format
is internal — so the test survives URL-shape refactors.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, cast
from urllib.parse import parse_qs, urlparse

from musickit_api_mock import (
    Album,
    Artwork,
    MusicKitApiMock,
    Request,
    Song,
)

if TYPE_CHECKING:
    from tests._apple_response import _AppleResponse


def _get(mock: MusicKitApiMock, url: str) -> _AppleResponse:
    resp = mock.handle_request(Request(method="GET", url=url, headers={}, body=None))
    assert resp is not None
    assert resp.status == 200
    return json.loads(resp.body)


def _stub_album(name: str) -> Album:
    return Album(
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


def test_song_albums_pagination_emits_next_when_overflowing(
    mock: MusicKitApiMock, song: Song
) -> None:
    """``/songs/<id>/albums`` (page_size=10): 11 ids → first page + ``next``."""
    album_ids = [f"a{i}" for i in range(11)]
    songs = cast("dict[str, Song]", mock.data.songs)
    songs["1"] = Song(
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
        has_lyrics=song.has_lyrics,
        audio_locale=song.audio_locale,
        audio_traits=song.audio_traits,
        has_time_synced_lyrics=song.has_time_synced_lyrics,
        is_apple_digital_master=song.is_apple_digital_master,
        is_mastered_for_itunes=song.is_mastered_for_itunes,
        is_vocal_attenuation_allowed=song.is_vocal_attenuation_allowed,
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
    mock.data.albums = lambda ctx: _stub_album(f"Album {ctx.id}")

    body = _get(mock, "https://api.music.apple.com/v1/catalog/us/songs/1/albums")
    assert len(body["data"]) == 10
    assert "next" in body
    page_one_ids = [x["id"] for x in body["data"]]

    parsed = urlparse(body["next"])
    offset = int(parse_qs(parsed.query)["offset"][0])
    body2 = _get(
        mock,
        f"https://api.music.apple.com/v1/catalog/us/songs/1/albums?offset={offset}",
    )
    assert len(body2["data"]) == 1
    assert "next" not in body2
    page_two_ids = [x["id"] for x in body2["data"]]

    assert set(page_one_ids).isdisjoint(page_two_ids)
    assert sorted([*page_one_ids, *page_two_ids]) == sorted(album_ids)


def test_song_albums_no_next_when_below_page_size(mock: MusicKitApiMock) -> None:
    """Single-page result has no ``next`` key (fixture: 1 album)."""
    body = _get(mock, "https://api.music.apple.com/v1/catalog/us/songs/1/albums")
    assert "next" not in body
