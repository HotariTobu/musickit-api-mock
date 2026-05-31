"""Async parity for ``test_musickit_loop_sync.py``."""

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
    from collections.abc import Awaitable, Callable

    from musickit_api_mock import Song
    from playwright.async_api import Page as AsyncPage


pytestmark = [
    pytest.mark.async_test,
    pytest.mark.usefixtures("assert_no_musickit_leaks"),
]


async def test_single_song_repeat_loops(
    mount_async_page: Callable[..., Awaitable[AsyncPage]],
    page_url: str,
    short_silence_song: Song,
    browser_name: str,
    dev_token: str,
) -> None:
    mock = make_playback_ready_mock({"s1": short_silence_song}, browser_name)
    page = await mount_async_page(mock)
    await page.goto(page_url)
    await page.evaluate(LOAD_AND_CONFIGURE, dev_token)
    await page.evaluate(AUTHORIZE)
    assert_looped(await page.evaluate(LOOP_SINGLE_SONG, "s1"))
