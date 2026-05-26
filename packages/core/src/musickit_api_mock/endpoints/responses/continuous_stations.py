"""Responses and context for the continuous-stations endpoint."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from musickit_api_mock.data.station import Station
from musickit_api_mock.json_value import _JSONValue


@dataclass
class StationSeed:
    """Seed item passed to the continuous-stations endpoint.

    Attributes:
        id: Catalog or library id of the seed resource.
        type: Seed resource type — one of ``songs``, ``library-songs``, or
            ``music-videos``.
        container_id: Optional containing resource id (e.g. album id of a
            song seed) when MusicKit JS includes one.
    """

    id: str
    type: Literal["songs", "library-songs", "music-videos"]
    container_id: str | None = None


@dataclass
class ContinuousStation:
    """Result a continuous-stations setter returns.

    Attributes:
        station: The resolved station.
        tracks: Initial follow-up track ids for the station. Leave unset to
            let the mock omit the tracks block.
    """

    station: Station
    tracks: list[str] | None = None


@dataclass
class ContinuousStationsContext:
    """Context for the continuous-stations setter.

    Attributes:
        seeds: Seeds the request specified, or ``None`` when the request
            carried no seeds.
    """

    seeds: list[StationSeed] | None = None


@dataclass
class ErrorEnvelope:
    """One entry in the Apple errors envelope (``body.errors[]``).

    Attributes:
        code: Apple error code string.
        title: Short error title.
        status: HTTP status code carried in the envelope as a string.
        detail: Long-form error detail.
        source: Source object indicating which input triggered the error.
    """

    code: str
    title: str
    status: str
    detail: str | None = None
    source: dict[str, _JSONValue] | None = None


@dataclass
class ContinuousStationsResponseSuccess:
    """200 response carrying the resolved continuous station.

    Attributes:
        continuous_station: The resolved station with optional track ids.
    """

    continuous_station: ContinuousStation


@dataclass
class ContinuousStationsResponseContentUnsupported:
    """Non-empty ``body.errors[]`` that triggers CONTENT_UNSUPPORTED.

    Attributes:
        errors: Error envelopes carried in the response body.
    """

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
