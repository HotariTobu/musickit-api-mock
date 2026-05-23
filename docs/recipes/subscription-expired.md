# Trigger a subscription-expired error mid-playback

MusicKit JS surfaces a subscription error from two body-driven endpoints — `web-playback` (the per-song playback payload) and the license-acquisition endpoints. Either path causes the page to see `MKError.Reason.SUBSCRIPTION_ERROR`; pick the one your code path actually exercises.

## At the web-playback endpoint

```python
from musickit_api_mock import (
    MusicKitApiMock,
    WebPlaybackResponseSubscriptionError,
    WebPlaybackResponseSuccess,
)

mock = MusicKitApiMock()

mock.endpoints.web_playback = {
    "1000000001": WebPlaybackResponseSubscriptionError(),
}
```

The web-playback setter is keyed by salable adam id, so only the listed song triggers the error. Other ids resolve through whatever else is configured (or raise if unset).

## At the license endpoint

```python
from musickit_api_mock import (
    LicenseResponseSubscriptionError,
    MusicKitApiMock,
)

mock = MusicKitApiMock()

mock.endpoints.license_catalog_song = {
    "1000000001": LicenseResponseSubscriptionError(),
}
```

Use this when you want the playback metadata fetch to succeed and the failure to surface only when the CDM requests the license — closer to a "subscription lapsed between fetch and play" scenario.

## Flip a healthy session into expired

Both setters accept a callable. Use a closure to start with success and switch to the error after the first call:

```python
calls = {"count": 0}

def web_playback_for(ctx):
    calls["count"] += 1
    if calls["count"] == 1:
        return WebPlaybackResponseSuccess(song_list=[...])
    return WebPlaybackResponseSubscriptionError()

mock.endpoints.web_playback = web_playback_for
```

This pattern works for every keyed endpoint, not just web-playback.
