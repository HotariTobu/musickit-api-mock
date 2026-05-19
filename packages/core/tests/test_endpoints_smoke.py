"""Boundary-surface smoke tests for endpoints not exercised elsewhere.

Drives one request per endpoint to verify that the URL is matched, the
handler runs, and the configured payload flows back through the
boundary. Assertions stay on observable contract (status, body bytes,
configured value round-trip) so they survive internal refactors.
"""

from __future__ import annotations

import json

from musickit_api_mock import (
    FairPlayCertResponseFailure,
    FairPlayCertResponseSuccess,
    LicenseResponseStreamUpsell,
    LicenseResponseSuccess,
    MusicKitApiMock,
    PlayActivityResponseSuccess,
    Request,
)


def test_hls_manifest_returns_apple_mpegurl(mock: MusicKitApiMock) -> None:
    resp = mock.handle_request(
        Request(
            method="GET",
            url="https://aod-ssl.itunes.apple.com/itunes-assets/1/index.m3u8",
            headers={},
            body=None,
        )
    )
    assert resp is not None
    assert resp.status == 200
    assert resp.headers.get("Content-Type") == "application/vnd.apple.mpegurl"
    assert resp.body.startswith(b"#EXTM3U")


def test_hls_manifest_unknown_song_404(mock: MusicKitApiMock) -> None:
    resp = mock.handle_request(
        Request(
            method="GET",
            url="https://aod-ssl.itunes.apple.com/itunes-assets/missing/index.m3u8",
            headers={},
            body=None,
        )
    )
    assert resp is not None
    assert resp.status == 404


def test_hls_segment_returns_configured_bytes(mock: MusicKitApiMock) -> None:
    resp = mock.handle_request(
        Request(
            method="GET",
            url="https://aod-ssl.itunes.apple.com/itunes-assets/1/index.m4s",
            headers={},
            body=None,
        )
    )
    assert resp is not None
    assert resp.status == 200
    assert resp.body == b"\x00\x00\x00\x00"


def test_hls_segment_unknown_song_404(mock: MusicKitApiMock) -> None:
    resp = mock.handle_request(
        Request(
            method="GET",
            url="https://aod-ssl.itunes.apple.com/itunes-assets/missing/index.m4s",
            headers={},
            body=None,
        )
    )
    assert resp is not None
    assert resp.status == 404


def test_preview_returns_configured_bytes(mock: MusicKitApiMock) -> None:
    resp = mock.handle_request(
        Request(
            method="GET",
            url="https://audio-ssl.itunes.apple.com/preview/1.m4a",
            headers={},
            body=None,
        )
    )
    assert resp is not None
    assert resp.status == 200
    assert resp.body == b"\x00\x00\x00\x00"


def test_preview_unknown_song_404(mock: MusicKitApiMock) -> None:
    resp = mock.handle_request(
        Request(
            method="GET",
            url="https://audio-ssl.itunes.apple.com/preview/missing.m4a",
            headers={},
            body=None,
        )
    )
    assert resp is not None
    assert resp.status == 404


def test_play_activity_returns_json(mock: MusicKitApiMock) -> None:
    mock.endpoints.play_activity = PlayActivityResponseSuccess()
    resp = mock.handle_request(
        Request(
            method="POST",
            url="https://universal-activity-service.itunes.apple.com/play",
            headers={},
            body=b"{}",
        )
    )
    assert resp is not None
    assert resp.status == 200
    assert json.loads(resp.body) == {}


def test_streaming_key_delivery_dispatches_to_live_radio_setter(
    mock: MusicKitApiMock,
) -> None:
    mock.endpoints.license_live_radio = LicenseResponseSuccess(license=b"radio-key")
    body = json.dumps(
        {"key-system": "com.widevine.alpha", "adamId": "ra.978194965"}
    ).encode()
    resp = mock.handle_request(
        Request(
            method="POST",
            url="https://linear.tv.apple.com/v1/radio/streaming-key-delivery",
            headers={},
            body=body,
        )
    )
    assert resp is not None
    assert resp.status == 200
    parsed = json.loads(resp.body)
    assert parsed["status"] == 0


def test_streaming_key_delivery_failure_emits_failure_code(
    mock: MusicKitApiMock,
) -> None:
    mock.endpoints.license_live_radio = LicenseResponseStreamUpsell()
    body = json.dumps(
        {"key-system": "com.widevine.alpha", "adamId": "ra.978194965"}
    ).encode()
    resp = mock.handle_request(
        Request(
            method="POST",
            url="https://linear.tv.apple.com/v1/radio/streaming-key-delivery",
            headers={},
            body=body,
        )
    )
    assert resp is not None
    parsed = json.loads(resp.body)
    assert parsed["status"] == 3084


def test_fairplay_cert_success_returns_bytes(mock: MusicKitApiMock) -> None:
    mock.endpoints.fairplay_cert = FairPlayCertResponseSuccess(cert=b"\xaa\xbb")
    resp = mock.handle_request(
        Request(
            method="GET",
            url="https://s.mzstatic.com/skdtool_2021_certbundle.bin",
            headers={},
            body=None,
        )
    )
    assert resp is not None
    assert resp.status == 200
    assert resp.body == b"\xaa\xbb"


def test_fairplay_cert_failure_returns_5xx(mock: MusicKitApiMock) -> None:
    mock.endpoints.fairplay_cert = FairPlayCertResponseFailure()
    resp = mock.handle_request(
        Request(
            method="GET",
            url="https://s.mzstatic.com/skdtool_2021_certbundle.bin",
            headers={},
            body=None,
        )
    )
    assert resp is not None
    assert resp.status >= 500
