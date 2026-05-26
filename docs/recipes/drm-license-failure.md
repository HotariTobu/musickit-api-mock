# Force a DRM license failure

DRM failure has two dials. The **key system** decides which CDM the page negotiates with (FairPlay on WebKit, Widevine on Chromium / Firefox, PlayReady on some Windows builds). The **license response** decides what the license-acquisition endpoint returns once the CDM asks for a key. To produce a DRM failure end-to-end, control both.

## Pick the key system

```python
from musickit_api_mock import MusicKitApiMock

mock = MusicKitApiMock()

mock.browser.eme_flavor = "com.widevine.alpha"  # or "com.apple.fps" / "com.microsoft.playready"
```

The shim reports this value when MusicKit JS probes Encrypted Media Extensions, so the page proceeds down the matching DRM code path regardless of the host browser's native CDM.

## Return a media-license failure

```python
from musickit_api_mock import LicenseResponseMediaLicense

mock.endpoints.license_catalog_song = {
    "1000000001": LicenseResponseMediaLicense(),
}
```

The license endpoint emits HTTP 200 with the body status code MusicKit JS dispatches as `MKError.Reason.MEDIA_LICENSE`. The behavior is identical for FairPlay and Widevine — MusicKit's parser is body-driven and ignores HTTP status when an error code is present.

## Other failure modes

The license response union exposes every error reason MusicKit JS recognizes. Reach for the variant that matches the failure you want to test:

- `LicenseResponseDeviceLimit` — "too many devices" prompt path.
- `LicenseResponseGeoBlock` — region restriction.
- `LicenseResponseSubscriptionError` — paid-up dropped between fetch and play.
- `LicenseResponseTokenExpired` — triggers a token renewal + retry.
- `LicenseResponseWidevineCdmExpired` — Widevine-specific "update your browser" path.
- `LicenseResponsePlayReadyCbcEncryptionError` — PlayReady CBC bug path.

The full set is in the [`mock.endpoints` reference](../reference/endpoints.md#license-drm).

## HLS-offers and live-radio

Catalog-song license is one of three license endpoints. Use the matching surface for HLS-offers (per-song renewal handshake) and live-radio:

```python
mock.endpoints.license_hls_offers = {"1000000001": LicenseResponseMediaLicense()}
mock.endpoints.license_live_radio = {"ra.1234567890": LicenseResponseGeoBlock()}
```
