"""Apple-defined failure-code emission for license + web-playback responses.

Each user-facing failure variant maps to an Apple ``failureType`` /
``errorCode`` numeric code. The test parametrizes over the variant class
and the code Apple emits, so the table itself is the contract being
verified — re-stated locally rather than imported from the library, so
that an accidental drift in the library table fails the test instead of
becoming invisible.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
from musickit_api_mock import (
    LicenseResponse,
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
    MusicKitApiMock,
    Request,
    WebPlaybackResponse,
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

if TYPE_CHECKING:
    from collections.abc import Callable

_LICENSE_TABLE: list[tuple[Callable[[], LicenseResponse], int]] = [
    (LicenseResponseMediaLicense, -1003),
    (LicenseResponseDeviceLimit, -1004),
    (LicenseResponseGeoBlock, -1017),
    (LicenseResponseNotFound, 1010),
    (LicenseResponseAuthorizationError, 2002),
    (LicenseResponseTokenExpired, 2034),
    (LicenseResponseSubscriptionError, 3063),
    (LicenseResponseContentUnavailable, 3076),
    (LicenseResponseContentRestricted, 3082),
    (LicenseResponseStreamUpsell, 3084),
    (LicenseResponseServerError, 5002),
    (LicenseResponsePlayReadyCbcEncryptionError, 180202),
    (LicenseResponseWidevineCdmExpired, 190121),
]

_WEB_PLAYBACK_TABLE: list[tuple[Callable[[], WebPlaybackResponse], int]] = [
    (WebPlaybackResponseMediaLicense, -1003),
    (WebPlaybackResponseDeviceLimit, -1004),
    (WebPlaybackResponseGeoBlock, -1017),
    (WebPlaybackResponseNotFound, 1010),
    (WebPlaybackResponseAuthorizationError, 2002),
    (WebPlaybackResponseTokenExpired, 2034),
    (WebPlaybackResponseSubscriptionError, 3063),
    (WebPlaybackResponseContentUnavailable, 3076),
    (WebPlaybackResponseContentRestricted, 3082),
    (WebPlaybackResponseStreamUpsell, 3084),
    (WebPlaybackResponseServerError, 5002),
    (WebPlaybackResponsePlayReadyCbcEncryptionError, 180202),
    (WebPlaybackResponseWidevineCdmExpired, 190121),
]


@pytest.mark.parametrize(("variant_cls", "expected_code"), _LICENSE_TABLE)
def test_license_failure_emits_apple_error_code(
    mock: MusicKitApiMock,
    variant_cls: Callable[[], LicenseResponse],
    expected_code: int,
) -> None:
    mock.endpoints.license_catalog_song = variant_cls()
    body = json.dumps({"key-system": "com.widevine.alpha", "adamId": "1"}).encode()
    resp = mock.handle_request(
        Request(
            method="POST",
            url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/acquireWebPlaybackLicense",
            headers={},
            body=body,
        )
    )
    assert resp is not None
    assert resp.status == 200
    parsed = json.loads(resp.body)
    assert parsed["errorCode"] == expected_code
    assert parsed["status"] == expected_code


@pytest.mark.parametrize(("variant_cls", "expected_code"), _WEB_PLAYBACK_TABLE)
def test_web_playback_failure_emits_apple_failure_type(
    mock: MusicKitApiMock,
    variant_cls: Callable[[], WebPlaybackResponse],
    expected_code: int,
) -> None:
    mock.endpoints.web_playback = variant_cls()
    body = json.dumps({"salableAdamId": "1"}).encode()
    resp = mock.handle_request(
        Request(
            method="POST",
            url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/webPlayback",
            headers={},
            body=body,
        )
    )
    assert resp is not None
    assert resp.status == 200
    parsed = json.loads(resp.body)
    assert parsed["failureType"] == expected_code
    assert parsed["status"] == expected_code
