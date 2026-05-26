"""Catalog album resource."""

from collections.abc import Callable
from dataclasses import dataclass

from musickit_api_mock.data.lookup import LookupContext, _lookup_source
from musickit_api_mock.data.primitives.artwork import Artwork
from musickit_api_mock.data.primitives.editorial_notes import EditorialNotes


@dataclass
class Album:
    """Apple Music catalog album.

    Attributes:
        name: Display title of the album.
        artist_name: Display name of the primary artist.
        artwork: Cover artwork.
        genre_names: Display names of the album's genres.
        track_count: Number of tracks on the album.
        is_compilation: Whether the album is a compilation.
        is_complete: Whether the album release is complete (vs. partial).
        is_mastered_for_itunes: Apple's "Mastered for iTunes" badge.
        is_single: Whether the release is a single.
        is_prerelease: Whether the release is a pre-release.
        audio_traits: Audio capability tags (lossless, dolby-atmos, etc.).
        url: Album landing-page URL on Apple Music.
        release_date: ISO-8601 release date.
        copyright: Copyright line.
        record_label: Display name of the record label.
        upc: Universal Product Code identifying the release.
        track_ids: Catalog song ids composing the album. The mock resolves
            these into full track resources at response time.
        artist_ids: Catalog artist ids credited on the album. Resolved into
            full artist resources at response time.
        content_rating: Apple content-rating tag (e.g. ``clean``, ``explicit``).
        editorial_notes: Editorial copy shown alongside the album.
        editorial_artwork: Treatment-keyed artworks emitted only when a
            request asks for them via ``?extend=editorialArtwork``.
        genre_ids: Catalog genre ids the album belongs to.
        record_label_ids: Catalog record-label ids associated with the album.
        library_album_id: Library album id when the album has a counterpart
            in the user's library, used to resolve ``?include=library``.
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
