"""Failure-variant emission for the four ``/v1/play/assets`` setters.

Live-audio / live-video / broadcast share the same five non-success
variants (Success, EmptyAssets, ServerError, SubscriptionError,
AccessDenied, ContentUnavailable). Each variant maps to a distinct HTTP
status and body that callers downstream of MusicKit JS branch on, so the
variant → response pairing is the user-facing contract being verified.
"""

from __future__ import annotations

import json

from musickit_api_mock import (
    MusicKitApiMock,
    PlayAssetsBroadcastResponseAccessDenied,
    PlayAssetsBroadcastResponseContentUnavailable,
    PlayAssetsBroadcastResponseEmptyAssets,
    PlayAssetsBroadcastResponseServerError,
    PlayAssetsBroadcastResponseSubscriptionError,
    PlayAssetsLiveAudioResponseAccessDenied,
    PlayAssetsLiveAudioResponseContentUnavailable,
    PlayAssetsLiveAudioResponseEmptyAssets,
    PlayAssetsLiveAudioResponseServerError,
    PlayAssetsLiveVideoResponseAccessDenied,
    PlayAssetsLiveVideoResponseContentUnavailable,
    PlayAssetsLiveVideoResponseEmptyAssets,
    PlayAssetsLiveVideoResponseServerError,
    PlayAssetsLiveVideoResponseSubscriptionError,
    Request,
    Station,
)

from tests._expected import ERROR_ID

_EMPTY_ASSETS_BODY = {"results": {"assets": []}}

_ACCESS_DENIED_BODY = {
    "errors": [
        {
            "id": ERROR_ID,
            "code": "40300",
            "title": "Forbidden",
            "detail": "Access denied",
            "status": "403",
        }
    ]
}

_SUBSCRIPTION_ERROR_BODY = {
    "errors": [
        {
            "id": ERROR_ID,
            "code": "40303",
            "title": "Forbidden",
            "detail": "Subscription required",
            "status": "403",
        }
    ]
}

_CONTENT_UNAVAILABLE_BODY = {
    "errors": [
        {
            "id": ERROR_ID,
            "title": "Not Found",
            "status": "404",
        }
    ]
}


def _live_audio_request(station_id: str) -> Request:
    return Request(
        method="GET",
        url=f"https://api.music.apple.com/v1/play/assets?id={station_id}&kind=radioStation&keyFormat=web",
        headers={},
        body=None,
    )


def test_play_assets_live_audio_empty_assets_returns_200_with_no_assets(
    mock: MusicKitApiMock,
) -> None:
    mock.endpoints.play_assets_live_audio = PlayAssetsLiveAudioResponseEmptyAssets()
    resp = mock.handle_request(_live_audio_request("ra.978194965"))
    assert resp is not None
    assert resp.status == 200
    assert json.loads(resp.body) == _EMPTY_ASSETS_BODY


def test_play_assets_live_audio_server_error_returns_5xx(
    mock: MusicKitApiMock,
) -> None:
    mock.endpoints.play_assets_live_audio = PlayAssetsLiveAudioResponseServerError()
    resp = mock.handle_request(_live_audio_request("ra.978194965"))
    assert resp is not None
    assert resp.status >= 500
    assert resp.body == b""


def test_play_assets_live_audio_access_denied_returns_403(
    mock: MusicKitApiMock,
) -> None:
    mock.endpoints.play_assets_live_audio = PlayAssetsLiveAudioResponseAccessDenied()
    resp = mock.handle_request(_live_audio_request("ra.978194965"))
    assert resp is not None
    assert resp.status == 403
    assert json.loads(resp.body) == _ACCESS_DENIED_BODY


def test_play_assets_live_audio_content_unavailable_returns_404(
    mock: MusicKitApiMock,
) -> None:
    mock.endpoints.play_assets_live_audio = (
        PlayAssetsLiveAudioResponseContentUnavailable()
    )
    resp = mock.handle_request(_live_audio_request("ra.978194965"))
    assert resp is not None
    assert resp.status == 404
    assert json.loads(resp.body) == _CONTENT_UNAVAILABLE_BODY


def _live_video_request(station_id: str) -> Request:
    return Request(
        method="GET",
        url=f"https://api.music.apple.com/v1/play/assets?id={station_id}&kind=radioStation&keyFormat=web",
        headers={},
        body=None,
    )


def _add_video_station(
    mock: MusicKitApiMock, station: Station, station_id: str
) -> None:
    mock.data.stations = {
        "ra.978194965": station,
        station_id: Station(
            name="Live Video",
            artwork=station.artwork,
            is_live=True,
            media_kind="video",
            url="https://example.com/x",
            is_tracks_station=False,
            has_drm=True,
            kind="radio",
            radio_url="https://example.com/x",
            requires_subscription=True,
        ),
    }


def test_play_assets_live_video_empty_assets_returns_200(
    mock: MusicKitApiMock, station: Station
) -> None:
    _add_video_station(mock, station, "ra.video")
    mock.endpoints.play_assets_live_video = PlayAssetsLiveVideoResponseEmptyAssets()
    resp = mock.handle_request(_live_video_request("ra.video"))
    assert resp is not None
    assert resp.status == 200
    assert json.loads(resp.body) == _EMPTY_ASSETS_BODY


