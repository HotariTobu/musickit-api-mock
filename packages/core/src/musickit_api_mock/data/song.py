"""Catalog song resource and helpers for sourcing songs from audio files."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from musickit_api_mock.data.lookup import LookupContext, _lookup_source

if TYPE_CHECKING:
    from musickit_api_mock.data.primitives.artwork import Artwork
    from musickit_api_mock.data.primitives.station_context_play_asset import (
        StationContextPlayAsset,
    )


@dataclass(frozen=True)
class HlsChunk:
    """Byte range of one media chunk inside an HLS fMP4 segment file."""

    duration_sec: float
    byte_offset: int
    byte_length: int


@dataclass(frozen=True)
class HlsLayout:
    """fMP4 segment layout describing what the HLS manifest must declare.

    The mock composes the wire-format manifest at serve time so the
    EXT-X-KEY directive can be selected from the active key system.
    """

    target_duration_sec: int
    init_byte_offset: int
    init_byte_length: int
    chunks: tuple[HlsChunk, ...]


@dataclass
class Song:
    """Apple Music catalog song.

    Holds the audio bytes the mock returns for HLS playback and preview, plus
    the layout the mock needs to compose the HLS manifest at serve time.
    Use ``Song.from_file`` to source these from an audio file on disk.
    ``album_ids`` / ``artist_ids`` / ``composer_ids`` carry the song's
    relationship composition by id; they're emitted as shallow refs in the
    song's ``relationships.{albums,artists,composers}`` block, or as deep
    inline resources when ``?include=...`` is requested.
    """

    title: str
    artist: str
    album: str
    duration_ms: int
    artwork: Artwork
    genres: list[str]
    has_lyrics: bool
    audio_locale: str
    audio_traits: list[str]
    has_time_synced_lyrics: bool
    is_apple_digital_master: bool
    is_mastered_for_itunes: bool
    is_vocal_attenuation_allowed: bool
    url: str
    hls_layout: HlsLayout
    hls_segment: bytes
    preview_audio: bytes
    bitrate: int
    sample_rate: int
    file_size: int
    release_date: str | None = None
    track_number: int | None = None
    disc_number: int | None = None
    composer: str | None = None
    isrc: str | None = None
    content_rating: str | None = None
    play_assets: list[StationContextPlayAsset] | None = None
    album_ids: list[str] | None = None
    artist_ids: list[str] | None = None
    composer_ids: list[str] | None = None
    genre_ids: list[str] | None = None
    music_video_ids: list[str] | None = None
    station_id: str | None = None
    library_song_id: str | None = None

    @classmethod
    def from_file(
        cls,
        audio_path: str,
        fallback: SongMetadataFallback | None = None,
        *,
        preview: PreviewRange | bytes | None = None,
    ) -> Song:
        """Build a Song by reading metadata and bytes from an audio file."""
        from musickit_api_mock.data.song_from_file import _song_from_file

        return _song_from_file(cls, audio_path, fallback, preview=preview)


@dataclass
class SongMetadataFallback:
    """Metadata defaults applied when an audio file's tags are missing fields."""

    title: str | None = None
    artist: str | None = None
    album: str | None = None
    artwork: Artwork | None = None
    genres: list[str] | None = None
    release_date: str | None = None
    track_number: int | None = None
    disc_number: int | None = None
    composer: str | None = None
    has_lyrics: bool | None = None
    isrc: str | None = None
    content_rating: str | None = None
    audio_locale: str | None = None
    audio_traits: list[str] | None = None
    has_time_synced_lyrics: bool | None = None
    is_apple_digital_master: bool | None = None
    is_mastered_for_itunes: bool | None = None
    is_vocal_attenuation_allowed: bool | None = None
    url: str | None = None


@dataclass
class PreviewRange:
    """Time window (in seconds) to extract from the source audio as the preview."""

    start_sec: float
    duration_sec: float


type SongsSource = dict[str, Song] | Callable[[LookupContext], Song | None] | None


class _SongResolver:
    """Library-internal lookup over ``DataSources.songs``."""

    def __init__(self, get_source: Callable[[], SongsSource]) -> None:
        """Bind to the ``DataSources.songs`` source via a callback."""
        self._get_source = get_source

    def get(self, context: LookupContext) -> Song | None:
        """Return the song for ``context.id`` or ``None`` if absent."""
        return _lookup_source(self._get_source(), "data.songs", context)
