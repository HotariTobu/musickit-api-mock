"""Library music-video resource."""

from collections.abc import Callable
from dataclasses import dataclass

from musickit_api_mock.data.lookup import LookupContext, _lookup_source
from musickit_api_mock.data.primitives.artwork import Artwork


@dataclass
class LibraryMusicVideo:
    """User-library music video.

    ``album_ids`` / ``artist_ids`` ref **library** albums/artists (not catalog)
    — Apple's /v1/me/library/music-videos/<id>?include=albums,artists returns
    library-albums and library-artists in relationships.
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
