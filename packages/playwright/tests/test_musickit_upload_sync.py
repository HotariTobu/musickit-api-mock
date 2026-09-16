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
)

from tests.helpers import make_uploaded_playback_ready_mock
from tests.scenarios_musickit import (
    AUTHORIZE,
    LOAD_AND_CONFIGURE,
    PLAY_UPLOAD_AND_AWAIT_PLAYING,
    assert_reached_playing_from_upload,
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


def test_uploaded_library_song_plays_from_raw_audio(
    mount_sync_page: Callable[..., Page],
    page_url: str,
    silence_audio_path: Path,
    browser_name: str,
    dev_token: str,
) -> None:
    song = UploadedLibrarySong.from_file(
        str(silence_audio_path),
        UploadedLibrarySongMetadataFallback(
            name="Upload",
            artist_name="Uploader",
            artwork=Artwork(url=f"{page_url}a.jpg", width=64, height=64),
            genre_names=[],
            has_lyrics=False,
        ),
    )
    mock = make_uploaded_playback_ready_mock({"i.upload1": song}, browser_name)
    page = mount_sync_page(mock)
    page.goto(page_url)
    page.evaluate(LOAD_AND_CONFIGURE, dev_token)
    page.evaluate(AUTHORIZE)
    with page.expect_response(
        lambda r: is_uploaded_audio_response(r.url), timeout=30000
    ) as audio:
        assert_reached_playing_from_upload(
            page.evaluate(PLAY_UPLOAD_AND_AWAIT_PLAYING, "i.upload1")
        )
    assert_uploaded_audio_served(
        audio.value.status, audio.value.headers.get("content-type")
    )
