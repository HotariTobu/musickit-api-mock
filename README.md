# musickit-api-mock

Apple Music API mock for [MusicKit JS](https://developer.apple.com/musickit/). Runs as an in-process request interceptor inside browser-automation tests, so the page hits the mock instead of `api.music.apple.com`.

Useful for testing web apps that embed MusicKit JS without depending on Apple's servers, a developer token, or a signed-in Apple Music subscription.

## Packages

This repository is a uv workspace with a thin core / adapter split:

- **`musickit-api-mock`** — transport-agnostic mock engine. Routes HTTP requests, composes Apple Music API response bodies, and ships the in-page JS shim that replaces MusicKit JS's browser integrations.
- **`musickit-api-mock-playwright`** — Playwright host adapter. Bridges the engine to `page.route` for both sync and async Playwright APIs.

## Install

```bash
pip install musickit-api-mock-playwright
```

The Playwright adapter depends on the core package transitively. Install only the core package if you write your own host adapter for a different browser-automation framework.

## Quick start

### Sync Playwright

```python
from musickit_api_mock import (
    MusicKitApiMock,
    Song,
    Storefront,
    StorefrontResponseSuccess,
)
from musickit_api_mock_playwright import intercept
from playwright.sync_api import sync_playwright

mock = MusicKitApiMock()

# Shared resource data: songs keyed by catalog id.
mock.data.songs = {
    "1000000001": Song.from_file("tests/fixtures/silence.m4a"),
}

# Endpoint-level response: storefront resolution.
mock.endpoints.storefront = StorefrontResponseSuccess(
    storefront=Storefront(
        id="us",
        name="United States",
        default_language_tag="en-US",
        supported_language_tags=["en-US"],
        explicit_content_policy="allowed",
    ),
)

with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page()
    intercept(mock, page)
    page.goto("https://your-app.example/")
    # ... drive MusicKit JS through your app and assert ...
    browser.close()
```

### Async Playwright

```python
from musickit_api_mock_playwright import intercept_async

await intercept_async(mock, page)
```

`intercept` and `intercept_async` accept either a `Page` (binds to that single page) or a `BrowserContext` (covers every page in the context, including popups and pages opened later).

## Surfaces

A `MusicKitApiMock` instance exposes three configuration surfaces. The split is load-bearing — each surface has a distinct semantic role:

- **`mock.data.*`** — shared resource sources (songs, albums, playlists, artists, library items, ...). Read by multiple endpoints when composing responses. Each field accepts a `dict[str, T]` keyed by id, or a `Callable[[LookupContext], T]` for dynamic resolution.
- **`mock.endpoints.*`** — per-endpoint response overrides (storefront, account, license, web playback, ...). Each field accepts a response value, a dict keyed by id, or a callable returning a response. Use these to shape the HTTP response itself (status, error variants, ...).
- **`mock.browser.*`** — state consumed by the in-page JS shim, e.g. the authorize response delivered when the page calls `music.authorize()`, and the EME key system flavor the shim should expose.

All fields default to `None`, which is the unset sentinel. Reading an unset field at request time raises `ValueError` — the mock does not invent fallback values for fields you didn't configure.

## Scope

- **Target audience**: third-party developers using the default MusicKit JS configuration, i.e. `MusicKit.configure(...)` without Apple-internal overrides.
- **Intercepted host**: `api.music.apple.com`. Apple's own web-player override hosts (e.g. `amp-api.music.apple.com`) are out of scope.
- **Intercepted paths**: every path the default-config host emits within MusicKit JS's resource set (songs, albums, artists, library-*, me/*, ...). Within an intercepted path, every form the path can accept is handled — not just the subset MusicKit JS happens to send.

## Supported environments

- Python ≥ 3.12
- Playwright (sync and async) on Chromium, Firefox, and WebKit
- Linux, macOS, Windows

## License

[CC0 1.0 Universal](LICENSE.txt) — public domain dedication.
