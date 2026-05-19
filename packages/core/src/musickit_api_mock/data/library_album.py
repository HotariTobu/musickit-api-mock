"""Library album resource."""

from collections.abc import Callable
from dataclasses import dataclass

from musickit_api_mock.data.lookup import LookupContext, _lookup_source
from musickit_api_mock.data.primitives.artwork import Artwork


@dataclass
class LibraryAlbum:
    """User-library album.

    ``track_ids`` refs library songs by id; ``artist_ids`` refs library
    artists by id and is emitted in ``relationships.artists`` only when
    ``?include=artists`` is requested. ``catalog_id`` links the library
    album back to its catalog counterpart for ``?include=catalog`` resolution.
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
