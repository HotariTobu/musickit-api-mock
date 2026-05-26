"""Library album resource."""

from collections.abc import Callable
from dataclasses import dataclass

from musickit_api_mock.data.lookup import LookupContext, _lookup_source
from musickit_api_mock.data.primitives.artwork import Artwork


@dataclass
class LibraryAlbum:
    """User-library album.

    Attributes:
        name: Display title of the album.
        artist_name: Display name of the primary artist.
        artwork: Cover artwork.
        genre_names: Display names of the album's genres.
        track_count: Number of tracks on the album.
        date_added: ISO-8601 timestamp the user added the album to their
            library.
        track_ids: Library song ids on the album.
        artist_ids: Library artist ids credited on the album. Surface in
            ``relationships.artists`` only when ``?include=artists`` is
            requested.
        release_date: ISO-8601 release date.
        catalog_id: Catalog album id linking back to the catalog counterpart,
            used to resolve ``?include=catalog``.
    """

    name: str
    artist_name: str
    artwork: Artwork
    genre_names: list[str]
    track_count: int
    date_added: str | None = None
    track_ids: list[str] | None = None
    artist_ids: list[str] | None = None
    release_date: str | None = None
    catalog_id: str | None = None


type LibraryAlbumsSource = (
    dict[str, LibraryAlbum] | Callable[[LookupContext], LibraryAlbum | None] | None
)


class _LibraryAlbumResolver:
    """Library-internal lookup over ``DataSources.library_albums``."""

    def __init__(self, get_source: Callable[[], LibraryAlbumsSource]) -> None:
        """Bind to the ``DataSources.library_albums`` source via a callback."""
        self._get_source = get_source

    def get(self, context: LookupContext) -> LibraryAlbum | None:
        """Return the library album for ``context.id`` or ``None`` if absent."""
        return _lookup_source(self._get_source(), "data.library_albums", context)
