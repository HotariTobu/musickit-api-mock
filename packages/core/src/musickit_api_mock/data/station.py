"""Catalog radio station resource."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from musickit_api_mock.data.lookup import LookupContext, _lookup_source
from musickit_api_mock.data.primitives.artwork import Artwork
from musickit_api_mock.data.primitives.editorial_notes import EditorialNotes


@dataclass
class Station:
    """Apple Music catalog radio station.

    Attributes:
        name: Display name of the station.
        artwork: Hero artwork for the station.
        is_live: Whether the station is a live broadcast.
        media_kind: Media kind — ``audio`` or ``video``.
        url: Station landing-page URL on Apple Music.
        is_tracks_station: Whether the station plays a track-driven playlist.
        has_drm: Whether the station's playback is DRM-protected.
        kind: Apple-specific station-kind tag.
        radio_url: HLS URL the station streams from.
        requires_subscription: Whether playback requires an Apple Music
            subscription.
        editorial_notes: Editorial copy shown alongside the station.
        streaming_radio_sub_type: Streaming sub-type — ``Episode`` for
            episodic broadcasts, ``Shoutcast`` for Shoutcast streams.
        station_provider_name: Display name of the third-party provider.
        radio_show_id: Catalog id of the linked radio show.
    """

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
