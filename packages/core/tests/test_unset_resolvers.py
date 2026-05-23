"""Every endpoint setter raises ``ValueError`` when reached while unset.

Encodes the "no implicit defaults" axis: configuration fields default to
``None`` and reading an unset field raises. Each test triggers exactly
one resolver via a real request without configuring its setter, then
asserts the raised ``ValueError`` mentions the field name. Matching on
the field name (not the surrounding "is not set" prose) binds to the
public API surface — the field path the user assigns to — so a refactor
of the error-message format won't break the test.
"""

from __future__ import annotations

import json

import pytest
from musickit_api_mock import Artwork, MusicKitApiMock, Request, Station


def _send(m: MusicKitApiMock, req: Request) -> None:
    m.handle_request(req)


def _new_mock() -> MusicKitApiMock:
    return MusicKitApiMock()


def test_storefront_unset_raises() -> None:
    m = _new_mock()
    with pytest.raises(ValueError, match="storefront"):
        _send(
            m,
            Request(
                method="GET",
                url="https://api.music.apple.com/v1/me/storefront",
                headers={},
                body=None,
            ),
        )


def test_account_unset_raises() -> None:
    m = _new_mock()
    with pytest.raises(ValueError, match="account"):
        _send(
            m,
            Request(
                method="GET",
                url="https://api.music.apple.com/v1/me/account?meta=subscription",
                headers={},
                body=None,
            ),
        )


def test_widevine_cert_unset_raises() -> None:
    m = _new_mock()
    with pytest.raises(ValueError, match="widevine_cert"):
        _send(
            m,
            Request(
                method="GET",
                url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/widevineCert",
                headers={},
                body=None,
            ),
        )


def test_fairplay_cert_unset_raises() -> None:
    m = _new_mock()
    with pytest.raises(ValueError, match="fairplay_cert"):
        _send(
            m,
            Request(
                method="GET",
                url="https://s.mzstatic.com/skdtool_2021_certbundle.bin",
                headers={},
                body=None,
            ),
        )


def test_webplayer_logout_unset_raises() -> None:
    m = _new_mock()
    with pytest.raises(ValueError, match="webplayer_logout"):
        _send(
            m,
            Request(
                method="POST",
                url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/webPlayerLogout",
                headers={},
                body=b"",
            ),
        )


def test_renew_music_token_unset_raises() -> None:
    m = _new_mock()
    with pytest.raises(ValueError, match="renew_music_token"):
        _send(
            m,
            Request(
                method="POST",
                url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/renewMusicToken",
                headers={},
                body=b"",
            ),
        )


def test_play_activity_unset_raises() -> None:
    m = _new_mock()
    with pytest.raises(ValueError, match="play_activity"):
        _send(
            m,
            Request(
                method="POST",
                url="https://universal-activity-service.itunes.apple.com/play",
                headers={},
                body=b"{}",
            ),
        )


def test_station_next_tracks_unset_raises() -> None:
    m = _new_mock()
    with pytest.raises(ValueError, match="station_next_tracks"):
        _send(
            m,
            Request(
                method="POST",
                url="https://api.music.apple.com/v1/me/stations/next-tracks/ra.1",
                headers={},
                body=b"",
            ),
        )


def test_continuous_stations_unset_raises() -> None:
    m = _new_mock()
    with pytest.raises(ValueError, match="continuous_stations"):
        _send(
            m,
            Request(
                method="POST",
                url="https://api.music.apple.com/v1/me/stations/continuous?with=tracks",
                headers={},
                body=b"{}",
            ),
        )


def test_license_hls_offers_unset_raises() -> None:
    m = _new_mock()
    body = json.dumps(
        {
            "key-system": "com.widevine.alpha",
            "license-requests": [{"adam-id": "1"}],
        }
    ).encode()
    with pytest.raises(ValueError, match="license_hls_offers"):
        _send(
            m,
            Request(
                method="POST",
                url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/acquireWebPlaybackLicense",
                headers={},
                body=body,
            ),
        )


def test_license_live_radio_unset_raises() -> None:
    m = _new_mock()
    body = json.dumps({"key-system": "com.widevine.alpha", "adamId": "ra.1"}).encode()
    with pytest.raises(ValueError, match="license_live_radio"):
        _send(
            m,
            Request(
                method="POST",
                url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/acquireWebPlaybackLicense",
                headers={},
                body=body,
            ),
        )


def test_web_playback_unset_raises() -> None:
    m = _new_mock()
    body = json.dumps({"salableAdamId": "1"}).encode()
    with pytest.raises(ValueError, match="web_playback"):
        _send(
            m,
            Request(
                method="POST",
                url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/webPlayback",
                headers={},
                body=body,
            ),
        )


def test_play_assets_catalog_song_unset_raises() -> None:
    m = _new_mock()
    with pytest.raises(ValueError, match="play_assets_catalog_song"):
        _send(
            m,
            Request(
                method="GET",
                url="https://api.music.apple.com/v1/play/assets?id=1&kind=song",
                headers={},
                body=None,
            ),
        )


def test_play_assets_live_audio_unset_raises() -> None:
    m = _new_mock()
    m.data.stations = {
        "ra.1": Station(
            name="X",
            artwork=Artwork(url="x", width=1, height=1),
            is_live=True,
            media_kind="audio",
            url="x",
            is_tracks_station=False,
            has_drm=True,
            kind="radio",
            radio_url="x",
            requires_subscription=True,
        )
    }
    with pytest.raises(ValueError, match="play_assets_live_audio"):
        _send(
            m,
            Request(
                method="GET",
                url="https://api.music.apple.com/v1/play/assets?id=ra.1&kind=radioStation",
                headers={},
                body=None,
            ),
        )


def test_authorize_response_unset_raises() -> None:
    m = _new_mock()
    with pytest.raises(ValueError, match="authorize_response"):
        _send(
            m,
            Request(
                method="GET",
                url="https://musickit-api-mock.invalid/browser/authorize_response",
                headers={},
                body=None,
            ),
        )


def test_eme_flavor_unset_raises() -> None:
    m = _new_mock()
    with pytest.raises(ValueError, match="eme_flavor"):
        _send(
            m,
            Request(
                method="GET",
                url="https://musickit-api-mock.invalid/browser/eme_flavor",
                headers={},
                body=None,
            ),
        )
