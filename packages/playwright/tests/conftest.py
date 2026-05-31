from __future__ import annotations

import socketserver
import threading
from http.server import BaseHTTPRequestHandler
from typing import TYPE_CHECKING
from urllib.parse import urlparse

import pytest
from musickit_api_mock import (
    Artwork,
    Song,
    SongMetadataFallback,
)
from musickit_api_mock_playwright import intercept, intercept_async
from playwright.sync_api import sync_playwright

from tests.constants import MUSICKIT_JS_URL
from tests.helpers import build_silence_m4a, make_test_jwt

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
    from pathlib import Path

    from musickit_api_mock import MusicKitApiMock, Request
    from playwright.async_api import Browser as AsyncBrowser
    from playwright.async_api import Page as AsyncPage
    from playwright.async_api import Route as AsyncRoute
    from playwright.sync_api import Browser as SyncBrowser
    from playwright.sync_api import Page as SyncPage
    from playwright.sync_api import Route as SyncRoute


_ALLOWED_HOSTS = frozenset(
    {
        "127.0.0.1",
        "localhost",
        "::1",
    }
)


def _is_allowed(url: str) -> bool:
    return urlparse(url).hostname in _ALLOWED_HOSTS


@pytest.fixture(scope="session")
def _musickit_js_cache() -> dict[str, bytes]:
    return {}


class _BlankHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(
            b"<!DOCTYPE html><html><head><meta charset='utf-8'></head><body></body></html>"
        )

    def log_message(self, *_args: object, **_kwargs: object) -> None:
        return None


@pytest.fixture(scope="session")
def page_url() -> Iterator[str]:
    server = socketserver.TCPServer(("127.0.0.1", 0), _BlankHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}/"
    finally:
        server.shutdown()
        server.server_close()


@pytest.fixture(scope="session")
def silence_audio_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    p = tmp_path_factory.mktemp("silence") / "silence.m4a"
    # 30 sec is long enough for webkit to keep the player in state=2 across
    # the time window pause/resume + skipToNextItem tests need to act in.
    # The default 2 sec lets webkit roll past completion before the test's
    # next interaction lands, masking the player-state behavior under test.
    build_silence_m4a(p, duration_sec=30.0)
    return p


@pytest.fixture(scope="session")
def short_silence_audio_path(tmp_path_factory: pytest.TempPathFactory) -> Path:
    p = tmp_path_factory.mktemp("silence_short") / "silence_short.m4a"
    # Sized to cross the end boundary quickly so a loop iteration completes
    # within the test window — the inverse of silence_audio_path, which is
    # sized to avoid completion.
    build_silence_m4a(p, duration_sec=4.0)
    return p


@pytest.fixture(scope="session")
def dev_token() -> str:
    return make_test_jwt()


def _silence_fallback(page_url: str) -> SongMetadataFallback:
    return SongMetadataFallback(
        artwork=Artwork(url=f"{page_url}a.jpg", width=64, height=64),
        has_lyrics=False,
        audio_locale="en-US",
        audio_traits=["lossless"],
        has_time_synced_lyrics=False,
        is_apple_digital_master=False,
        is_mastered_for_itunes=False,
        is_vocal_attenuation_allowed=False,
        url="https://music.apple.com/us/song/s1",
        title="Silence",
        artist="Test Artist",
        album="Test Album",
        genres=["Test"],
        release_date="2020-01-01",
        track_number=1,
        disc_number=1,
    )


@pytest.fixture
def silence_song(silence_audio_path: Path, page_url: str) -> Song:
    return Song.from_file(str(silence_audio_path), _silence_fallback(page_url))


@pytest.fixture
def short_silence_song(short_silence_audio_path: Path, page_url: str) -> Song:
    return Song.from_file(str(short_silence_audio_path), _silence_fallback(page_url))


@pytest.fixture
async def mount_async_page(
    browser: AsyncBrowser,
    _musickit_js_cache: dict[str, bytes],
) -> AsyncIterator[Callable[[MusicKitApiMock], Awaitable[AsyncPage]]]:
    context = await browser.new_context()
    context.set_default_timeout(60_000)
    leaked: list[str] = []

    async def _guard(route: AsyncRoute) -> None:
        url = route.request.url
        if _is_allowed(url):
            await route.fallback()
        else:
            leaked.append(f"{route.request.method} {url}")
            await route.abort()

    async def _serve_musickit(route: AsyncRoute) -> None:
        if "body" not in _musickit_js_cache:
            response = await route.fetch()
            _musickit_js_cache["body"] = await response.body()
        await route.fulfill(
            status=200,
            content_type="application/javascript",
            body=_musickit_js_cache["body"],
        )

    page = await context.new_page()
    await page.route("**/*", _guard)
    await page.route(MUSICKIT_JS_URL, _serve_musickit)

    async def mount(
        mock: MusicKitApiMock,
        pre_intercept: Callable[[AsyncPage], Awaitable[None]] | None = None,
    ) -> AsyncPage:
        if pre_intercept is not None:
            await pre_intercept(page)
        await intercept_async(mock, page)
        return page

    try:
        yield mount
    finally:
        await context.close()
        assert not leaked, f"external requests leaked: {leaked}"


@pytest.fixture(scope="module")
def _sync_browser(
    browser_name: str, browser_type_launch_args: dict[str, object]
) -> Iterator[SyncBrowser]:
    with sync_playwright() as p:
        browser = getattr(p, browser_name).launch(**browser_type_launch_args)
        try:
            yield browser
        finally:
            browser.close()


@pytest.fixture
def mount_sync_page(
    _sync_browser: SyncBrowser,
    _musickit_js_cache: dict[str, bytes],
) -> Iterator[Callable[[MusicKitApiMock], SyncPage]]:
    context = _sync_browser.new_context()
    context.set_default_timeout(60_000)
    leaked: list[str] = []

    def _guard(route: SyncRoute) -> None:
        url = route.request.url
        if _is_allowed(url):
            route.fallback()
        else:
            leaked.append(f"{route.request.method} {url}")
            route.abort()

    def _serve_musickit(route: SyncRoute) -> None:
        if "body" not in _musickit_js_cache:
            response = route.fetch()
            _musickit_js_cache["body"] = response.body()
        route.fulfill(
            status=200,
            content_type="application/javascript",
            body=_musickit_js_cache["body"],
        )

    page = context.new_page()
    page.route("**/*", _guard)
    page.route(MUSICKIT_JS_URL, _serve_musickit)

    def mount(
        mock: MusicKitApiMock,
        pre_intercept: Callable[[SyncPage], None] | None = None,
    ) -> SyncPage:
        if pre_intercept is not None:
            pre_intercept(page)
        intercept(mock, page)
        return page

    try:
        yield mount
    finally:
        context.close()
        assert not leaked, f"external requests leaked: {leaked}"


@pytest.fixture
def assert_no_musickit_leaks(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Enforce the all-intercept guarantee: fail the test if any leak occurs.

    Monkey-patches the mock's musickit-related warning hook so every request
    the mock would have warned about is recorded instead of printed. At fixture
    teardown, the test fails if any request was recorded. Activated via
    ``pytest.mark.usefixtures`` at module level; no test-side call is required.
    """
    captured: list[Request] = []
    monkeypatch.setattr(
        "musickit_api_mock.mock._warn_possibly_musickit_related",
        captured.append,
    )
    yield
    leaks = [f"{r.method} {r.url}" for r in captured]
    assert not leaks, (
        "musickit-related requests leaked (not handled by mock):\n  "
        + "\n  ".join(leaks)
    )
