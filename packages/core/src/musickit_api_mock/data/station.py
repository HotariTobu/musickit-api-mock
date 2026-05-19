"""Catalog radio station resource."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from musickit_api_mock.data.lookup import LookupContext, _lookup_source
from musickit_api_mock.data.primitives.artwork import Artwork
from musickit_api_mock.data.primitives.editorial_notes import EditorialNotes


@dataclass
class Station:
    """Apple Music catalog radio station."""

    name: str
    artwork: Artwork
    is_live: bool
    media_kind: Literal["audio", "video"]
    url: str
    is_tracks_station: bool
    has_drm: bool
    kind: str
    radio_url: str
    requires_subscription: bool
    editorial_notes: EditorialNotes | None = None
    streaming_radio_sub_type: Literal["Episode", "Shoutcast"] | None = None
    station_provider_name: str | None = None
    radio_show_id: str | None = None


type StationsSource = (
    dict[str, Station] | Callable[[LookupContext], Station | None] | None
)


class _StationResolver:
    """Library-internal lookup over ``DataSources.stations``."""

    def __init__(self, get_source: Callable[[], StationsSource]) -> None:
        """Bind to the ``DataSources.stations`` source via a callback."""
        self._get_source = get_source

    def get(self, context: LookupContext) -> Station | None:
        """Return the station for ``context.id`` or ``None`` if absent."""
        return _lookup_source(self._get_source(), "data.stations", context)
