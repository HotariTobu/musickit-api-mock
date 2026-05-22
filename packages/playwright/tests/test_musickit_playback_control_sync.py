"""Playback-control E2E tests.

These exercise state-machine paths that depend on the underlying audio
element actually fetching HLS segments and progressing through playback:
pause → resume, seek mid-playback, stop during playback, jump to a non-
adjacent queue index.

Sister module: ``test_musickit_playback_control_async.py`` (async API).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.helpers import make_playback_ready_mock
from tests.scenarios_musickit import (
    AUTHORIZE,
    JUMP_DURING_PLAYBACK,
    LOAD_AND_CONFIGURE,
    PAUSE_AND_RESUME,
    SEEK_TO_TIME,
    STOP_DURING_PLAYBACK,
    assert_jumped_to,
    assert_paused_and_resumed,
    assert_seeked_to,
    assert_stopped,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from musickit_api_mock import Song
    from playwright.sync_api import Page


pytestmark = [
    pytest.mark.sync_test,
    pytest.mark.usefixtures("assert_no_musickit_leaks"),
]


def test_pause_and_resume(
    mount_sync_page: Callable[..., Page],
    page_url: str,
    silence_song: Song,
    browser_name: str,
    dev_token: str,
) -> None:
    mock = make_playback_ready_mock({"s1": silence_song}, browser_name)
    page = mount_sync_page(mock)
    page.goto(page_url)
    page.evaluate(LOAD_AND_CONFIGURE, dev_token)
    page.evaluate(AUTHORIZE)
    assert_paused_and_resumed(page.evaluate(PAUSE_AND_RESUME, "s1"))


def test_seek_to_time_during_playback(
    mount_sync_page: Callable[..., Page],
    page_url: str,
    silence_song: Song,
    browser_name: str,
    dev_token: str,
) -> None:
    target_sec = 10.0
    mock = make_playback_ready_mock({"s1": silence_song}, browser_name)
    page = mount_sync_page(mock)
    page.goto(page_url)
    page.evaluate(LOAD_AND_CONFIGURE, dev_token)
    page.evaluate(AUTHORIZE)
    result = page.evaluate(SEEK_TO_TIME, {"songId": "s1", "targetSec": target_sec})
    assert_seeked_to(result, target_sec)


def test_stop_during_playback(
    mount_sync_page: Callable[..., Page],
    page_url: str,
    silence_song: Song,
    browser_name: str,
    dev_token: str,
) -> None:
    mock = make_playback_ready_mock({"s1": silence_song}, browser_name)
    page = mount_sync_page(mock)
    page.goto(page_url)
    page.evaluate(LOAD_AND_CONFIGURE, dev_token)
    page.evaluate(AUTHORIZE)
    assert_stopped(page.evaluate(STOP_DURING_PLAYBACK, "s1"))


def test_jump_to_non_adjacent_index(
    mount_sync_page: Callable[..., Page],
    page_url: str,
    silence_song: Song,
    browser_name: str,
    dev_token: str,
) -> None:
    mock = make_playback_ready_mock(
        {"s1": silence_song, "s2": silence_song, "s3": silence_song},
        browser_name,
    )
    page = mount_sync_page(mock)
    page.goto(page_url)
    page.evaluate(LOAD_AND_CONFIGURE, dev_token)
    page.evaluate(AUTHORIZE)
    result = page.evaluate(
        JUMP_DURING_PLAYBACK,
        {"songIds": ["s1", "s2", "s3"], "targetIndex": 2},
    )
    assert_jumped_to(result, "s3")
