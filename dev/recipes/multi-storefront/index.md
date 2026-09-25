# Serve different storefronts per test

`mock.endpoints.storefront` is a static setter you re-assign per test. The mock reads the field on every request, so re-assignment after `intercept(...)` takes effect immediately — no need to rebuild the mock or rebind the page.

## One mock, multiple tests

```python
from musickit_api_mock import (
    MusicKitApiMock,
    Storefront,
    StorefrontResponseSuccess,
)


def _storefront(code: str, name: str, language: str) -> StorefrontResponseSuccess:
    return StorefrontResponseSuccess(
        storefront=Storefront(
            id=code,
            name=name,
            default_language_tag=language,
            supported_language_tags=[language],
            explicit_content_policy="allowed",
        ),
    )


mock = MusicKitApiMock()


def test_us_storefront(page):
    mock.endpoints.storefront = _storefront("us", "United States", "en-US")
    # ... drive the page ...


def test_jp_storefront(page):
    mock.endpoints.storefront = _storefront("jp", "Japan", "ja")
    # ... drive the page ...
```

## Decide at request time

When the storefront should depend on something the test computes lazily (e.g. a fixture parameter), pass a zero-argument callable instead of a value:

```python
mock.endpoints.storefront = lambda: _storefront(
    current_country.id,
    current_country.name,
    current_country.language,
)
```

`current_country` is your test's active country — a fixture parameter, dataclass instance, or shared state holding `id` / `name` / `language` attributes. The callable runs on every `/v1/me/storefront` request, so updating `current_country` between requests changes what the page sees on the next fetch.

## Keep account and storefront aligned

`Account.subscription_storefront` and `Storefront.id` are independent fields — the mock does not enforce a relationship. When your app reads both, set them to the same storefront identifier to avoid the page receiving a mismatched pair MusicKit's docs never describe.
