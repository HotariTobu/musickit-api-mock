"""Library album resource."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from musickit_api_mock.data.lookup import (
    LookupContext,
    _dangling_catalog_id,
    _lookup_source,
)
from musickit_api_mock.data.primitives.artwork import Artwork


@dataclass
class CatalogLibraryAlbum:
    """User-library album linked to an Apple Music catalog album.

    Attributes:
        name: Display title of the album.
        artist_name: Display name of the primary artist.
        artwork: Cover artwork.
        genre_names: Display names of the album's genres.
        track_count: Number of tracks on the album.
        catalog_id: Catalog album id the library album is linked to,
            resolved for ``?include=catalog``.
        date_added: ISO-8601 timestamp the user added the album to their
            library.
        track_ids: Library song ids on the album.
        artist_ids: Library artist ids credited on the album. Surface in
            ``relationships.artists`` only when ``?include=artists`` is
            requested.
        release_date: ISO-8601 release date.
    """

    name: str
    artist_name: str
    artwork: Artwork
    genre_names: list[str]
    track_count: int
    catalog_id: str
    date_added: str | None = None
    track_ids: list[str] | None = None
    artist_ids: list[str] | None = None
    release_date: str | None = None


@dataclass
class UploadedLibraryAlbum:
    """User-library album made of uploaded songs, with no catalog counterpart.

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
    """

    name: str
    artist_name: str
    artwork: Artwork
    genre_names: list[str]
    track_count: int
    date_added: str | None = None
    track_ids: list[str] | None = None
    artist_ids: list[str] | None = None


LibraryAlbum = CatalogLibraryAlbum | UploadedLibraryAlbum

type LibraryAlbumsSource = (
    Mapping[str, LibraryAlbum] | Callable[[LookupContext], LibraryAlbum | None] | None
)


class _LibraryAlbumResolver:
    """Library-internal lookup over ``DataSources.library_albums``.

    A catalog-linked album resolves only when its catalog counterpart
    exists; a dangling ``catalog_id`` raises on every lookup.
    """

    def __init__(
        self,
        get_source: Callable[[], LibraryAlbumsSource],
        get_catalog: Callable[[LookupContext], object | None],
    ) -> None:
        """Bind to the ``DataSources.library_albums`` source and the catalog album lookup."""
        self._get_source = get_source
        self._get_catalog = get_catalog

    def get(self, context: LookupContext) -> LibraryAlbum | None:
        """Return the library album for ``context.id`` or ``None`` if absent."""
        album = _lookup_source(self._get_source(), "data.library_albums", context)
        if isinstance(album, CatalogLibraryAlbum) and (
            self._get_catalog(LookupContext(album.catalog_id, context.locale)) is None
        ):
            raise _dangling_catalog_id(
                "data.library_albums", context.id, "data.albums", album.catalog_id
            )
        return album
