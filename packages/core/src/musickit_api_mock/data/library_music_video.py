"""Library music-video resource."""

from collections.abc import Callable
from dataclasses import dataclass

from musickit_api_mock.data.lookup import LookupContext, _lookup_source
from musickit_api_mock.data.primitives.artwork import Artwork


@dataclass
class LibraryMusicVideo:
    """User-library music video.

    Attributes:
        name: Display title of the music video.
        artist_name: Display name of the primary artist.
        artwork: Cover artwork.
        duration_ms: Duration in milliseconds.
        genre_names: Display names of the genres.
        release_date: ISO-8601 release date.
        track_number: Track number when part of an album.
        album_ids: Library album ids the video belongs to. These reference
            library albums (not catalog albums) — the same endpoint
            ``?include=albums`` returns library-albums in relationships.
        artist_ids: Library artist ids credited on the video. References
            library artists for the same reason as the album ids.
        content_rating: Apple content-rating tag.
        album_name: Display name of the album the video belongs to.
        catalog_id: Catalog music-video id linking back to the catalog
            counterpart, used to resolve ``?include=catalog``.
    """

    name: str
    artist_name: str
    artwork: Artwork
    duration_ms: int
    genre_names: list[str]
    release_date: str | None = None
    track_number: int | None = None
    album_ids: list[str] | None = None
    artist_ids: list[str] | None = None
    content_rating: str | None = None
    album_name: str | None = None
    catalog_id: str | None = None


type LibraryMusicVideosSource = (
    dict[str, LibraryMusicVideo]
    | Callable[[LookupContext], LibraryMusicVideo | None]
    | None
)


class _LibraryMusicVideoResolver:
    """Library-internal lookup over ``DataSources.library_music_videos``."""

    def __init__(self, get_source: Callable[[], LibraryMusicVideosSource]) -> None:
        """Bind to the ``DataSources.library_music_videos`` source via a callback."""
        self._get_source = get_source

    def get(self, context: LookupContext) -> LibraryMusicVideo | None:
        """Return the library music video for ``context.id`` or ``None`` if absent."""
        return _lookup_source(self._get_source(), "data.library_music_videos", context)
