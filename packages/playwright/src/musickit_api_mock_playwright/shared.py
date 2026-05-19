"""Shared helper to convert a Playwright ``Request`` into the core ``Request`` type."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.transport.http import Request

if TYPE_CHECKING:
    from playwright.async_api import Request as AsyncRequest
    from playwright.sync_api import Request as SyncRequest


def _to_core_request(playwright_request: SyncRequest | AsyncRequest) -> Request:
    body: bytes | None = None
    raw = playwright_request.post_data_buffer
    if raw is not None:
        body = bytes(raw)
    elif playwright_request.post_data is not None:
        body = playwright_request.post_data.encode("utf-8")
    headers_dict: dict[str, str] = dict(playwright_request.headers or {})
    return Request(
        method=playwright_request.method,
        url=playwright_request.url,
        headers=headers_dict,
        body=body,
    )
