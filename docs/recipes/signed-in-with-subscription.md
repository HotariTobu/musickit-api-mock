# Simulate a signed-in user with an active subscription

The end-to-end "signed in, paid up" baseline used by almost every other recipe. Three surfaces participate:

- `mock.browser.authorize_response` — what `music.authorize()` resolves to in the page.
- `mock.endpoints.account` — what `/v1/me/account` reports about the user's subscription.
- `mock.endpoints.storefront` — what `/v1/me/storefront` reports as the active storefront.

```python
from musickit_api_mock import (
    Account,
    AccountResponseSuccess,
    AuthorizeSuccess,
    MusicKitApiMock,
    Storefront,
    StorefrontResponseSuccess,
)

mock = MusicKitApiMock()

mock.browser.authorize_response = AuthorizeSuccess(
    user_token="test-user-token",
    cid="test-cid",
)

mock.endpoints.account = AccountResponseSuccess(
    account=Account(
        subscription_active=True,
        subscription_storefront="us",
    ),
)

mock.endpoints.storefront = StorefrontResponseSuccess(
    storefront=Storefront(
        id="us",
        name="United States",
        default_language_tag="en-US",
        supported_language_tags=["en-US"],
        explicit_content_policy="allowed",
    ),
)
```

After `intercept(mock, page)`, the page sees a successful authorize flow, an active subscription, and a resolved storefront — the prerequisites MusicKit JS checks before exposing playback APIs.

!!! tip
    Keep `subscription_storefront` and the `Storefront.id` in agreement when your app reads both. The mock does not cross-validate; mismatches surface in the page exactly as they would against Apple.
