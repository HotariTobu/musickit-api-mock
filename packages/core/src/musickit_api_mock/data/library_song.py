"""Library song resource."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from musickit_api_mock.data.lookup import LookupContext, _lookup_source
from musickit_api_mock.data.primitives.artwork import Artwork


@dataclass
class CatalogLibrarySong:
    """User-library song linked to an Apple Music catalog song.

    Playback streams the linked catalog song, so this variant carries no
    audio of its own.

    Attributes:
        name: Display title of the song.
        artist_name: Display name of the primary artist.
        artwork: Cover artwork.
        duration_ms: Duration in milliseconds.
        genre_names: Display names of the song's genres.
        has_lyrics: Whether lyrics are available.
        catalog_id: Catalog song id the library song is linked to. Emitted
            as ``playParams.catalogId`` / ``playParams.reportingId`` and
            resolved for ``?include=catalog``.
        album_name: Display name of the album the song belongs to.
        disc_number: Disc number when part of a multi-disc album.
        track_number: Track number within the album.
        release_date: ISO-8601 release date.
        album_ids: Library album ids the song belongs to.
        artist_ids: Library artist ids credited on the song.
    """

    name: str
    artist_name: str
    artwork: Artwork
    duration_ms: int
    genre_names: list[str]
    has_lyrics: bool
    catalog_id: str
    album_name: str | None = None
    disc_number: int | None = None
    track_number: int | None = None
    release_date: str | None = None
    album_ids: list[str] | None = None
    artist_ids: list[str] | None = None


@dataclass
class UploadedLibrarySong:
    """User-library song uploaded by the user, with no catalog counterpart.

    Playback serves the song's own audio bytes. The ``from_file`` constructor
    sources the audio and metadata from an audio file on disk.

    Attributes:
        name: Display title of the song.
        artist_name: Display name of the primary artist.
        artwork: Cover artwork.
        duration_ms: Duration in milliseconds.
        genre_names: Display names of the song's genres.
        has_lyrics: Whether lyrics are available.
        audio: Raw bytes of the audio file the mock serves for playback.
        album_name: Display name of the album the song belongs to.
        disc_number: Disc number when part of a multi-disc album.
        track_number: Track number within the album.
        album_ids: Library album ids the song belongs to.
        artist_ids: Library artist ids credited on the song.
    """

    name: str
    artist_name: str
    artwork: Artwork
    duration_ms: int
    genre_names: list[str]
    has_lyrics: bool
    audio: bytes
    album_name: str | None = None
    disc_number: int | None = None
    track_number: int | None = None
    album_ids: list[str] | None = None
    artist_ids: list[str] | None = None

    @classmethod
    def from_file(
        cls,
        audio_path: str,
        fallback: "UploadedLibrarySongMetadataFallback | None" = None,
    ) -> "UploadedLibrarySong":
        """Build an uploaded library song from an audio file.

        Reads tags, duration, and embedded artwork from the file and stores
        the file bytes as the served audio. Fields the file does not supply
        come from ``fallback``.

        Args:
            audio_path: Path to the audio file.
            fallback: Metadata defaults for fields the file's tags lack.

        Returns:
            The uploaded library song.

        Raises:
            ValueError: A required field is missing from both the file's
                tags and ``fallback``.
        """
        from musickit_api_mock.data.song_from_file import (
            _uploaded_library_song_from_file,
        )

        return _uploaded_library_song_from_file(cls, audio_path, fallback)


@dataclass
class UploadedLibrarySongMetadataFallback:
    """Metadata defaults applied when an uploaded file's tags are missing fields.

    Each field corresponds to the same-named attribute on the uploaded
    library song dataclass and is used only when the source file's tags do
    not supply the value. Fields left unset (``None``) provide no fallback
    and the loader raises if the tag is also missing.

    Attributes:
        name: Display-title fallback.
        artist_name: Primary-artist fallback.
        artwork: Cover-artwork fallback.
        genre_names: Genres fallback.
        has_lyrics: Lyrics-availability fallback.
        album_name: Album-name fallback.
        disc_number: Disc-number fallback.
        track_number: Track-number fallback.
    """

    name: str | None = None
    artist_name: str | None = None
    artwork: Artwork | None = None
    genre_names: list[str] | None = None
    has_lyrics: bool | None = None
    album_name: str | None = None
    disc_number: int | None = None
    track_number: int | None = None


LibrarySong = CatalogLibrarySong | UploadedLibrarySong

type LibrarySongsSource = (
    Mapping[str, LibrarySong] | Callable[[LookupContext], LibrarySong | None] | None
)


class _LibrarySongResolver:
    """Library-internal lookup over ``DataSources.library_songs``."""

    def __init__(self, get_source: Callable[[], LibrarySongsSource]) -> None:
        """Bind to the ``DataSources.library_songs`` source via a callback."""
        self._get_source = get_source

    def get(self, context: LookupContext) -> LibrarySong | None:
        """Return the library song for ``context.id`` or ``None`` if absent."""
        return _lookup_source(self._get_source(), "data.library_songs", context)
