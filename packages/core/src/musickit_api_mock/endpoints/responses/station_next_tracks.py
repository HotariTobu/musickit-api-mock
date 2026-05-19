"""Context and setter type alias for the station next-tracks endpoint."""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class StationNextTracksContext:
    """Context for the station next-tracks setter."""

    station_id: str
    limit: int


type StationNextTracksSetter = (
    dict[str, list[str]] | Callable[[StationNextTracksContext], list[str]] | None
)
