"""Library song resource."""

from collections.abc import Callable
from dataclasses import dataclass

from musickit_api_mock.data.lookup import LookupContext, _lookup_source
from musickit_api_mock.data.primitives.artwork import Artwork


@dataclass
class LibrarySong:
    """User-library song.

    Attributes:
        name: Display title of the song.
        artist_name: Display name of the primary artist.
        artwork: Cover artwork.
        duration_ms: Duration in milliseconds.
        genre_names: Display names of the song's genres.
        has_lyrics: Whether lyrics are available.
        album_name: Display name of the album the song belongs to.
        disc_number: Disc number when part of a multi-disc album.
        track_number: Track number within the album.
        release_date: ISO-8601 release date.
        catalog_id: Catalog song id linking back to the catalog counterpart,
            used to resolve ``?include=catalog``.
        album_ids: Library album ids the song belongs to.
        artist_ids: Library artist ids credited on the song.
    """

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
