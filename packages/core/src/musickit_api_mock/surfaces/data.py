"""Shared resource sources DTO + library-internal lookup composer.

The DTO carries user-assigned resource sources (catalog and library, as
``dict`` or ``Callable``). The composer wires the per-resource sub-resolvers
(each defined alongside its dataclass under ``data/``) into one access
point; reading an unset (default ``None``) source through any sub-resolver
raises ``ValueError``.

Each sub-resolver receives its source via a callback so user re-assignment
of ``mock.data.<field>`` after construction is reflected on the next lookup.
"""

from collections.abc import Callable
from dataclasses import dataclass

from musickit_api_mock.data.album import AlbumsSource, _AlbumResolver
from musickit_api_mock.data.artist import ArtistsSource, _ArtistResolver
from musickit_api_mock.data.curator import CuratorsSource, _CuratorResolver
from musickit_api_mock.data.genre import GenresSource, _GenreResolver
from musickit_api_mock.data.grouping import GroupingsSource, _GroupingResolver
from musickit_api_mock.data.library_album import (
    LibraryAlbumsSource,
    _LibraryAlbumResolver,
)
from musickit_api_mock.data.library_artist import (
    LibraryArtistsSource,
    _LibraryArtistResolver,
)
from musickit_api_mock.data.library_music_video import (
    LibraryMusicVideosSource,
    _LibraryMusicVideoResolver,
)
from musickit_api_mock.data.library_playlist import (
    LibraryPlaylistsSource,
    _LibraryPlaylistResolver,
)
from musickit_api_mock.data.library_song import (
    LibrarySongsSource,
    _LibrarySongResolver,
)
from musickit_api_mock.data.music_video import MusicVideosSource, _MusicVideoResolver
from musickit_api_mock.data.personal_recommendation import (
    PersonalRecommendationsSource,
    _PersonalRecommendationResolver,
)
from musickit_api_mock.data.playlist import PlaylistsSource, _PlaylistResolver
from musickit_api_mock.data.record_label import (
    RecordLabelsSource,
    _RecordLabelResolver,
)
from musickit_api_mock.data.song import SongsSource, _SongResolver
from musickit_api_mock.data.station import StationsSource, _StationResolver


@dataclass
class DataSources:
    """Shared resource sources read by multiple endpoints.

    Pure data holder. Each field accepts either an id-keyed mapping or a
    lookup callable returning the resource (or ``None`` when not found).
    Fields default to ``None``; reading an unset source via the mock raises
    ``ValueError`` rather than synthesizing a fallback.

    Attributes:
        songs: Catalog song source.
        albums: Catalog album source.
        playlists: Catalog playlist source.
        artists: Catalog artist source.
        music_videos: Catalog music-video source.
        stations: Catalog radio-station source.
        curators: Catalog curator source (apple-curators and curators).
        genres: Catalog genre source.
        record_labels: Catalog record-label source.
        groupings: Catalog grouping source (editorial categories).
        personal_recommendations: User recommendation row source.
        library_songs: User-library song source.
        library_albums: User-library album source.
        library_playlists: User-library playlist source.
        library_artists: User-library artist source.
        library_music_videos: User-library music-video source.
    """

    songs: SongsSource = None
    albums: AlbumsSource = None
    playlists: PlaylistsSource = None
    artists: ArtistsSource = None
    music_videos: MusicVideosSource = None
    stations: StationsSource = None
    curators: CuratorsSource = None
    genres: GenresSource = None
    record_labels: RecordLabelsSource = None
    groupings: GroupingsSource = None
    personal_recommendations: PersonalRecommendationsSource = None
    library_songs: LibrarySongsSource = None
    library_albums: LibraryAlbumsSource = None
    library_playlists: LibraryPlaylistsSource = None
    library_artists: LibraryArtistsSource = None
    library_music_videos: LibraryMusicVideosSource = None


class _DataResolver:
    """Library-internal lookup composer over the shared-data DTO.

    Each per-resource module owns its own sub-resolver; this class composes
    them into one access point keyed by resource. Each sub-resolver re-reads
    its source via the callback on every ``.get(...)`` call, so user
    re-assignment of ``mock.data.<field>`` after construction is reflected
    on the next lookup.
    """

    song: _SongResolver
    album: _AlbumResolver
    playlist: _PlaylistResolver
    artist: _ArtistResolver
    music_video: _MusicVideoResolver
    station: _StationResolver
    curator: _CuratorResolver
    genre: _GenreResolver
    record_label: _RecordLabelResolver
    grouping: _GroupingResolver
    personal_recommendation: _PersonalRecommendationResolver
    library_song: _LibrarySongResolver
    library_album: _LibraryAlbumResolver
    library_playlist: _LibraryPlaylistResolver
    library_artist: _LibraryArtistResolver
    library_music_video: _LibraryMusicVideoResolver

    def __init__(self, get_data: Callable[[], DataSources]) -> None:
        """Compose per-resource sub-resolvers, each bound to its source via the callback."""
        self.song = _SongResolver(lambda: get_data().songs)
        self.album = _AlbumResolver(lambda: get_data().albums)
        self.playlist = _PlaylistResolver(lambda: get_data().playlists)
        self.artist = _ArtistResolver(lambda: get_data().artists)
        self.music_video = _MusicVideoResolver(lambda: get_data().music_videos)
        self.station = _StationResolver(lambda: get_data().stations)
        self.curator = _CuratorResolver(lambda: get_data().curators)
        self.genre = _GenreResolver(lambda: get_data().genres)
        self.record_label = _RecordLabelResolver(lambda: get_data().record_labels)
        self.grouping = _GroupingResolver(lambda: get_data().groupings)
        self.personal_recommendation = _PersonalRecommendationResolver(
            lambda: get_data().personal_recommendations
        )
        self.library_song = _LibrarySongResolver(lambda: get_data().library_songs)
        self.library_album = _LibraryAlbumResolver(lambda: get_data().library_albums)
        self.library_playlist = _LibraryPlaylistResolver(
            lambda: get_data().library_playlists
        )
        self.library_artist = _LibraryArtistResolver(lambda: get_data().library_artists)
        self.library_music_video = _LibraryMusicVideoResolver(
            lambda: get_data().library_music_videos
        )
