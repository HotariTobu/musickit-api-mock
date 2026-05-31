"""Single-song repeat (repeatMode = 1) loop E2E test.

Exercises the end-of-media boundary: the player must reach the song's end,
surface ended, and loop back to the start with playback continuing. This is
the only path that depends on the synthetic media element reporting the real
media duration (so an end boundary exists at all) — distinct from the
playback-control tests, which act before completion.

Sister module: ``test_musickit_loop_async.py`` (async API).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.helpers import make_playback_ready_mock
from tests.scenarios_musickit import (
    AUTHORIZE,
    LOAD_AND_CONFIGURE,
    LOOP_SINGLE_SONG,
    assert_looped,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from musickit_api_mock import Song
    from playwright.sync_api import Page


pytestmark = [
    pytest.mark.sync_test,
    pytest.mark.usefixtures("assert_no_musickit_leaks"),
]


def test_single_song_repeat_loops(
    mount_sync_page: Callable[..., Page],
    page_url: str,
    short_silence_song: Song,
    browser_name: str,
    dev_token: str,
) -> None:
    mock = make_playback_ready_mock({"s1": short_silence_song}, browser_name)
    page = mount_sync_page(mock)
    page.goto(page_url)
    page.evaluate(LOAD_AND_CONFIGURE, dev_token)
    page.evaluate(AUTHORIZE)
    assert_looped(page.evaluate(LOOP_SINGLE_SONG, "s1"))
