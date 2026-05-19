"""Catalog artist resource."""

from collections.abc import Callable
from dataclasses import dataclass

from musickit_api_mock.data.lookup import LookupContext, _lookup_source
from musickit_api_mock.data.primitives.artwork import Artwork


@dataclass
class Artist:
    """Apple Music catalog artist.

    ``album_ids`` carries the artist's discography by id; the library resolves
    them into full album resources at response time.
    """

    name: str
    genre_names: list[str]
    url: str
    artwork: Artwork | None = None
    album_ids: list[str] | None = None
    genre_ids: list[str] | None = None
    music_video_ids: list[str] | None = None
    playlist_ids: list[str] | None = None
    station_id: str | None = None


type ArtistsSource = dict[str, Artist] | Callable[[LookupContext], Artist | None] | None


class _ArtistResolver:
    """Library-internal lookup over ``DataSources.artists``."""

    def __init__(self, get_source: Callable[[], ArtistsSource]) -> None:
        """Bind to the ``DataSources.artists`` source via a callback."""
        self._get_source = get_source

    def get(self, context: LookupContext) -> Artist | None:
        """Return the artist for ``context.id`` or ``None`` if absent."""
        return _lookup_source(self._get_source(), "data.artists", context)
