"""Responses and context for the continuous-stations endpoint."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from musickit_api_mock.data.station import Station
from musickit_api_mock.json_value import _JSONValue


@dataclass
class StationSeed:
    """Seed item passed to the continuous-stations endpoint."""

    id: str
    type: Literal["songs", "library-songs", "music-videos"]
    container_id: str | None = None


@dataclass
class ContinuousStation:
    """Result a continuous-stations setter returns: a Station plus its track ids."""

    station: Station
    tracks: list[str] | None = None


@dataclass
class ContinuousStationsContext:
    """Context for the continuous-stations setter."""

    seeds: list[StationSeed] | None = None


@dataclass
class ErrorEnvelope:
    """One entry in the Apple errors envelope (``body.errors[]``)."""

    code: str
    title: str
    status: str
    detail: str | None = None
    source: dict[str, _JSONValue] | None = None


@dataclass
class ContinuousStationsResponseSuccess:
    """200 response carrying the resolved continuous station."""

    continuous_station: ContinuousStation


@dataclass
class ContinuousStationsResponseContentUnsupported:
    """Non-empty ``body.errors[]`` that triggers CONTENT_UNSUPPORTED."""

    errors: list[ErrorEnvelope]


@dataclass
class ContinuousStationsResponseNoStation:
    """``results.station`` missing that triggers CONTENT_UNAVAILABLE."""


ContinuousStationsResponse = (
    ContinuousStationsResponseSuccess
    | ContinuousStationsResponseContentUnsupported
    | ContinuousStationsResponseNoStation
)


type ContinuousStationsSetter = (
    ContinuousStationsResponse
    | Callable[[ContinuousStationsContext], ContinuousStationsResponse]
    | None
)
