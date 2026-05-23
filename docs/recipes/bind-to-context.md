# Bind one mock to many pages opened in a single browser context

`intercept` / `intercept_async` accept either a `Page` or a `BrowserContext`. A page binding covers only that one page; a context binding covers every page in the context — existing ones, future ones, and popups MusicKit JS opens during the authorize flow.

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
    # MusicKit JS's authorize popup also runs against the mock,
    # because the popup is a new Page inside the same context.
```

## Async

```python
from musickit_api_mock_playwright import intercept_async

context = await browser.new_context()
await intercept_async(mock, context)
page = await context.new_page()
```

## When to prefer a page binding

`Page` binding is strict-scope: the popup MusicKit JS opens during the authorize flow is a **new page in the same context**, so a page binding will not intercept it. That's the right choice for tests that intentionally exclude popup traffic. Most other cases — and every test that drives the authorize flow — want the context binding.

## Sharing config vs. sharing state

Re-using one `MusicKitApiMock` instance across multiple pages shares both the configuration *and* any per-request state the mock holds (e.g. counters inside callable setters). When two pages must run in isolation, build two `MusicKitApiMock()` instances and bind each to its own context.
