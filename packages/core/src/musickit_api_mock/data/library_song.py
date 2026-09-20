"""Library song resource."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass

from musickit_api_mock.data.lookup import (
    LookupContext,
    _dangling_catalog_id,
    _lookup_source,
)
from musickit_api_mock.data.primitives.artwork import Artwork
from musickit_api_mock.data.song import CatalogSong


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

    Playback serves the song's own audio. The ``from_file`` constructor
    sources the audio and metadata from an audio file on disk the way a
    Music.app import does; assign to the fields afterwards to model edits
    made in Music.app.

    Attributes:
        name: Display title of the song.
        artist_name: Display name of the primary artist. ``None`` when the
            song has no artist; Apple then omits the attribute.
        artwork: Cover artwork. ``None`` when the song has no artwork;
            Apple then omits the attribute.
        duration_ms: Duration in milliseconds.
        genre_names: Display names of the song's genres.
        has_lyrics: Whether lyrics are available.
        audio: AAC audio in an M4A container the mock serves for playback.
        disc_number: Disc number, ``0`` when unset.
        track_number: Track number, ``0`` when unset.
        album_name: Display name of the album the song belongs to. ``None``
            when the song has no album; Apple then omits the attribute.
        album_ids: Library album ids the song belongs to.
        artist_ids: Library artist ids credited on the song.
    """

    name: str
    artist_name: str | None
    artwork: Artwork | None
    duration_ms: int
    genre_names: list[str]
    has_lyrics: bool
    audio: bytes
    disc_number: int
    track_number: int
    album_name: str | None = None
    album_ids: list[str] | None = None
    artist_ids: list[str] | None = None

    @classmethod
    def from_file(cls, audio_path: str) -> "UploadedLibrarySong":
        """Build an uploaded library song from an audio file.

        Reads the file the way a Music.app import does and transcodes the
        audio to AAC in an M4A container, as Apple does for uploads. No tag
        is required; an empty tag counts as absent.

        - ``name``: the title tag, or the file name without its last
          extension when the tag is absent.
        - ``artist_name`` / ``album_name``: the artist / album tag, or
          ``None`` when absent.
        - ``genre_names``: the genre tag as a single element, verbatim, or
          ``[""]`` when absent.
        - ``track_number`` / ``disc_number``: the tag parsed like C's
          ``strtol`` (leading whitespace, an optional sign, then ASCII
          digits up to the first other character, so ``"3/12"`` gives
          ``3``), reduced modulo 65536; ``0`` when the tag is absent, has
          no leading integer, or exceeds 32767 after reduction.
        - ``artwork``: the first embedded picture as a data URL, reported
          as 1200 by 1200 regardless of the picture's size, or ``None`` when
          the file has none.
        - ``has_lyrics``: always ``False``.

        Args:
            audio_path: Path to the audio file.

        Returns:
            The uploaded library song.
        """
        from musickit_api_mock.data.song_from_file import (
            _uploaded_library_song_from_file,
        )

        return _uploaded_library_song_from_file(cls, audio_path)


LibrarySong = CatalogLibrarySong | UploadedLibrarySong

type LibrarySongsSource = (
    Mapping[str, LibrarySong] | Callable[[LookupContext], LibrarySong | None] | None
)


class _LibrarySongResolver:
    """Library-internal lookup over ``DataSources.library_songs``.

    A catalog-linked song resolves only when its catalog counterpart
    exists; a dangling ``catalog_id`` raises on every lookup.
    """

    def __init__(
        self,
        get_source: Callable[[], LibrarySongsSource],
        get_catalog: Callable[[LookupContext], CatalogSong | None],
    ) -> None:
        """Bind to the ``DataSources.library_songs`` source and the catalog song lookup."""
        self._get_source = get_source
        self._get_catalog = get_catalog

    def get(self, context: LookupContext) -> LibrarySong | None:
        """Return the library song for ``context.id`` or ``None`` if absent."""
        song = _lookup_source(self._get_source(), "data.library_songs", context)
        if isinstance(song, CatalogLibrarySong):
            self.catalog_for(context, song)
        return song

    def catalog_for(
        self, context: LookupContext, song: CatalogLibrarySong
    ) -> CatalogSong:
        """Return the catalog song ``song`` is linked to, raising if it has no entry."""
        catalog = self._get_catalog(LookupContext(song.catalog_id, context.locale))
        if catalog is None:
            raise _dangling_catalog_id(
                "data.library_songs", context.id, "data.songs", song.catalog_id
            )
        return catalog
