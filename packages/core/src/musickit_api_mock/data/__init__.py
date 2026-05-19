"""Resource dataclasses (catalog and library) and shared building blocks."""

from musickit_api_mock.data.album import Album
from musickit_api_mock.data.artist import Artist
from musickit_api_mock.data.curator import Curator
from musickit_api_mock.data.genre import Genre
from musickit_api_mock.data.grouping import Grouping
from musickit_api_mock.data.library_album import LibraryAlbum
from musickit_api_mock.data.library_artist import LibraryArtist
from musickit_api_mock.data.library_music_video import LibraryMusicVideo
from musickit_api_mock.data.library_playlist import LibraryPlaylist
from musickit_api_mock.data.library_song import LibrarySong
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
    HlsChunk,
    HlsLayout,
    PreviewRange,
    Song,
    SongMetadataFallback,
)
from musickit_api_mock.data.station import Station

__all__ = [
    "Album",
    "Artist",
    "Artwork",
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
    "Song",
    "SongMetadataFallback",
    "Station",
    "StationContextPlayAsset",
]
