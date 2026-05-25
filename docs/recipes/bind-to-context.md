# Bind one mock to many pages opened in a single browser context

`intercept` / `intercept_async` accept either a `Page` or a `BrowserContext`. A page binding covers only that one page; a context binding covers every page in the context — existing ones and any opened later.

## Sync

```python
from musickit_api_mock import MusicKitApiMock
from musickit_api_mock_playwright import intercept
from playwright.sync_api import sync_playwright

mock = MusicKitApiMock()
# ... configure the mock ...

with sync_playwright() as pw:
    browser = pw.chromium.launch()
    context = browser.new_context()
    intercept(mock, context)

    page = context.new_page()
    page.goto("https://your-app.example/")
```

## Async

```python
from musickit_api_mock_playwright import intercept_async

context = await browser.new_context()
await intercept_async(mock, context)
page = await context.new_page()
```

## Page vs. BrowserContext

`Page` binding is strict-scope: it intercepts only that one page. Choose it when your test drives a single page and you want strict isolation. The in-page shim handles MusicKit JS's authorize flow inside the page that injected it, so authorize works regardless of which binding you choose.

Choose `BrowserContext` binding when your test opens multiple pages, or when your app opens real popups via `window.open` for non-MusicKit URLs (e.g. external OAuth providers) — the shim only stubs MusicKit's authorize URL, other popups become real new pages and need the context binding to be intercepted.

## Sharing config vs. sharing state

Re-using one `MusicKitApiMock` instance across multiple pages shares both the configuration *and* any per-request state the mock holds (e.g. counters inside callable setters). When two pages must run in isolation, build two `MusicKitApiMock()` instances and bind each to its own context.
