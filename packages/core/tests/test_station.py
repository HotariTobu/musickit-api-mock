from __future__ import annotations

import json
from typing import TYPE_CHECKING, cast

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

if TYPE_CHECKING:
    from tests._apple_response import _AppleResponse


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
    body = json.loads(resp.body)
    assert len(body["data"]) == 1
    assert body["data"][0]["id"] == "1"


def test_s01_next_tracks_callable_with_context(mock: MusicKitApiMock) -> None:
    captured: list[int] = []

    def fn(ctx: StationNextTracksContext) -> list[str]:
        captured.append(ctx.limit)
        return ["1"]

    mock.endpoints.station_next_tracks = fn
    mock.handle_request(
        Request(
            method="POST",
            url="https://api.music.apple.com/v1/me/stations/next-tracks/ra.978194965?limit=5",
            headers={},
            body=b"",
        )
    )
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


def test_s02_continuous(mock: MusicKitApiMock) -> None:
    stations = cast("dict[str, Station]", mock.data.stations)
    station = stations["ra.978194965"]
    mock.endpoints.continuous_stations = lambda _: ContinuousStationsResponseSuccess(
        continuous_station=ContinuousStation(station=station, tracks=["1"])
    )
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
    assert resp.status == 200
    parsed = json.loads(resp.body)
    assert "station" in parsed["results"]
    assert "tracks" in parsed["results"]


def _post_continuous(mock: MusicKitApiMock) -> tuple[int, _AppleResponse]:
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
    assert body["errors"][0]["code"] == "40004"


def test_s02_continuous_no_station_emits_no_station_shape(
    mock: MusicKitApiMock,
) -> None:
    mock.endpoints.continuous_stations = ContinuousStationsResponseNoStation()
    status, body = _post_continuous(mock)
    assert status == 200
    results = body.get("results", {})
    assert "station" not in results
