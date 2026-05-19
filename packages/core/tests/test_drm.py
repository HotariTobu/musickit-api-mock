from __future__ import annotations

import base64
import json
from typing import TYPE_CHECKING

import pytest
from musickit_api_mock import (
    LicenseCatalogSongContext,
    LicenseHlsOffersContext,
    LicenseLiveRadioContext,
    LicenseResponse,
    LicenseResponseGeoBlock,
    LicenseResponseStreamUpsell,
    LicenseResponseSuccess,
    MusicKitApiMock,
    Request,
    WidevineCertResponseFailure,
    WidevineCertResponseSuccess,
)

if TYPE_CHECKING:
    from musickit_api_mock.json_value import _JSONValue

    from tests._apple_response import _LicenseResponseBody


_ACQUIRE_LICENSE_URL = (
    "https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/acquireWebPlaybackLicense"
)
_STREAMING_KEY_DELIVERY_URL = (
    "https://linear.tv.apple.com/v1/radio/streaming-key-delivery"
)


def _post_license(
    mock: MusicKitApiMock, body_dict: dict[str, _JSONValue]
) -> tuple[int, _LicenseResponseBody]:
    body = json.dumps(body_dict).encode()
    resp = mock.handle_request(
        Request(
            method="POST",
            url=_ACQUIRE_LICENSE_URL,
            headers={},
            body=body,
        )
    )
    assert resp is not None
    return resp.status, json.loads(resp.body)


def _post_license_raw(
    mock: MusicKitApiMock, body: bytes | None, *, url: str = _ACQUIRE_LICENSE_URL
) -> None:
    mock.handle_request(Request(method="POST", url=url, headers={}, body=body))


def _post_streaming_key_delivery(
    mock: MusicKitApiMock, body_dict: dict[str, _JSONValue]
) -> tuple[int, _LicenseResponseBody]:
    body = json.dumps(body_dict).encode()
    resp = mock.handle_request(
        Request(
            method="POST",
            url=_STREAMING_KEY_DELIVERY_URL,
            headers={},
            body=body,
        )
    )
    assert resp is not None
    return resp.status, json.loads(resp.body)


def test_license_catalog_song_success_static(mock: MusicKitApiMock) -> None:
    mock.endpoints.license_catalog_song = LicenseResponseSuccess(
        license=b"hello", renew_after=600
    )
    status, body = _post_license(
        mock,
        {
            "challenge": "abc",
            "uri": "data:;base64,xxx",
            "key-system": "com.widevine.alpha",
            "adamId": "1",
            "isLibrary": False,
            "user-initiated": True,
        },
    )
    assert status == 200
    assert base64.b64decode(body["license"]) == b"hello"
    assert body["renew-after"] == 600
    assert body["status"] == 0


def test_license_catalog_song_geo_block(mock: MusicKitApiMock) -> None:
    failures: dict[str, LicenseResponse] = {"1": LicenseResponseGeoBlock()}
    mock.endpoints.license_catalog_song = failures
    status, body = _post_license(
        mock, {"key-system": "com.widevine.alpha", "adamId": "1"}
    )
    assert status == 200
    assert body["status"] == -1017
    assert body["errorCode"] == -1017


def test_license_catalog_song_callable_per_key_system(mock: MusicKitApiMock) -> None:
    mock.endpoints.license_catalog_song = lambda ctx: (
        LicenseResponseStreamUpsell()
        if ctx.key_system == "com.widevine.alpha"
        else LicenseResponseSuccess(license=b"")
    )
    s1, b1 = _post_license(mock, {"key-system": "com.widevine.alpha", "adamId": "1"})
    s2, b2 = _post_license(mock, {"key-system": "com.apple.fps", "adamId": "1"})
    assert s1 == 200
    assert b1["status"] == 3084
    assert s2 == 200
    assert b2["status"] == 0


def test_license_live_radio_dispatch(mock: MusicKitApiMock) -> None:
    failures: dict[str, LicenseResponse] = {
        "ra.978194965": LicenseResponseStreamUpsell(),
    }
    mock.endpoints.license_live_radio = failures
    status, body = _post_license(
        mock, {"key-system": "com.widevine.alpha", "adamId": "ra.978194965"}
    )
    assert status == 200
    assert body["status"] == 3084


def test_license_unset_raises(mock: MusicKitApiMock) -> None:
    with pytest.raises(ValueError, match="license_catalog_song"):
        _post_license(mock, {"key-system": "com.widevine.alpha", "adamId": "1"})


def test_widevine_cert_success(mock: MusicKitApiMock) -> None:
    mock.endpoints.widevine_cert = WidevineCertResponseSuccess(cert=b"\x00\x01\x02")
    resp = mock.handle_request(
        Request(
            method="GET",
            url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/widevineCert?t=1",
            headers={},
            body=None,
        )
    )
    assert resp is not None
    assert resp.status == 200
    assert resp.body == b"\x00\x01\x02"


def test_widevine_cert_failure(mock: MusicKitApiMock) -> None:
    mock.endpoints.widevine_cert = WidevineCertResponseFailure()
    resp = mock.handle_request(
        Request(
            method="GET",
            url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/widevineCert",
            headers={},
            body=None,
        )
    )
    assert resp is not None
    assert resp.status == 500


