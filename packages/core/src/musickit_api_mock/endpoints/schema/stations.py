"""Station resource and continuous-stations envelope builders."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.endpoints.schema.builders import (
    _artwork,
    _editorial_notes,
    _stable_hash,
    _strip_none,
)
from musickit_api_mock.endpoints.schema.play_params import _play_params_station
from musickit_api_mock.endpoints.schema.songs import _song_resource

if TYPE_CHECKING:
    from musickit_api_mock.data.song import Song
    from musickit_api_mock.data.station import Station
    from musickit_api_mock.endpoints.responses.continuous_stations import (
        ContinuousStation,
    )
    from musickit_api_mock.json_value import _JSONValue


def _station_resource(
    sf: str,
    station_id: str,
    station: Station,
    *,
    relationships: dict[str, _JSONValue] | None = None,
) -> dict[str, _JSONValue]:
    attrs: dict[str, _JSONValue] = _strip_none(
        {
            "artwork": _artwork(station.artwork),
            "editorialNotes": (
                _editorial_notes(station.editorial_notes)
                if station.editorial_notes is not None
                else None
            ),
            "isLive": station.is_live,
            "kind": station.kind,
            "mediaKind": station.media_kind,
            "name": station.name,
            "playParams": _play_params_station(station_id, station),
            "radioUrl": station.radio_url,
            "requiresSubscription": station.requires_subscription,
            "stationProviderName": station.station_provider_name,
            "streamingRadioSubType": station.streaming_radio_sub_type,
            "supportedDrms": (
                ["fairplay", "playready", "widevine"] if station.has_drm else None
            ),
            "url": station.url,
        }
    )
    out: dict[str, _JSONValue] = {
        "id": station_id,
        "type": "stations",
        "href": f"/v1/catalog/{sf}/stations/{station_id}",
        "attributes": attrs,
    }
    if relationships is not None:
        out["relationships"] = relationships
    return out


def _continuous_station_envelope(
    cs: ContinuousStation,
    sf: str,
    *,
    tracks: list[tuple[str, Song]] | None,
) -> dict[str, _JSONValue]:
    station_id = _stable_hash("continuous", cs.station.name)
    station_dict = {
        "id": station_id,
        "type": "stations",
        "href": f"/v1/catalog/{sf}/stations/{station_id}",
        "attributes": _strip_none(
            {
                "name": cs.station.name,
                "artwork": _artwork(cs.station.artwork),
                "isLive": cs.station.is_live,
                "kind": cs.station.kind,
                "mediaKind": cs.station.media_kind,
                "playParams": _play_params_station(station_id, cs.station),
                "radioUrl": cs.station.radio_url,
                "requiresSubscription": cs.station.requires_subscription,
                "url": cs.station.url,
            }
        ),
    }
    results: dict[str, _JSONValue] = {"station": station_dict}
    if tracks is not None:
        results["tracks"] = [
            _song_resource(sf, tid, song, include_play_assets=True)
            for tid, song in tracks
        ]
    return {"results": results}