def test_play_assets_live_video_server_error_returns_5xx(
    mock: MusicKitApiMock, station: Station
) -> None:
    _add_video_station(mock, station, "ra.video")
    mock.endpoints.play_assets_live_video = PlayAssetsLiveVideoResponseServerError()
    resp = mock.handle_request(_live_video_request("ra.video"))
    assert resp is not None
    assert resp.status >= 500
    assert resp.body == b""


def test_play_assets_live_video_subscription_error_returns_403(
    mock: MusicKitApiMock, station: Station
) -> None:
    _add_video_station(mock, station, "ra.video")
    mock.endpoints.play_assets_live_video = (
        PlayAssetsLiveVideoResponseSubscriptionError()
    )
    resp = mock.handle_request(_live_video_request("ra.video"))
    assert resp is not None
    assert resp.status == 403
    assert json.loads(resp.body) == _SUBSCRIPTION_ERROR_BODY


def test_play_assets_live_video_access_denied_returns_403(
    mock: MusicKitApiMock, station: Station
) -> None:
    _add_video_station(mock, station, "ra.video")
    mock.endpoints.play_assets_live_video = PlayAssetsLiveVideoResponseAccessDenied()
    resp = mock.handle_request(_live_video_request("ra.video"))
    assert resp is not None
    assert resp.status == 403
    assert json.loads(resp.body) == _ACCESS_DENIED_BODY


def test_play_assets_live_video_content_unavailable_returns_404(
    mock: MusicKitApiMock, station: Station
) -> None:
    _add_video_station(mock, station, "ra.video")
    mock.endpoints.play_assets_live_video = (
        PlayAssetsLiveVideoResponseContentUnavailable()
    )
    resp = mock.handle_request(_live_video_request("ra.video"))
    assert resp is not None
    assert resp.status == 404
    assert json.loads(resp.body) == _CONTENT_UNAVAILABLE_BODY


def _add_broadcast_station(
    mock: MusicKitApiMock, station: Station, station_id: str
) -> None:
    mock.data.stations = {
        "ra.978194965": station,
        station_id: Station(
            name="BBC",
            artwork=station.artwork,
            is_live=True,
            media_kind="audio",
            url="https://example.com/bbc",
            is_tracks_station=False,
            has_drm=False,
            kind="radio",
            radio_url="https://example.com/bbc",
            requires_subscription=False,
        ),
    }


def _broadcast_request(station_id: str) -> Request:
    return Request(
        method="GET",
        url=f"https://api.music.apple.com/v1/play/assets?id={station_id}&kind=radioStation&keyFormat=web",
        headers={},
        body=None,
    )


def test_play_assets_broadcast_empty_assets_returns_200(
    mock: MusicKitApiMock, station: Station
) -> None:
    _add_broadcast_station(mock, station, "ra.bbc")
    mock.endpoints.play_assets_broadcast = PlayAssetsBroadcastResponseEmptyAssets()
    resp = mock.handle_request(_broadcast_request("ra.bbc"))
    assert resp is not None
    assert resp.status == 200
    assert json.loads(resp.body) == _EMPTY_ASSETS_BODY


def test_play_assets_broadcast_server_error_returns_5xx(
    mock: MusicKitApiMock, station: Station
) -> None:
    _add_broadcast_station(mock, station, "ra.bbc")
    mock.endpoints.play_assets_broadcast = PlayAssetsBroadcastResponseServerError()
    resp = mock.handle_request(_broadcast_request("ra.bbc"))
    assert resp is not None
    assert resp.status >= 500
    assert resp.body == b""


def test_play_assets_broadcast_subscription_error_returns_403(
    mock: MusicKitApiMock, station: Station
) -> None:
    _add_broadcast_station(mock, station, "ra.bbc")
    mock.endpoints.play_assets_broadcast = (
        PlayAssetsBroadcastResponseSubscriptionError()
    )
    resp = mock.handle_request(_broadcast_request("ra.bbc"))
    assert resp is not None
    assert resp.status == 403
    assert json.loads(resp.body) == _SUBSCRIPTION_ERROR_BODY


def test_play_assets_broadcast_access_denied_returns_403(
    mock: MusicKitApiMock, station: Station
) -> None:
    _add_broadcast_station(mock, station, "ra.bbc")
    mock.endpoints.play_assets_broadcast = PlayAssetsBroadcastResponseAccessDenied()
    resp = mock.handle_request(_broadcast_request("ra.bbc"))
    assert resp is not None
    assert resp.status == 403
    assert json.loads(resp.body) == _ACCESS_DENIED_BODY


def test_play_assets_broadcast_content_unavailable_returns_404(
    mock: MusicKitApiMock, station: Station
) -> None:
    _add_broadcast_station(mock, station, "ra.bbc")
    mock.endpoints.play_assets_broadcast = (
        PlayAssetsBroadcastResponseContentUnavailable()
    )
    resp = mock.handle_request(_broadcast_request("ra.bbc"))
    assert resp is not None
    assert resp.status == 404
    assert json.loads(resp.body) == _CONTENT_UNAVAILABLE_BODY
