"""Shared failure code mapping for license and web_playback endpoints.

Apple emits the same numeric ``errorCode`` / ``failureType`` for both the
license endpoints (``acquireWebPlaybackLicense``, ``streamingKeyDelivery``)
and the web_playback endpoint, parameterized by the same set of failure
kinds (MediaLicense, DeviceLimit, GeoBlock, etc.). Each kind is paired
with its ``LicenseResponse*`` and ``WebPlaybackResponse*`` classes here so
the numeric value lives in a single place.
"""

from __future__ import annotations

from musickit_api_mock.endpoints.responses.license import (
    LicenseResponseAuthorizationError,
    LicenseResponseContentRestricted,
    LicenseResponseContentUnavailable,
    LicenseResponseDeviceLimit,
    LicenseResponseGeoBlock,
    LicenseResponseMediaLicense,
    LicenseResponseNotFound,
    LicenseResponsePlayReadyCbcEncryptionError,
    LicenseResponseServerError,
    LicenseResponseStreamUpsell,
    LicenseResponseSubscriptionError,
    LicenseResponseTokenExpired,
    LicenseResponseWidevineCdmExpired,
)
from musickit_api_mock.endpoints.responses.web_playback import (
    WebPlaybackResponseAuthorizationError,
    WebPlaybackResponseContentRestricted,
    WebPlaybackResponseContentUnavailable,
    WebPlaybackResponseDeviceLimit,
    WebPlaybackResponseGeoBlock,
    WebPlaybackResponseMediaLicense,
    WebPlaybackResponseNotFound,
    WebPlaybackResponsePlayReadyCbcEncryptionError,
    WebPlaybackResponseServerError,
    WebPlaybackResponseStreamUpsell,
    WebPlaybackResponseSubscriptionError,
    WebPlaybackResponseTokenExpired,
    WebPlaybackResponseWidevineCdmExpired,
)

_PLAYBACK_FAILURES: list[tuple[int, type, type]] = [
    (-1003, LicenseResponseMediaLicense, WebPlaybackResponseMediaLicense),
    (-1004, LicenseResponseDeviceLimit, WebPlaybackResponseDeviceLimit),
    (-1017, LicenseResponseGeoBlock, WebPlaybackResponseGeoBlock),
    (1010, LicenseResponseNotFound, WebPlaybackResponseNotFound),
    (2002, LicenseResponseAuthorizationError, WebPlaybackResponseAuthorizationError),
    (2034, LicenseResponseTokenExpired, WebPlaybackResponseTokenExpired),
    (3063, LicenseResponseSubscriptionError, WebPlaybackResponseSubscriptionError),
    (3076, LicenseResponseContentUnavailable, WebPlaybackResponseContentUnavailable),
    (3082, LicenseResponseContentRestricted, WebPlaybackResponseContentRestricted),
    (3084, LicenseResponseStreamUpsell, WebPlaybackResponseStreamUpsell),
    (5002, LicenseResponseServerError, WebPlaybackResponseServerError),
    (
        180202,
        LicenseResponsePlayReadyCbcEncryptionError,
        WebPlaybackResponsePlayReadyCbcEncryptionError,
    ),
    (
        190121,
        LicenseResponseWidevineCdmExpired,
        WebPlaybackResponseWidevineCdmExpired,
    ),
]


_LICENSE_FAILURE_CODES: dict[type, int] = {
    license_cls: code for code, license_cls, _ in _PLAYBACK_FAILURES
}

_WEB_PLAYBACK_FAILURE_CODES: dict[type, int] = {
    web_playback_cls: code for code, _, web_playback_cls in _PLAYBACK_FAILURES
}
