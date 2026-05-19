"""Catalog music-video resource."""

from collections.abc import Callable
from dataclasses import dataclass

from musickit_api_mock.data.lookup import LookupContext, _lookup_source
from musickit_api_mock.data.primitives.artwork import Artwork
from musickit_api_mock.data.primitives.preview import Preview


@dataclass
class MusicVideo:
    """Apple Music catalog music video."""

    name: str
    artist_name: str
    artwork: Artwork
    duration_ms: int
    genre_names: list[str]
    has_4k: bool
    has_hdr: bool
    url: str
    previews: list[Preview]
    video_traits: list[str]
    isrc: str | None = None
    release_date: str | None = None
    album_name: str | None = None
    content_rating: str | None = None
    disc_number: int | None = None
    track_number: int | None = None
    album_ids: list[str] | None = None
    artist_ids: list[str] | None = None
    genre_ids: list[str] | None = None
    song_ids: list[str] | None = None
    library_music_video_id: str | None = None


type MusicVideosSource = (
    dict[str, MusicVideo] | Callable[[LookupContext], MusicVideo | None] | None
)


class _MusicVideoResolver:
    """Library-internal lookup over ``DataSources.music_videos``."""

    def __init__(self, get_source: Callable[[], MusicVideosSource]) -> None:
        """Bind to the ``DataSources.music_videos`` source via a callback."""
        self._get_source = get_source

    def get(self, context: LookupContext) -> MusicVideo | None:
        """Return the music video for ``context.id`` or ``None`` if absent."""
        return _lookup_source(self._get_source(), "data.music_videos", context)
