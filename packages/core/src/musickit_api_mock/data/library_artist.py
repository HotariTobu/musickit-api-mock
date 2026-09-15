"""Library artist resource."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from musickit_api_mock.data.lookup import LookupContext, _lookup_source


@dataclass
class CatalogLibraryArtist:
    """User-library artist linked to an Apple Music catalog artist.

    Attributes:
        name: Display name of the artist.
        catalog_id: Catalog artist id the library artist is linked to,
            resolved for ``?include=catalog``.
        album_ids: Library album ids credited to the artist.
    """

    name: str
    catalog_id: str
    album_ids: list[str] | None = None


@dataclass
class UploadedLibraryArtist:
    """User-library artist known only from uploaded songs, with no catalog counterpart.

    Attributes:
        name: Display name of the artist.
        album_ids: Library album ids credited to the artist.
    """

    name: str
    album_ids: list[str] | None = None


LibraryArtist = CatalogLibraryArtist | UploadedLibraryArtist

type LibraryArtistsSource = (
    Mapping[str, LibraryArtist] | Callable[[LookupContext], LibraryArtist | None] | None
)


class _LibraryArtistResolver:
    """Library-internal lookup over ``DataSources.library_artists``."""

    def __init__(self, get_source: Callable[[], LibraryArtistsSource]) -> None:
        """Bind to the ``DataSources.library_artists`` source via a callback."""
        self._get_source = get_source

    def get(self, context: LookupContext) -> LibraryArtist | None:
        """Return the library artist for ``context.id`` or ``None`` if absent."""
        return _lookup_source(self._get_source(), "data.library_artists", context)
