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
    """Byte range of one media chunk inside an HLS fMP4 segment file.

    Attributes:
        duration_sec: Duration of this chunk in seconds.
        byte_offset: Offset of the chunk within the segment file.
        byte_length: Length of the chunk in bytes.
    """

    duration_sec: float
    byte_offset: int
    byte_length: int


@dataclass(frozen=True)
class HlsLayout:
    """fMP4 segment layout describing what the HLS manifest must declare.

    The mock composes the wire-format manifest at serve time so the
    EXT-X-KEY directive can be selected from the active key system.

    Attributes:
        target_duration_sec: Target chunk duration declared in the manifest.
        init_byte_offset: Offset of the initialization fragment within the
            segment file.
        init_byte_length: Length of the initialization fragment in bytes.
        chunks: Per-chunk byte-range descriptors in playback order.
    """

    target_duration_sec: int
    init_byte_offset: int
    init_byte_length: int
    chunks: tuple[HlsChunk, ...]


@dataclass
class Song:
    """Apple Music catalog song.

    Holds the audio bytes the mock returns for HLS playback and preview,
    plus the layout the mock needs to compose the HLS manifest at serve
    time. The ``from_file`` constructor sources these from an audio file on
    disk.

    Attributes:
        title: Display title of the song.
        artist: Display name of the primary artist.
        album: Display name of the album the song belongs to.
        duration_ms: Duration in milliseconds.
        artwork: Cover artwork.
        genres: Display names of the song's genres.
        has_lyrics: Whether lyrics are available.
        audio_locale: BCP-47 locale tag of the recorded audio.
        audio_traits: Audio capability tags (lossless, dolby-atmos, etc.).
        has_time_synced_lyrics: Whether time-synced lyrics are available.
        is_apple_digital_master: Apple's "Apple Digital Master" badge.
        is_mastered_for_itunes: Apple's "Mastered for iTunes" badge.
        is_vocal_attenuation_allowed: Whether vocal attenuation (Sing) is
            allowed.
        url: Song landing-page URL on Apple Music.
        hls_layout: fMP4 segment layout for the HLS manifest.
        hls_segment: Raw bytes of the fMP4 segment served for HLS playback.
        preview_audio: Raw bytes the mock serves as the preview asset.
        bitrate: Bitrate in kilobits per second.
        sample_rate: Sample rate in hertz.
        file_size: Source file size in bytes.
        release_date: ISO-8601 release date.
        track_number: Track number within the album.
        disc_number: Disc number when part of a multi-disc album.
        composer: Display name of the primary composer.
        isrc: International Standard Recording Code.
        content_rating: Apple content-rating tag.
        play_assets: Per-bit-rate play-asset variants surfaced in station
            track-info responses.
        album_ids: Catalog album ids the song belongs to. Emitted as
            shallow refs in ``relationships.albums``, or as deep inline
            resources when ``?include=albums`` is requested.
        artist_ids: Catalog artist ids credited on the song. Emitted in
            ``relationships.artists`` with the same shallow/deep rule.
        composer_ids: Catalog artist ids credited as composers. Emitted in
            ``relationships.composers`` with the same shallow/deep rule.
        genre_ids: Catalog genre ids the song belongs to.
        music_video_ids: Catalog music-video ids associated with the song.
        station_id: Catalog station id of the song's radio station.
        library_song_id: Library song id when the song has a counterpart in
            the user's library.
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
        """Build a song by reading metadata and audio bytes from a file on disk.

        Reads tags and audio data from the file at ``audio_path`` and
        populates every field of the result, including HLS segment bytes
        and layout. Missing tag fields are filled from ``fallback`` when
        supplied; fields with neither a tag nor a fallback raise.

        Args:
            audio_path: Filesystem path to the source audio file.
            fallback: Metadata defaults applied when tags are missing the
                corresponding field. Leave unset to require every field to
                be present in the file's tags.
            preview: Either an explicit byte payload to serve as the preview,
                or a time window to extract from the source audio. Leave
                unset to use the full source audio as the preview.

        Returns:
            A fully-populated song built from the file.
        """
        from musickit_api_mock.data.song_from_file import _song_from_file

        return _song_from_file(cls, audio_path, fallback, preview=preview)


@dataclass
class SongMetadataFallback:
    """Metadata defaults applied when an audio file's tags are missing fields.

    Each field corresponds to the same-named attribute on the song
    dataclass and is used only when the source file's tags do not supply
    the value. Fields left unset (``None``) provide no fallback and the
    loader raises if the tag is also missing.

    Attributes:
        title: Display title fallback.
        artist: Primary artist fallback.
        album: Album-name fallback.
        artwork: Cover-artwork fallback.
        genres: Genres fallback.
        release_date: ISO-8601 release-date fallback.
        track_number: Track-number fallback.
        disc_number: Disc-number fallback.
        composer: Composer fallback.
        has_lyrics: Lyrics-availability fallback.
        isrc: ISRC fallback.
        content_rating: Content-rating fallback.
        audio_locale: BCP-47 audio-locale fallback.
        audio_traits: Audio-traits fallback.
        has_time_synced_lyrics: Time-synced lyrics-availability fallback.
        is_apple_digital_master: Apple Digital Master fallback.
        is_mastered_for_itunes: Mastered for iTunes fallback.
        is_vocal_attenuation_allowed: Vocal-attenuation-allowed fallback.
        url: Landing-page URL fallback.
    """

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
    """Time window (in seconds) to extract from the source audio as the preview.

    Attributes:
        start_sec: Start offset in seconds from the beginning of the source.
        duration_sec: Preview duration in seconds.
    """

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
