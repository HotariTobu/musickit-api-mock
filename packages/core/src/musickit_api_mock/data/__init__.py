"""Resource dataclasses (catalog and library) and shared building blocks."""

from musickit_api_mock.data.album import CatalogAlbum
from musickit_api_mock.data.artist import CatalogArtist
from musickit_api_mock.data.curator import Curator
from musickit_api_mock.data.genre import Genre
from musickit_api_mock.data.grouping import Grouping
from musickit_api_mock.data.library_album import (
    CatalogLibraryAlbum,
    LibraryAlbum,
    UploadedLibraryAlbum,
)
from musickit_api_mock.data.library_artist import (
    CatalogLibraryArtist,
    LibraryArtist,
    UploadedLibraryArtist,
)
from musickit_api_mock.data.library_music_video import LibraryMusicVideo
from musickit_api_mock.data.library_playlist import LibraryPlaylist
from musickit_api_mock.data.library_song import (
    CatalogLibrarySong,
    LibrarySong,
    UploadedLibrarySong,
    UploadedLibrarySongMetadataFallback,
)
from musickit_api_mock.data.lookup import LookupContext
from musickit_api_mock.data.music_video import MusicVideo
from musickit_api_mock.data.personal_recommendation import (
    PersonalRecommendation,
    PersonalRecommendationContent,
    PersonalRecommendationDisplay,
)
from musickit_api_mock.data.playlist import Playlist
from musickit_api_mock.data.primitives import (
    Artwork,
    Description,
    EditorialNotes,
    Preview,
    StationContextPlayAsset,
)
from musickit_api_mock.data.record_label import RecordLabel
from musickit_api_mock.data.song import (
    CatalogSong,
    HlsChunk,
    HlsLayout,
    PreviewRange,
    SongMetadataFallback,
)
from musickit_api_mock.data.station import Station

__all__ = [
    "Artwork",
    "CatalogAlbum",
    "CatalogArtist",
    "CatalogLibraryAlbum",
    "CatalogLibraryArtist",
    "CatalogLibrarySong",
    "CatalogSong",
    "Curator",
    "Description",
    "EditorialNotes",
    "Genre",
    "Grouping",
    "HlsChunk",
    "HlsLayout",
    "LibraryAlbum",
    "LibraryArtist",
    "LibraryMusicVideo",
    "LibraryPlaylist",
    "LibrarySong",
    "LookupContext",
    "MusicVideo",
    "PersonalRecommendation",
    "PersonalRecommendationContent",
    "PersonalRecommendationDisplay",
    "Playlist",
    "Preview",
    "PreviewRange",
    "RecordLabel",
    "SongMetadataFallback",
    "Station",
    "StationContextPlayAsset",
    "UploadedLibraryAlbum",
    "UploadedLibraryArtist",
    "UploadedLibrarySong",
    "UploadedLibrarySongMetadataFallback",
]
