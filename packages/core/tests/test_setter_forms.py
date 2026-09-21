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

import pytest
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
    WebPlaybackCatalogItemContext,
    WebPlaybackCatalogLibrarySong,
    WebPlaybackCatalogSong,
    WebPlaybackContext,
    WebPlaybackLibraryItemContext,
    WebPlaybackResponse,
    WebPlaybackResponseSuccess,
)

from tests._expected import ACCOUNT, ARTWORK_CATALOG

_WEB_PLAYBACK_SONG_BODY = {
    "songId": "s1",
    "hls-key-cert-url": "https://s.mzstatic.com/skdtool_2021_certbundle.bin",
    "hls-key-server-url": "https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/acquireWebPlaybackLicense",
    "widevine-cert-url": "https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/widevineCert",
    "assets": [
        {
            "flavor": "28:cbcp32",
            "URL": "https://aod-ssl.itunes.apple.com/itunes-assets/s1/index.m3u8",
        }
    ],
}

_EMPTY_WEB_PLAYBACK_BODY = {"songList": [], "status": 0}

_CONTINUOUS_STATION_BODY = {
    "results": {
        "station": {
            "id": "105900f77595dab2",
            "type": "stations",
            "href": "/v1/catalog/us/stations/105900f77595dab2",
            "attributes": {
                "name": "Apple Music 1",
                "artwork": ARTWORK_CATALOG,
                "isLive": True,
                "kind": "radio",
                "mediaKind": "audio",
                "playParams": {
                    "id": "105900f77595dab2",
                    "kind": "radioStation",
                    "hasDrm": True,
                    "mediaType": "audio",
                    "stationHash": "0510829bf4f6692e",
                },
                "radioUrl": "https://itsliveradio.apple.com/gl/ra.978194965/index-cmaf.m3u8",
                "requiresSubscription": True,
                "url": "https://music.apple.com/us/station/ra.978194965",
            },
        },
    }
}


def _get(mock: MusicKitApiMock, url: str) -> tuple[int, object]:
    resp = mock.handle_request(Request(method="GET", url=url, headers={}, body=None))
    assert resp is not None
    return resp.status, json.loads(resp.body)


def _post(mock: MusicKitApiMock, url: str, body: bytes) -> tuple[int, object]:
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


def _expected_storefront_body(storefront_id: str) -> dict[str, object]:
    return {
        "data": [
            {
                "id": storefront_id,
                "type": "storefronts",
                "href": f"/v1/storefronts/{storefront_id}",
                "attributes": {
                    "name": "X",
                    "defaultLanguageTag": "en-US",
                    "supportedLanguageTags": ["en-US"],
                    "explicitContentPolicy": "allowed",
                },
            }
        ]
    }


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
    assert b1 == _expected_storefront_body("sf-1")
    assert b2 == _expected_storefront_body("sf-2")


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
    assert body == {
        "data": [ACCOUNT],
        "meta": {"subscription": {"active": False, "storefront": "us"}},
    }


