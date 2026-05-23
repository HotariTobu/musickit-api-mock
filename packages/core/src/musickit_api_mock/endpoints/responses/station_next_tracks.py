"""Context and setter type alias for the station next-tracks endpoint."""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class StationNextTracksContext:
    """Context for the station next-tracks setter.

    Attributes:
        station_id: Catalog station id the next-tracks request is for.
        limit: Maximum number of follow-up tracks the request asked for.
    """

    station_id: str
    limit: int


type StationNextTracksSetter = (
    dict[str, list[str]] | Callable[[StationNextTracksContext], list[str]] | None
)
