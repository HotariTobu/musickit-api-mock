"""Library song resource."""

from collections.abc import Callable
from dataclasses import dataclass

from musickit_api_mock.data.lookup import LookupContext, _lookup_source
from musickit_api_mock.data.primitives.artwork import Artwork


@dataclass
class LibrarySong:
    """User-library song. ``catalog_id`` links back to the catalog song if known."""

    name: str
    artist_name: str
    artwork: Artwork
    duration_ms: int
    genre_names: list[str]
    has_lyrics: bool
    album_name: str | None = None
    disc_number: int | None = None
    track_number: int | None = None
    release_date: str | None = None
    catalog_id: str | None = None
    album_ids: list[str] | None = None
    artist_ids: list[str] | None = None


type LibrarySongsSource = (
    dict[str, LibrarySong] | Callable[[LookupContext], LibrarySong | None] | None
)


class _LibrarySongResolver:
    """Library-internal lookup over ``DataSources.library_songs``."""

    def __init__(self, get_source: Callable[[], LibrarySongsSource]) -> None:
        """Bind to the ``DataSources.library_songs`` source via a callback."""
        self._get_source = get_source

    def get(self, context: LookupContext) -> LibrarySong | None:
        """Return the library song for ``context.id`` or ``None`` if absent."""
        return _lookup_source(self._get_source(), "data.library_songs", context)
