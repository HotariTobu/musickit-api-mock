"""Setter forms each resolver path supports.

The endpoint resolver layer has three lookup paths:

- static (``_resolve_static``): bare value or no-arg ``Callable[[], T]``
- with-context (``_resolve_with_context``): bare value or
  ``Callable[[ctx], T]``
- keyed (``_resolve_keyed``): bare value, ``dict[str, T]``, or
  ``Callable[[ctx], T]``

Existing tests cover the bare-value form for most setters and the
callable form for a few. These tests round out the matrix so each
resolver's documented forms are exercised at least once.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, cast

from musickit_api_mock import (
    Account,
    AccountResponse,
    AccountResponseSuccess,
    ContinuousStation,
    ContinuousStationsContext,
    ContinuousStationsResponse,
    ContinuousStationsResponseSuccess,
    LicenseResponseGeoBlock,
    LicenseResponseSuccess,
    LogoutResponseSuccess,
    MusicKitApiMock,
    PlayActivityResponseSuccess,
    Request,
    Station,
    Storefront,
    StorefrontResponse,
    StorefrontResponseSuccess,
    WebPlaybackAsset,
    WebPlaybackContext,
    WebPlaybackResponse,
    WebPlaybackResponseSuccess,
    WebPlaybackSong,
)

if TYPE_CHECKING:
    from tests._apple_response import (
        _AccountMeta,
        _AppleResponse,
        _LicenseResponseBody,
        _WebPlaybackResponseBody,
    )


def _get(mock: MusicKitApiMock, url: str) -> tuple[int, _AppleResponse]:
    resp = mock.handle_request(Request(method="GET", url=url, headers={}, body=None))
    assert resp is not None
    return resp.status, json.loads(resp.body)


def _post(mock: MusicKitApiMock, url: str, body: bytes) -> tuple[int, _AppleResponse]:
    resp = mock.handle_request(Request(method="POST", url=url, headers={}, body=body))
    assert resp is not None
    return resp.status, json.loads(resp.body)


def _storefront() -> StorefrontResponse:
    return StorefrontResponseSuccess(
        storefront=Storefront(
            id="us",
            name="US",
            default_language_tag="en-US",
            supported_language_tags=["en-US"],
            explicit_content_policy="allowed",
        )
    )


# --- _resolve_static: callable form ------------------------------------------------


def test_storefront_callable_form_evaluated_per_call() -> None:
    """``mock.endpoints.storefront`` accepts a ``Callable[[], StorefrontResponse]``."""
    counter = {"n": 0}

    def make_resp() -> StorefrontResponse:
        counter["n"] += 1
        return StorefrontResponseSuccess(
            storefront=Storefront(
                id=f"sf-{counter['n']}",
                name="X",
                default_language_tag="en-US",
                supported_language_tags=["en-US"],
                explicit_content_policy="allowed",
            )
        )

    m = MusicKitApiMock()
    m.endpoints.storefront = make_resp
    s1, b1 = _get(m, "https://api.music.apple.com/v1/me/storefront")
    s2, b2 = _get(m, "https://api.music.apple.com/v1/me/storefront")
    assert s1 == s2 == 200
    assert b1["data"][0]["id"] == "sf-1"
    assert b2["data"][0]["id"] == "sf-2"


def test_account_callable_form() -> None:
    m = MusicKitApiMock()

    def make_resp() -> AccountResponse:
        return AccountResponseSuccess(
            account=Account(subscription_active=False, subscription_storefront="us")
        )

    m.endpoints.account = make_resp
    status, body = _get(
        m, "https://api.music.apple.com/v1/me/account?meta=subscription"
    )
    assert status == 200
    meta = cast("_AccountMeta", body["meta"])
    assert meta["subscription"]["active"] is False


def test_play_activity_callable_form() -> None:
    m = MusicKitApiMock()
    m.endpoints.play_activity = lambda: PlayActivityResponseSuccess()
    status, _body = _post(
        m,
        "https://universal-activity-service.itunes.apple.com/play",
        b"{}",
    )
    assert status == 200


def test_webplayer_logout_callable_form() -> None:
    m = MusicKitApiMock()
    m.endpoints.webplayer_logout = lambda: LogoutResponseSuccess()
    status, body = _post(
        m,
        "https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/webPlayerLogout",
        b"",
    )
    assert status == 200
    assert body == {"status": 0}


# --- _resolve_keyed: dict form for web_playback / play_assets / station_next_tracks


def test_web_playback_dict_form_dispatches_on_salable_adam_id(
    mock: MusicKitApiMock,
) -> None:
    """``endpoints.web_playback = {<id>: <response>}`` keys on ``salableAdamId``."""
    success_song = WebPlaybackSong(
        song_id="s1",
        hls_key_cert_url="https://s.mzstatic.com/skdtool_2021_certbundle.bin",
        hls_key_server_url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/acquireWebPlaybackLicense",
        widevine_cert_url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/widevineCert",
        assets=[
            WebPlaybackAsset(
                flavor="28:cbcp32",
                url="https://aod-ssl.itunes.apple.com/itunes-assets/s1/index.m3u8",
            )
        ],
    )
    web_playback_dict: dict[str, WebPlaybackResponse] = {
        "s1": WebPlaybackResponseSuccess(song_list=[success_song]),
    }
    mock.endpoints.web_playback = web_playback_dict
    body = json.dumps({"salableAdamId": "s1"}).encode()
    status, raw = _post(
        mock,
        "https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/webPlayback",
        body,
    )
    parsed = cast("_WebPlaybackResponseBody", raw)
    assert status == 200
    assert parsed["status"] == 0
    assert parsed["songList"][0]["songId"] == "s1"


def test_web_playback_callable_form_receives_context(mock: MusicKitApiMock) -> None:
    captured: list[str] = []

    def fn(ctx: WebPlaybackContext) -> WebPlaybackResponse:
        captured.append(ctx.salable_adam_id)
        return WebPlaybackResponseSuccess(song_list=[])

    mock.endpoints.web_playback = fn
    body = json.dumps({"salableAdamId": "abc"}).encode()
    _post(
        mock,
        "https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/webPlayback",
        body,
    )
    assert captured == ["abc"]


# --- _resolve_with_context: static form for continuous_stations ------------------


def test_continuous_stations_static_form(mock: MusicKitApiMock) -> None:
    """``endpoints.continuous_stations = <response>`` (no callable) is the static form."""
    stations = cast("dict[str, Station]", mock.data.stations)
    station = stations["ra.978194965"]
    static_resp: ContinuousStationsResponse = ContinuousStationsResponseSuccess(
        continuous_station=ContinuousStation(station=station, tracks=None)
    )
    mock.endpoints.continuous_stations = static_resp
    body = json.dumps({"data": [{"id": "1", "type": "songs"}]}).encode()
    status, parsed = _post(
        mock,
        "https://api.music.apple.com/v1/me/stations/continuous",
        body,
    )
    assert status == 200
    assert "station" in parsed["results"]


def test_continuous_stations_callable_receives_context(
    mock: MusicKitApiMock,
) -> None:
    captured: list[int] = []

    def fn(ctx: ContinuousStationsContext) -> ContinuousStationsResponse:
        captured.append(len(ctx.seeds or []))
        stations = cast("dict[str, Station]", mock.data.stations)
        return ContinuousStationsResponseSuccess(
            continuous_station=ContinuousStation(
                station=stations["ra.978194965"], tracks=None
            )
        )

    mock.endpoints.continuous_stations = fn
    body = json.dumps(
        {"data": [{"id": "1", "type": "songs"}, {"id": "2", "type": "songs"}]}
    ).encode()
    _post(mock, "https://api.music.apple.com/v1/me/stations/continuous", body)
    assert captured == [2]


# --- _resolve_keyed: license dict + callable forms cross-check ----------------


def test_license_dict_form_keys_on_adam_id(mock: MusicKitApiMock) -> None:
    """A dict mapping adam_id → response covers per-id license dispatch."""
    from musickit_api_mock import LicenseResponse

    license_dict: dict[str, LicenseResponse] = {
        "1": LicenseResponseSuccess(license=b"good"),
        "2": LicenseResponseGeoBlock(),
    }
    mock.endpoints.license_catalog_song = license_dict
    a = json.dumps({"key-system": "com.widevine.alpha", "adamId": "1"}).encode()
    b = json.dumps({"key-system": "com.widevine.alpha", "adamId": "2"}).encode()
    s_a, raw_a = _post(
        mock,
        "https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/acquireWebPlaybackLicense",
        a,
    )
    s_b, raw_b = _post(
        mock,
        "https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/acquireWebPlaybackLicense",
        b,
    )
    body_a = cast("_LicenseResponseBody", raw_a)
    body_b = cast("_LicenseResponseBody", raw_b)
    assert s_a == s_b == 200
    assert body_a["status"] == 0
    assert body_b["status"] == -1017