def test_license_success_emits_renew_after(mock: MusicKitApiMock) -> None:
    """``LicenseResponseSuccess.renew_after`` surfaces as ``renew-after`` in the body."""
    mock.endpoints.license_catalog_song = LicenseResponseSuccess(
        license=b"k", renew_after=900
    )
    status, body = _post_license(
        mock, {"key-system": "com.widevine.alpha", "adamId": "1"}
    )
    assert status == 200
    assert body["renew-after"] == 900


def test_license_success_emits_stkn(mock: MusicKitApiMock) -> None:
    """``LicenseResponseSuccess.stkn`` surfaces as ``stkn`` in the body."""
    mock.endpoints.license_catalog_song = LicenseResponseSuccess(
        license=b"k", stkn="session-token"
    )
    status, body = _post_license(
        mock, {"key-system": "com.widevine.alpha", "adamId": "1"}
    )
    assert status == 200
    assert body["stkn"] == "session-token"


def test_license_success_omits_renew_after_when_unset(mock: MusicKitApiMock) -> None:
    """An unset ``renew_after`` does not surface as ``renew-after: null``."""
    mock.endpoints.license_catalog_song = LicenseResponseSuccess(license=b"k")
    status, body = _post_license(
        mock, {"key-system": "com.widevine.alpha", "adamId": "1"}
    )
    assert status == 200
    assert "renew-after" not in body
    assert "stkn" not in body


def test_license_playready_key_system_dispatch(mock: MusicKitApiMock) -> None:
    captured: list[str] = []

    def handler(ctx: LicenseCatalogSongContext) -> LicenseResponse:
        captured.append(ctx.key_system)
        return LicenseResponseSuccess(license=b"")

    mock.endpoints.license_catalog_song = handler
    status, _ = _post_license(
        mock, {"key-system": "com.microsoft.playready", "adamId": "1"}
    )
    assert status == 200
    assert captured == ["com.microsoft.playready"]


def test_license_missing_key_system_raises(mock: MusicKitApiMock) -> None:
    mock.endpoints.license_catalog_song = LicenseResponseSuccess(license=b"")
    with pytest.raises(ValueError, match="key-system"):
        _post_license(mock, {"adamId": "1"})


def test_license_invalid_key_system_flows_through(mock: MusicKitApiMock) -> None:
    captured: list[str] = []

    def handler(ctx: LicenseCatalogSongContext) -> LicenseResponse:
        captured.append(ctx.key_system)
        return LicenseResponseSuccess(license=b"")

    mock.endpoints.license_catalog_song = handler
    status, _ = _post_license(
        mock,
        {"key-system": "com.example.unknown-drm", "adamId": "1"},
    )
    assert status == 200
    assert captured == ["com.example.unknown-drm"]


@pytest.mark.parametrize(
    "body",
    [
        None,
        b"",
        b"   ",
        b"not json",
        b"[1, 2, 3]",
        b'"string-root"',
    ],
)
def test_license_decode_body_edge_cases(
    mock: MusicKitApiMock, body: bytes | None
) -> None:
    mock.endpoints.license_catalog_song = LicenseResponseSuccess(license=b"")
    with pytest.raises(ValueError, match="key-system"):
        _post_license_raw(mock, body)


def test_license_hls_offers_dispatch(mock: MusicKitApiMock) -> None:
    captured: list[LicenseHlsOffersContext] = []

    def handler(ctx: LicenseHlsOffersContext) -> LicenseResponse:
        captured.append(ctx)
        return LicenseResponseSuccess(license=b"")

    mock.endpoints.license_hls_offers = handler
    status, _ = _post_license(
        mock,
        {
            "key-system": "com.widevine.alpha",
            "license-requests": [{"adam-id": "9876"}],
        },
    )
    assert status == 200
    assert len(captured) == 1
    assert captured[0].adam_id == "9876"
    assert captured[0].key_system == "com.widevine.alpha"


def test_license_hls_offers_first_not_dict_fallback(mock: MusicKitApiMock) -> None:
    captured: list[LicenseHlsOffersContext] = []

    def handler(ctx: LicenseHlsOffersContext) -> LicenseResponse:
        captured.append(ctx)
        return LicenseResponseSuccess(license=b"")

    mock.endpoints.license_hls_offers = handler
    status, _ = _post_license(
        mock,
        {
            "key-system": "com.widevine.alpha",
            "license-requests": ["not-a-dict"],
        },
    )
    assert status == 200
    assert len(captured) == 1
    assert captured[0].adam_id == ""


def test_streaming_key_delivery_dispatch(mock: MusicKitApiMock) -> None:
    captured: list[LicenseLiveRadioContext] = []

    def handler(ctx: LicenseLiveRadioContext) -> LicenseResponse:
        captured.append(ctx)
        return LicenseResponseSuccess(license=b"k")

    mock.endpoints.license_live_radio = handler
    status, _ = _post_streaming_key_delivery(
        mock,
        {"key-system": "com.apple.fps", "adamId": "ra.978194965"},
    )
    assert status == 200
    assert len(captured) == 1
    assert captured[0].station_id == "ra.978194965"
    assert captured[0].key_system == "com.apple.fps"
