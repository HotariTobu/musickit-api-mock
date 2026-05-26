# Getting started

## Install

```bash
pip install musickit-api-mock-playwright
```

The Playwright adapter pulls in the core package as a transitive dependency. Install only the core package if you write your own host adapter for a different browser-automation framework:

```bash
pip install musickit-api-mock
```

## Minimum example (sync Playwright)

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
    "1000000001": Song.from_file("path/to/song.m4a"),
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

## Async Playwright

The async API mirrors the sync one — only the adapter call changes:

```python
from musickit_api_mock_playwright import intercept_async

await intercept_async(mock, page)
```

## What's happening?

1. **`MusicKitApiMock()`** creates an in-memory mock with three configuration surfaces (`mock.data`, `mock.endpoints`, `mock.browser`) all unset.
2. **Configure the surfaces** with the resources and responses your test needs. Anything you don't configure stays unset; the mock does not invent fallback values.
3. **`intercept(mock, page)`** wires the mock into Playwright's `page.route` interceptor and injects the in-page JS shim that replaces MusicKit JS's browser integrations (EME, Media Source, authorize popup).
4. When the page calls MusicKit JS APIs, the corresponding HTTP requests hit the mock instead of `api.music.apple.com`.

Continue with [Surfaces overview](surfaces.md) to learn what each surface holds.
