"""Async Playwright adapter."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from musickit_api_mock_playwright.shared import _to_core_request

if TYPE_CHECKING:
    from musickit_api_mock.mock import MusicKitApiMock
    from playwright.async_api import BrowserContext as AsyncBrowserContext
    from playwright.async_api import Page as AsyncPage
    from playwright.async_api import Route as AsyncRoute


async def intercept_async(
    mock: MusicKitApiMock,
    target: AsyncPage | AsyncBrowserContext,
) -> None:
    """Wire the mock into an async Playwright page or browser context.

    Pass a page to bind to that single page. Pass a browser context to cover
    every page in the context, including popups and pages opened later.
    """
    await target.add_init_script(mock.get_shim_script())
    await target.route("**/*", lambda route: _handle_async(mock, route))


async def _handle_async(mock: MusicKitApiMock, route: AsyncRoute) -> None:
    req = _to_core_request(route.request)
    try:
        resp = mock.handle_request(req)
    except Exception as e:
        # The mock raised (e.g. a setter is unset). Surface the original
        # message to stderr (it would otherwise be lost in the network-level
        # abort) and end the request as a network failure rather than hanging.
        # Returning any HTTP status here would collide with mock-produced
        # status responses, so abort is the only collision-free choice.
        print(
            f"[musickit-api-mock] handler error: {type(e).__name__}: {e}",
            file=sys.stderr,
        )
        await route.abort()
        return
    if resp is None:
        await route.fallback()
        return
    await route.fulfill(status=resp.status, headers=resp.headers, body=resp.body)
