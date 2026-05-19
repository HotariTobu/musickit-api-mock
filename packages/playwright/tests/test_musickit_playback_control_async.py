"""Async parity for ``test_musickit_playback_control_sync.py``."""

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
    from collections.abc import Awaitable, Callable

    from musickit_api_mock import Song
    from playwright.async_api import Page as AsyncPage


pytestmark = [
    pytest.mark.async_test,
    pytest.mark.usefixtures("assert_no_musickit_leaks"),
]


@pytest.fixture(autouse=True)
def _skip_on_webkit(browser_name: str) -> None:
    if browser_name == "webkit":
        pytest.skip("FairPlay shim limitation; see module docstring of sync sister")


async def test_pause_and_resume(
    mount_async_page: Callable[..., Awaitable[AsyncPage]],
    page_url: str,
    silence_song: Song,
    browser_name: str,
    dev_token: str,
) -> None:
    mock = make_playback_ready_mock({"s1": silence_song}, browser_name)
    page = await mount_async_page(mock)
    await page.goto(page_url)
    await page.evaluate(LOAD_AND_CONFIGURE, dev_token)
    await page.evaluate(AUTHORIZE)
    assert_paused_and_resumed(await page.evaluate(PAUSE_AND_RESUME, "s1"))


async def test_seek_to_time_during_playback(
    mount_async_page: Callable[..., Awaitable[AsyncPage]],
    page_url: str,
    silence_song: Song,
    browser_name: str,
    dev_token: str,
) -> None:
    target_sec = 10.0
    mock = make_playback_ready_mock({"s1": silence_song}, browser_name)
    page = await mount_async_page(mock)
    await page.goto(page_url)
    await page.evaluate(LOAD_AND_CONFIGURE, dev_token)
    await page.evaluate(AUTHORIZE)
    result = await page.evaluate(
        SEEK_TO_TIME, {"songId": "s1", "targetSec": target_sec}
    )
    assert_seeked_to(result, target_sec)


async def test_stop_during_playback(
    mount_async_page: Callable[..., Awaitable[AsyncPage]],
    page_url: str,
    silence_song: Song,
    browser_name: str,
    dev_token: str,
) -> None:
    mock = make_playback_ready_mock({"s1": silence_song}, browser_name)
    page = await mount_async_page(mock)
    await page.goto(page_url)
    await page.evaluate(LOAD_AND_CONFIGURE, dev_token)
    await page.evaluate(AUTHORIZE)
    assert_stopped(await page.evaluate(STOP_DURING_PLAYBACK, "s1"))


async def test_jump_to_non_adjacent_index(
    mount_async_page: Callable[..., Awaitable[AsyncPage]],
    page_url: str,
    silence_song: Song,
    browser_name: str,
    dev_token: str,
) -> None:
    mock = make_playback_ready_mock(
        {"s1": silence_song, "s2": silence_song, "s3": silence_song},
        browser_name,
    )
    page = await mount_async_page(mock)
    await page.goto(page_url)
    await page.evaluate(LOAD_AND_CONFIGURE, dev_token)
    await page.evaluate(AUTHORIZE)
    result = await page.evaluate(
        JUMP_DURING_PLAYBACK,
        {"songIds": ["s1", "s2", "s3"], "targetIndex": 2},
    )
    assert_jumped_to(result, "s3")
