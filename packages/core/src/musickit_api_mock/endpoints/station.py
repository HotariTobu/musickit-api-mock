"""Handlers for station next-tracks and continuous-stations endpoints."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from musickit_api_mock.data.lookup import LookupContext
from musickit_api_mock.endpoints.query import _parse_query
from musickit_api_mock.endpoints.responses.account import (
    AccountResponseSuccess,
)
from musickit_api_mock.endpoints.responses.continuous_stations import (
    ContinuousStationsContext,
    ContinuousStationsResponseContentUnsupported,
    ContinuousStationsResponseNoStation,
    ContinuousStationsResponseSuccess,
    StationSeed,
)
from musickit_api_mock.endpoints.responses.station_next_tracks import (
    StationNextTracksContext,
)
from musickit_api_mock.endpoints.schema import (
    _batch_envelope,
    _continuous_station_envelope,
    _continuous_stations_errors_envelope,
    _continuous_stations_no_station_envelope,
    _limit_exceeded_envelope,
    _parameter_invalid_envelope,
    _song_resource,
)
from musickit_api_mock.transport.response_builders import _json_response

if TYPE_CHECKING:
    from musickit_api_mock.data.song import Song
    from musickit_api_mock.json_value import _JSONValue
    from musickit_api_mock.mock import MusicKitApiMock
    from musickit_api_mock.transport.http import Request, Response


_NEXT_TRACKS_DEFAULT_LIMIT = 2
_NEXT_TRACKS_MAX_LIMIT = 10

_CONTINUOUS_TRACKS_MIN_LIMIT = 1
_CONTINUOUS_TRACKS_MAX_LIMIT = 10
_CONTINUOUS_TRACKS_LIMIT_PARAM = "limit[results:tracks]"


def _parse_continuous_tracks_limit(
    q: dict[str, list[str]],
) -> tuple[int | None, Response | None]:
    """Parse ``?limit[results:tracks]=N`` for continuous-stations.

    Apple distinguishes 4 cases: missing/empty (use default), non-integer
    (400 ``Value must be an integer``), underflow <1 (400 ``Value must be
    an integer greater than or equal to 1``), overflow >10 (400 ``Value
    must be an integer less than or equal to 10``).
    """
    raw = q.get(_CONTINUOUS_TRACKS_LIMIT_PARAM, [None])[-1]
    if raw is None or raw == "":
        return None, None
    try:
        value = int(raw)
    except ValueError:
        return None, _json_response(
            _parameter_invalid_envelope(
                _CONTINUOUS_TRACKS_LIMIT_PARAM, "Value must be an integer"
            ),
            status=400,
        )
    if value < _CONTINUOUS_TRACKS_MIN_LIMIT:
        return None, _json_response(
            _parameter_invalid_envelope(
                _CONTINUOUS_TRACKS_LIMIT_PARAM,
                "Value must be an integer greater than or equal to 1",
            ),
            status=400,
        )
    if value > _CONTINUOUS_TRACKS_MAX_LIMIT:
        return None, _json_response(
            _parameter_invalid_envelope(
                _CONTINUOUS_TRACKS_LIMIT_PARAM,
                f"Value must be an integer less than or equal to {_CONTINUOUS_TRACKS_MAX_LIMIT}",
            ),
            status=400,
        )
    return value, None


def _parse_next_tracks_limit(
    q: dict[str, list[str]],
) -> tuple[int | None, Response | None]:
    """Parse ``?limit=N`` for station next-tracks.

    Apple distinguishes 4 cases: missing/empty (use default), non-integer
    (400 ``Value must be an integer``), underflow <1 (400 ``Value must be
    an integer greater than or equal to 1``), overflow >10 (400 ``Value
    must be an integer less than or equal to 10, but was: N``).
    """
    raw = q.get("limit", [None])[-1]
    if raw is None or raw == "":
        return None, None
    try:
        value = int(raw)
    except ValueError:
        return None, _json_response(
            _parameter_invalid_envelope("limit", "Value must be an integer"),
            status=400,
        )
    if value < 1:
        return None, _json_response(
            _parameter_invalid_envelope(
                "limit", "Value must be an integer greater than or equal to 1"
            ),
            status=400,
        )
    if value > _NEXT_TRACKS_MAX_LIMIT:
        return None, _json_response(
            _limit_exceeded_envelope(_NEXT_TRACKS_MAX_LIMIT, value), status=400
        )
    return value, None


def _handle_next_tracks(
    mock: MusicKitApiMock, req: Request, station_id: str
) -> Response:
    q = _parse_query(req.url)
    limit, err = _parse_next_tracks_limit(q)
    if err is not None:
        return err
    if limit is None:
        limit = _NEXT_TRACKS_DEFAULT_LIMIT

    song_ids = mock._endpoint_resolver.station_next_tracks(
        StationNextTracksContext(station_id=station_id, limit=limit)
    )
    song_ids = song_ids[:limit]
    sf = _account_storefront(mock)
    data: list[dict[str, _JSONValue]] = []
    for sid in song_ids:
        song = mock._data_resolver.song.get(LookupContext(sid, None))
        if song is None:
            continue
        data.append(_song_resource(sf, sid, song, include_play_assets=True))
    return _json_response(_batch_envelope(data))


def _account_storefront(mock: MusicKitApiMock) -> str:
    resp = mock._endpoint_resolver.account()
    if isinstance(resp, AccountResponseSuccess):
        return resp.account.subscription_storefront
    raise ValueError("account is not in a success state")


def _handle_continuous(mock: MusicKitApiMock, req: Request) -> Response:
    q = _parse_query(req.url)
    tracks_limit, err = _parse_continuous_tracks_limit(q)
    if err is not None:
        return err

    body_text = (req.body or b"").decode("utf-8", errors="replace") or "{}"
    try:
        body = json.loads(body_text)
    except json.JSONDecodeError:
        body = {}
    raw_seeds = body.get("data", []) if isinstance(body, dict) else []
    seeds: list[StationSeed] = []
    for s in raw_seeds:
        if not isinstance(s, dict):
            continue
        sid = s.get("id")
        stype = s.get("type")
        if sid is None or stype not in ("songs", "library-songs", "music-videos"):
            continue
        container_id = None
        meta = s.get("meta")
        if isinstance(meta, dict):
            container = meta.get("container")
            if isinstance(container, dict):
                container_id = container.get("id")
        seeds.append(StationSeed(id=str(sid), type=stype, container_id=container_id))

    resp = mock._endpoint_resolver.continuous_stations(
        ContinuousStationsContext(seeds=seeds)
    )
    if isinstance(resp, ContinuousStationsResponseSuccess):
        with_raw = q.get("with", [""])[-1]
        with_tracks = "tracks" in {p.strip() for p in with_raw.split(",") if p.strip()}
        sf = _account_storefront(mock)
        resolved_tracks: list[tuple[str, Song]] | None = None
        if with_tracks:
            track_ids = resp.continuous_station.tracks
            if track_ids is not None:
                if tracks_limit is not None:
                    track_ids = track_ids[:tracks_limit]
                resolved_tracks = []
                for tid in track_ids:
                    song = mock._data_resolver.song.get(LookupContext(tid, None))
                    if song is not None:
                        resolved_tracks.append((tid, song))
        return _json_response(
            _continuous_station_envelope(
                resp.continuous_station,
                sf,
                tracks=resolved_tracks,
            )
        )
    if isinstance(resp, ContinuousStationsResponseContentUnsupported):
        return _json_response(_continuous_stations_errors_envelope(resp.errors))
    if isinstance(resp, ContinuousStationsResponseNoStation):
        return _json_response(_continuous_stations_no_station_envelope())
    raise TypeError(f"Unexpected continuous_stations response: {type(resp).__name__}")
