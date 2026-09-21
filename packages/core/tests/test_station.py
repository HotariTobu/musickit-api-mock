from __future__ import annotations

import json

from musickit_api_mock import (
    ContinuousStation,
    ContinuousStationsResponseContentUnsupported,
    ContinuousStationsResponseNoStation,
    ContinuousStationsResponseSuccess,
    ErrorEnvelope,
    MusicKitApiMock,
    Request,
    Station,
    StationNextTracksContext,
)

from tests._expected import ARTWORK_CATALOG, ERROR_ID, SONG


def test_s01_next_tracks_default_limit_2(mock: MusicKitApiMock) -> None:
    mock.endpoints.station_next_tracks = {"ra.978194965": ["1"]}
    resp = mock.handle_request(
        Request(
            method="POST",
            url="https://api.music.apple.com/v1/me/stations/next-tracks/ra.978194965",
            headers={},
            body=b"",
        )
    )
    assert resp is not None
    assert resp.status == 200
    assert json.loads(resp.body) == {"data": [SONG]}


def test_s01_next_tracks_callable_with_context(mock: MusicKitApiMock) -> None:
    captured: list[int] = []

    def fn(ctx: StationNextTracksContext) -> list[str]:
        captured.append(ctx.limit)
        return ["1"]

    mock.endpoints.station_next_tracks = fn
    resp = mock.handle_request(
        Request(
            method="POST",
            url="https://api.music.apple.com/v1/me/stations/next-tracks/ra.978194965?limit=5",
            headers={},
            body=b"",
        )
    )
    assert resp is not None
    assert json.loads(resp.body) == {"data": [SONG]}
    assert captured == [5]


def test_s01_invalid_limit_400(mock: MusicKitApiMock) -> None:
    mock.endpoints.station_next_tracks = {"ra.978194965": ["1"]}
    resp = mock.handle_request(
        Request(
            method="POST",
            url="https://api.music.apple.com/v1/me/stations/next-tracks/ra.978194965?limit=20",
            headers={},
            body=b"",
        )
    )
    assert resp is not None
    assert resp.status == 400
    assert json.loads(resp.body) == {
        "errors": [
            {
                "id": ERROR_ID,
                "title": "Invalid Parameter Value",
                "detail": "Value must be an integer less than or equal to 10, but was: 20",
                "status": "400",
                "code": "40005",
                "source": {"parameter": "limit"},
            }
        ]
    }


_CONTINUOUS_STATION = {
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
}


def _post_continuous(mock: MusicKitApiMock) -> tuple[int, object]:
    body = json.dumps({"data": [{"id": "1", "type": "songs"}]}).encode()
    resp = mock.handle_request(
        Request(
            method="POST",
            url="https://api.music.apple.com/v1/me/stations/continuous?with=tracks",
            headers={},
            body=body,
        )
    )
    assert resp is not None
    return resp.status, json.loads(resp.body)


def test_s02_continuous(mock: MusicKitApiMock, station: Station) -> None:
    mock.endpoints.continuous_stations = lambda _: ContinuousStationsResponseSuccess(
        continuous_station=ContinuousStation(station=station, tracks=["1"])
    )
    status, body = _post_continuous(mock)
    assert status == 200
    assert body == {"results": {"station": _CONTINUOUS_STATION, "tracks": [SONG]}}


def test_s02_continuous_content_unsupported_emits_errors_envelope(
    mock: MusicKitApiMock,
) -> None:
    mock.endpoints.continuous_stations = ContinuousStationsResponseContentUnsupported(
        errors=[
            ErrorEnvelope(
                code="40004",
                title="Bad Request",
                status="400",
                detail="content unsupported",
            )
        ]
    )
    status, body = _post_continuous(mock)
    assert status == 200
    assert body == {
        "errors": [
            {
                "id": ERROR_ID,
                "code": "40004",
                "title": "Bad Request",
                "status": "400",
                "detail": "content unsupported",
            }
        ]
    }


def test_s02_continuous_no_station_emits_no_station_shape(
    mock: MusicKitApiMock,
) -> None:
    mock.endpoints.continuous_stations = ContinuousStationsResponseNoStation()
    status, body = _post_continuous(mock)
    assert status == 200
    assert body == {"results": {}}
