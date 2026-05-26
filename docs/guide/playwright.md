# Playwright integration

The Playwright adapter exposes two entry points — one for the sync API, one for the async API. Both accept either a `Page` or a `BrowserContext`.

## Sync

```python
from musickit_api_mock_playwright import intercept
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    browser = pw.chromium.launch()
    page = browser.new_page()
    intercept(mock, page)
    page.goto("https://your-app.example/")
```

## Async

```python
from musickit_api_mock_playwright import intercept_async
from playwright.async_api import async_playwright

async with async_playwright() as pw:
    browser = await pw.chromium.launch()
    page = await browser.new_page()
    await intercept_async(mock, page)
    await page.goto("https://your-app.example/")
```

## Page vs. BrowserContext

| Target | Effect |
|---|---|
| `Page` | Binds to that single page only. Popups and pages opened later are **not** intercepted. |
| `BrowserContext` | Covers every page in the context, including popups and pages opened later. |

Use `BrowserContext` when:

- Your test opens multiple pages.
- Your app opens real popups via `window.open` for non-MusicKit URLs (e.g. external OAuth providers).
- You want one configuration to apply to many pages in one test.

Use `Page` when:

- You're testing a single isolated page and want strict scoping.

## What the adapter actually does

`intercept` and `intercept_async` do two things:

1. **Register HTTP interception** via `page.route` (or `context.route`) for hosts the mock claims as in-scope.
2. **Inject the in-page JS shim** via `add_init_script`, which replaces MusicKit JS's browser integrations (EME, Media Source, authorize popup) so the page can run end-to-end without real Apple Music infrastructure.

If you write your own adapter for a different framework (Selenium, Puppeteer, raw CDP, ...), use the core package directly — the engine itself is transport-agnostic.

## Supported browsers

All three Playwright browsers are supported: **Chromium, Firefox, WebKit**. The in-page shim accounts for the runtime differences between them (e.g. WebKit's FairPlay vs. other browsers' Widevine).
