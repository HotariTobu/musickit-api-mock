"""Catalog album resource."""

from collections.abc import Callable
from dataclasses import dataclass

from musickit_api_mock.data.lookup import LookupContext, _lookup_source
from musickit_api_mock.data.primitives.artwork import Artwork
from musickit_api_mock.data.primitives.editorial_notes import EditorialNotes


@dataclass
class Album:
    """Apple Music catalog album.

    ``track_ids`` and ``artist_ids`` carry the album's composition by id; the
    library resolves those into full track/artist resources at response time.
    ``editorial_artwork`` carries treatment-keyed artworks emitted only when
    a request asks for them via ``?extend=editorialArtwork``.
    """

    name: str
    artist_name: str
    artwork: Artwork
    genre_names: list[str]
    track_count: int
    is_compilation: bool
    is_complete: bool
    is_mastered_for_itunes: bool
    is_single: bool
    is_prerelease: bool
    audio_traits: list[str]
    url: str
    release_date: str | None = None
    copyright: str | None = None
    record_label: str | None = None
    upc: str | None = None
    track_ids: list[str] | None = None
    artist_ids: list[str] | None = None
    content_rating: str | None = None
    editorial_notes: EditorialNotes | None = None
    editorial_artwork: dict[str, Artwork] | None = None
    genre_ids: list[str] | None = None
    record_label_ids: list[str] | None = None
    library_album_id: str | None = None


type AlbumsSource = dict[str, Album] | Callable[[LookupContext], Album | None] | None


class _AlbumResolver:
    """Library-internal lookup over ``DataSources.albums``."""

    def __init__(self, get_source: Callable[[], AlbumsSource]) -> None:
        """Bind to the ``DataSources.albums`` source via a callback."""
        self._get_source = get_source

    def get(self, context: LookupContext) -> Album | None:
        """Return the album for ``context.id`` or ``None`` if absent."""
        return _lookup_source(self._get_source(), "data.albums", context)
