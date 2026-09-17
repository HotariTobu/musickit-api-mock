"""Uploaded library song playback E2E test (sync API).

An uploaded library song has no catalog counterpart: MusicKit posts the
library id to web-playback and plays the raw audio file the response
points at, with no DRM chain.

Sister module: ``test_musickit_upload_async.py`` (async API).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from musickit_api_mock import (
    Artwork,
    UploadedLibrarySong,
    UploadedLibrarySongMetadataFallback,
    WebPlaybackResponseSuccess,
    WebPlaybackUploadedLibraryAsset,
    WebPlaybackUploadedLibraryAssetMetadata,
    WebPlaybackUploadedLibrarySong,
)

from tests.helpers import make_uploaded_playback_ready_mock
from tests.scenarios_musickit import (
    AUTHORIZE,
    LOAD_AND_CONFIGURE,
    PLAY_AND_AWAIT_ERROR,
    PLAY_UPLOAD_AND_AWAIT_PLAYING,
    assert_reached_playing_from_upload,
    assert_upload_playback_failed,
    assert_uploaded_audio_served,
    is_uploaded_audio_response,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from playwright.sync_api import Page


pytestmark = [
    pytest.mark.sync_test,
    pytest.mark.usefixtures("assert_no_musickit_leaks"),
]


def _uploaded_song(silence_audio_path: Path, page_url: str) -> UploadedLibrarySong:
    return UploadedLibrarySong.from_file(
        str(silence_audio_path),
        UploadedLibrarySongMetadataFallback(
            name="Upload",
            artist_name="Uploader",
            artwork=Artwork(url=f"{page_url}a.jpg", width=64, height=64),
            genre_names=[],
            has_lyrics=False,
        ),
    )


def test_uploaded_library_song_plays_from_raw_audio(
    mount_sync_page: Callable[..., Page],
    page_url: str,
    silence_audio_path: Path,
    browser_name: str,
    dev_token: str,
) -> None:
    song = _uploaded_song(silence_audio_path, page_url)
    mock = make_uploaded_playback_ready_mock({"i.upload1": song}, browser_name)
    page = mount_sync_page(mock)
    page.goto(page_url)
    page.evaluate(LOAD_AND_CONFIGURE, dev_token)
    page.evaluate(AUTHORIZE)
    with page.expect_response(
        lambda r: is_uploaded_audio_response(r.url) and r.status != 0, timeout=30000
    ) as audio:
        assert_reached_playing_from_upload(
            page.evaluate(PLAY_UPLOAD_AND_AWAIT_PLAYING, "i.upload1")
        )
    assert_uploaded_audio_served(
        audio.value.status, audio.value.headers.get("content-type")
    )


def test_uploaded_library_song_with_unserved_audio_fails_playback(
    mount_sync_page: Callable[..., Page],
    page_url: str,
    silence_audio_path: Path,
    browser_name: str,
    dev_token: str,
) -> None:
    song = _uploaded_song(silence_audio_path, page_url)
    mock = make_uploaded_playback_ready_mock({"i.upload1": song}, browser_name)
    mock.endpoints.web_playback = {
        "i.upload1": WebPlaybackResponseSuccess(
            song_list=[
                WebPlaybackUploadedLibrarySong(
                    asset=WebPlaybackUploadedLibraryAsset(
                        url="https://store-001.blobstore.apple.com/uploads/i.missing/audio",
                        metadata=WebPlaybackUploadedLibraryAssetMetadata(
                            item_name=song.name,
                            artist_name=song.artist_name,
                            playlist_name="",
                            duration=song.duration_ms,
                            kind="song",
                        ),
                    )
                )
            ]
        )
    }
    page = mount_sync_page(mock)
    page.goto(page_url)
    page.evaluate(LOAD_AND_CONFIGURE, dev_token)
    page.evaluate(AUTHORIZE)
    assert_upload_playback_failed(page.evaluate(PLAY_AND_AWAIT_ERROR, "i.upload1"))
