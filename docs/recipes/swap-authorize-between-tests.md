# Switch the in-page authorize response between tests

`mock.browser.authorize_response` accepts either a static response variant or a zero-argument callable. The shim re-reads the field every time the page opens an authorize popup, so re-assigning it between tests changes what the next popup resolves to — no need to re-create the page or rerun `intercept(...)`.

## Static swap

```python
from musickit_api_mock import (
    AuthorizeDecline,
    AuthorizeSuccess,
    MusicKitApiMock,
)

mock = MusicKitApiMock()


def test_accepts(page):
    mock.browser.authorize_response = AuthorizeSuccess(
        user_token="t",
        cid="c",
    )
    page.goto(...)
    # Authorize popup resolves to success.


def test_declines(page):
    mock.browser.authorize_response = AuthorizeDecline()
    page.goto(...)
    # Authorize popup resolves to a user-declined result.
```

## Per-popup variation with a callable

When one test opens the popup multiple times, set a callable so each open can return a different result:

```python
results = iter([
    AuthorizeClose(),       # user dismisses the first prompt
    AuthorizeSuccess(user_token="t", cid="c"),  # accepts on retry
])

mock.browser.authorize_response = lambda: next(results)
```

The callable is invoked once per authorize popup. Raising from it surfaces as a failed authorize attempt in the page.

## Variant menu

The authorize response union mirrors every result Apple's authorize service can deliver:

- `AuthorizeSuccess(user_token, cid, restricted=None)` — accepted, with the token MusicKit JS stores.
- `AuthorizeDecline` — user declined.
- `AuthorizeClose` — user closed the prompt without choosing.
- `AuthorizeSwitchUserId` — user switched Apple ID mid-flow; MusicKit JS retries.
- `AuthorizeUnavailable` — the authorize flow is not available.

Pick the variant that drives the page-side code path under test.