def test_play_activity_callable_form() -> None:
    m = MusicKitApiMock()
    m.endpoints.play_activity = lambda: PlayActivityResponseSuccess()
    status, body = _post(
        m,
        "https://universal-activity-service.itunes.apple.com/play",
        b"{}",
    )
    assert status == 200
    assert body == {}


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
    success_song = WebPlaybackCatalogSong(
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
    status, parsed = _post(
        mock,
        "https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/webPlayback",
        body,
    )
    assert status == 200
    assert parsed == {"songList": [_WEB_PLAYBACK_SONG_BODY], "status": 0}


def test_web_playback_mapping_form_dispatches_on_universal_library_id(
    mock: MusicKitApiMock,
) -> None:
    """Library-item bodies key the mapping form by ``universalLibraryId``."""
    success_song = WebPlaybackCatalogLibrarySong(
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
        "i.abc": WebPlaybackResponseSuccess(song_list=[success_song]),
    }
    mock.endpoints.web_playback = web_playback_dict
    body = json.dumps(
        {"subscriptionAdamId": "s1", "universalLibraryId": "i.abc"}
    ).encode()
    status, parsed = _post(
        mock,
        "https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/webPlayback",
        body,
    )
    assert status == 200
    assert parsed == {
        "songList": [{**_WEB_PLAYBACK_SONG_BODY, "needsPlaybackReporting": True}],
        "status": 0,
    }


def test_web_playback_mapping_form_rejects_library_item_without_universal_library_id(
    mock: MusicKitApiMock,
) -> None:
    web_playback_dict: dict[str, WebPlaybackResponse] = {}
    mock.endpoints.web_playback = web_playback_dict
    body = json.dumps({"subscriptionAdamId": "s1"}).encode()
    with pytest.raises(
        ValueError, match=r"endpoints\.web_playback mapping form has no key"
    ):
        _post(
            mock,
            "https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/webPlayback",
            body,
        )


def test_web_playback_static_form_ignores_missing_universal_library_id(
    mock: MusicKitApiMock,
) -> None:
    mock.endpoints.web_playback = WebPlaybackResponseSuccess(song_list=[])
    body = json.dumps({"subscriptionAdamId": "s1"}).encode()
    status, parsed = _post(
        mock,
        "https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/webPlayback",
        body,
    )
    assert status == 200
    assert parsed == _EMPTY_WEB_PLAYBACK_BODY


def test_web_playback_callable_form_receives_omitted_library_fields_as_none(
    mock: MusicKitApiMock,
) -> None:
    captured: list[WebPlaybackContext] = []

    def fn(ctx: WebPlaybackContext) -> WebPlaybackResponse:
        captured.append(ctx)
        return WebPlaybackResponseSuccess(song_list=[])

    mock.endpoints.web_playback = fn
    body = json.dumps({"subscriptionAdamId": "s1"}).encode()
    _, parsed = _post(
        mock,
        "https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/webPlayback",
        body,
    )
    assert parsed == _EMPTY_WEB_PLAYBACK_BODY
    assert captured == [
        WebPlaybackLibraryItemContext(
            subscription_adam_id="s1",
            universal_library_id=None,
            purchase_adam_id=None,
        )
    ]


def test_web_playback_callable_form_receives_catalog_item_context(
    mock: MusicKitApiMock,
) -> None:
    captured: list[WebPlaybackContext] = []

    def fn(ctx: WebPlaybackContext) -> WebPlaybackResponse:
        captured.append(ctx)
        return WebPlaybackResponseSuccess(song_list=[])

    mock.endpoints.web_playback = fn
    body = json.dumps({"salableAdamId": "abc"}).encode()
    _, parsed = _post(
        mock,
        "https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/webPlayback",
        body,
    )
    assert parsed == _EMPTY_WEB_PLAYBACK_BODY
    assert captured == [WebPlaybackCatalogItemContext(salable_adam_id="abc")]


def test_web_playback_callable_form_receives_library_item_context(
    mock: MusicKitApiMock,
) -> None:
    captured: list[WebPlaybackContext] = []

    def fn(ctx: WebPlaybackContext) -> WebPlaybackResponse:
        captured.append(ctx)
        return WebPlaybackResponseSuccess(song_list=[])

    mock.endpoints.web_playback = fn
    body = json.dumps(
        {
            "purchaseAdamId": "p1",
            "subscriptionAdamId": "c1",
            "universalLibraryId": "i.abc",
        }
    ).encode()
    _, parsed = _post(
        mock,
        "https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/webPlayback",
        body,
    )
    assert parsed == _EMPTY_WEB_PLAYBACK_BODY
    assert captured == [
        WebPlaybackLibraryItemContext(
            subscription_adam_id="c1",
            universal_library_id="i.abc",
            purchase_adam_id="p1",
        )
    ]


# --- _resolve_with_context: static form for continuous_stations ------------------


def test_continuous_stations_static_form(
    mock: MusicKitApiMock, station: Station
) -> None:
    """``endpoints.continuous_stations = <response>`` (no callable) is the static form."""
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
    assert parsed == _CONTINUOUS_STATION_BODY


def test_continuous_stations_callable_receives_context(
    mock: MusicKitApiMock, station: Station
) -> None:
    captured: list[int] = []

    def fn(ctx: ContinuousStationsContext) -> ContinuousStationsResponse:
        captured.append(len(ctx.seeds or []))
        return ContinuousStationsResponseSuccess(
            continuous_station=ContinuousStation(station=station, tracks=None)
        )

    mock.endpoints.continuous_stations = fn
    body = json.dumps(
        {"data": [{"id": "1", "type": "songs"}, {"id": "2", "type": "songs"}]}
    ).encode()
    _, parsed = _post(
        mock, "https://api.music.apple.com/v1/me/stations/continuous", body
    )
    assert parsed == _CONTINUOUS_STATION_BODY
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
    s_a, body_a = _post(
        mock,
        "https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/acquireWebPlaybackLicense",
        a,
    )
    s_b, body_b = _post(
        mock,
        "https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/acquireWebPlaybackLicense",
        b,
    )
    assert s_a == s_b == 200
    assert body_a == {"license": "Z29vZA==", "errorCode": 0, "status": 0}
    assert body_b == {"license": "", "errorCode": -1017, "status": -1017}
