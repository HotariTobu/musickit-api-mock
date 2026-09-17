"""Library artist resource."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from musickit_api_mock.data.artist import CatalogArtist
from musickit_api_mock.data.lookup import (
    LookupContext,
    _dangling_catalog_id,
    _lookup_source,
)


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
    """Library-internal lookup over ``DataSources.library_artists``.

    A catalog-linked artist resolves only when its catalog counterpart
    exists; a dangling ``catalog_id`` raises on every lookup.
    """

    def __init__(
        self,
        get_source: Callable[[], LibraryArtistsSource],
        get_catalog: Callable[[LookupContext], CatalogArtist | None],
    ) -> None:
        """Bind to the ``DataSources.library_artists`` source and the catalog artist lookup."""
        self._get_source = get_source
        self._get_catalog = get_catalog

    def get(self, context: LookupContext) -> LibraryArtist | None:
        """Return the library artist for ``context.id`` or ``None`` if absent."""
        artist = _lookup_source(self._get_source(), "data.library_artists", context)
        if isinstance(artist, CatalogLibraryArtist):
            self.catalog_for(context, artist)
        return artist

    def catalog_for(
        self, context: LookupContext, artist: CatalogLibraryArtist
    ) -> CatalogArtist:
        """Return the catalog artist ``artist`` is linked to, raising if it has no entry."""
        catalog = self._get_catalog(LookupContext(artist.catalog_id, context.locale))
        if catalog is None:
            raise _dangling_catalog_id(
                "data.library_artists", context.id, "data.artists", artist.catalog_id
            )
        return catalog
