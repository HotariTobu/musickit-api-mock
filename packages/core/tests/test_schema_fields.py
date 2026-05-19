"""Per-resource attribute emit verification.

Each resource (Song, Album, Artist, Playlist, MusicVideo, Station, plus
their library counterparts) carries a documented Apple Music API
attribute set. The tests below pin the fixture-value → JSON-attribute
mapping for every field the schema layer emits, so a regression in any
one builder surfaces as a single targeted failure rather than only being
caught by the few golden-path tests.

Brittleness: each assertion binds to (a) the Apple-documented attribute
name and (b) the conftest fixture value. Both are stable contract
points: the attribute names are the public API surface MusicKit JS and
user code observe; the fixture values are owned by ``conftest.py`` so
their reuse is intentional.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, cast

from musickit_api_mock import (
    Album,
    Artist,
    LibraryAlbum,
    LibraryArtist,
    LibraryMusicVideo,
    LibraryPlaylist,
    LibrarySong,
    MusicKitApiMock,
    MusicVideo,
    Playlist,
    Request,
    Song,
    Station,
)

if TYPE_CHECKING:
    from musickit_api_mock.json_value import _JSONValue

    from tests._apple_response import _AppleArtwork, _ApplePreview, _AppleResponse


def _get(mock: MusicKitApiMock, url: str) -> _AppleResponse:
    resp = mock.handle_request(Request(method="GET", url=url, headers={}, body=None))
    assert resp is not None
    assert resp.status == 200
    return json.loads(resp.body)


def _attrs(body: _AppleResponse) -> dict[str, _JSONValue]:
    attrs = body["data"][0].get("attributes")
    assert attrs is not None
    return attrs


def test_song_attributes_emit_configured_fields(
    mock: MusicKitApiMock, song: Song
) -> None:
    body = _get(mock, "https://api.music.apple.com/v1/catalog/us/songs?ids=1")
    attrs = _attrs(body)
    assert attrs["name"] == song.title
    assert attrs["artistName"] == song.artist
    assert attrs["albumName"] == song.album
    assert attrs["durationInMillis"] == song.duration_ms
    assert attrs["genreNames"] == song.genres
    assert attrs["releaseDate"] == song.release_date
    assert attrs["trackNumber"] == song.track_number
    assert attrs["discNumber"] == song.disc_number
    assert attrs["composerName"] == song.composer
    assert attrs["hasLyrics"] == song.has_lyrics
    assert attrs["audioLocale"] == song.audio_locale
    assert attrs["audioTraits"] == song.audio_traits
    assert attrs["hasTimeSyncedLyrics"] == song.has_time_synced_lyrics
    assert attrs["isAppleDigitalMaster"] == song.is_apple_digital_master
    assert attrs["isMasteredForItunes"] == song.is_mastered_for_itunes
    assert attrs["isVocalAttenuationAllowed"] == song.is_vocal_attenuation_allowed
    assert attrs["url"] == song.url
    artwork = cast("_AppleArtwork", attrs["artwork"])
    assert artwork["width"] == song.artwork.width
    assert artwork["height"] == song.artwork.height
    assert artwork["url"] == song.artwork.url


def test_album_attributes_emit_configured_fields(
    mock: MusicKitApiMock, album: Album
) -> None:
    body = _get(mock, "https://api.music.apple.com/v1/catalog/us/albums?ids=a1")
    attrs = _attrs(body)
    assert attrs["name"] == album.name
    assert attrs["artistName"] == album.artist_name
    assert attrs["genreNames"] == album.genre_names
    assert attrs["releaseDate"] == album.release_date
    assert attrs["trackCount"] == album.track_count
    assert attrs["copyright"] == album.copyright
    assert attrs["recordLabel"] == album.record_label
    assert attrs["upc"] == album.upc
    assert attrs["isCompilation"] == album.is_compilation
    assert attrs["isComplete"] == album.is_complete
    assert attrs["isMasteredForItunes"] == album.is_mastered_for_itunes
    assert attrs["isSingle"] == album.is_single
    assert attrs["isPrerelease"] == album.is_prerelease
    assert attrs["audioTraits"] == album.audio_traits
    assert attrs["url"] == album.url


def test_artist_attributes_emit_configured_fields(
    mock: MusicKitApiMock, artist: Artist
) -> None:
    body = _get(mock, "https://api.music.apple.com/v1/catalog/us/artists?ids=ar1")
    attrs = _attrs(body)
    assert attrs["name"] == artist.name
    assert attrs["genreNames"] == artist.genre_names
    assert attrs["url"] == artist.url
    assert artist.artwork is not None
    assert cast("_AppleArtwork", attrs["artwork"])["width"] == artist.artwork.width


def test_playlist_attributes_emit_configured_fields(
    mock: MusicKitApiMock, playlist: Playlist
) -> None:
    body = _get(mock, "https://api.music.apple.com/v1/catalog/us/playlists?ids=pl1")
    attrs = _attrs(body)
    assert attrs["name"] == playlist.name
    assert attrs["playlistType"] == playlist.playlist_type
    assert attrs["curatorName"] == playlist.curator_name
    assert attrs["hasCollaboration"] == playlist.has_collaboration
    assert attrs["isChart"] == playlist.is_chart
    assert attrs["supportsSing"] == playlist.supports_sing
    assert attrs["url"] == playlist.url
    assert attrs["lastModifiedDate"] == playlist.last_modified


def test_music_video_attributes_emit_configured_fields(
    mock: MusicKitApiMock, music_video: MusicVideo
) -> None:
    body = _get(mock, "https://api.music.apple.com/v1/catalog/us/music-videos?ids=mv1")
    attrs = _attrs(body)
    assert attrs["name"] == music_video.name
    assert attrs["artistName"] == music_video.artist_name
    assert attrs["durationInMillis"] == music_video.duration_ms
    assert attrs["genreNames"] == music_video.genre_names
    assert attrs["has4K"] == music_video.has_4k
    assert attrs["hasHDR"] == music_video.has_hdr
    assert attrs["isrc"] == music_video.isrc
    assert attrs["releaseDate"] == music_video.release_date
    assert attrs["url"] == music_video.url
    assert attrs["videoTraits"] == music_video.video_traits
    previews = cast("list[_ApplePreview]", attrs["previews"])
    assert previews[0]["url"] == music_video.previews[0].url


def test_station_attributes_emit_configured_fields(
    mock: MusicKitApiMock, station: Station
) -> None:
    body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/stations?ids=ra.978194965",
    )
    attrs = _attrs(body)
    assert attrs["name"] == station.name
    assert attrs["mediaKind"] == station.media_kind
    assert attrs["isLive"] == station.is_live
    assert attrs["kind"] == station.kind
    assert attrs["requiresSubscription"] == station.requires_subscription
    assert attrs["url"] == station.url
    # has_drm=True surfaces as the documented supportedDrms triple.
    supported_drms = cast("list[str]", attrs["supportedDrms"])
    assert "fairplay" in supported_drms
    assert "widevine" in supported_drms
    assert "playready" in supported_drms


def test_library_song_attributes_emit_configured_fields(
    mock: MusicKitApiMock, library_song: LibrarySong
) -> None:
    body = _get(mock, "https://api.music.apple.com/v1/me/library/songs/i.s1")
    attrs = _attrs(body)
    assert attrs["name"] == library_song.name
    assert attrs["artistName"] == library_song.artist_name
    assert attrs["albumName"] == library_song.album_name
    assert attrs["discNumber"] == library_song.disc_number
    assert attrs["durationInMillis"] == library_song.duration_ms
    assert attrs["genreNames"] == library_song.genre_names
    assert attrs["hasLyrics"] == library_song.has_lyrics
    assert attrs["trackNumber"] == library_song.track_number


def test_library_album_attributes_emit_configured_fields(
    mock: MusicKitApiMock, library_album: LibraryAlbum
) -> None:
    body = _get(mock, "https://api.music.apple.com/v1/me/library/albums/l.a1")
    attrs = _attrs(body)
    assert attrs["name"] == library_album.name
    assert attrs["artistName"] == library_album.artist_name
    assert attrs["dateAdded"] == library_album.date_added
    assert attrs["genreNames"] == library_album.genre_names
    assert attrs["trackCount"] == library_album.track_count


def test_library_artist_attributes_emit_only_name(
    mock: MusicKitApiMock, library_artist: LibraryArtist
) -> None:
    """LibraryArtist's API surface is just ``{name}`` per Apple."""
    body = _get(mock, "https://api.music.apple.com/v1/me/library/artists/r.ar1")
    attrs = _attrs(body)
    assert attrs == {"name": library_artist.name}


def test_library_playlist_attributes_emit_configured_fields(
    mock: MusicKitApiMock, library_playlist: LibraryPlaylist
) -> None:
    body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/playlists/p.pl1?include=tracks",
    )
    attrs = _attrs(body)
    assert attrs["name"] == library_playlist.name
    assert attrs["canDelete"] == library_playlist.can_delete
    assert attrs["canEdit"] == library_playlist.can_edit
    assert attrs["isPublic"] == library_playlist.is_public
    assert attrs["dateAdded"] == library_playlist.date_added
    assert attrs["lastModifiedDate"] == library_playlist.last_modified_date
    assert attrs["hasCatalog"] == library_playlist.has_catalog
    assert attrs["hasCollaboration"] == library_playlist.has_collaboration


def test_library_music_video_attributes_emit_configured_fields(
    mock: MusicKitApiMock, library_music_video: LibraryMusicVideo
) -> None:
    body = _get(mock, "https://api.music.apple.com/v1/me/library/music-videos/i.mv1")
    attrs = _attrs(body)
    assert attrs["name"] == library_music_video.name
    assert attrs["artistName"] == library_music_video.artist_name
    assert attrs["durationInMillis"] == library_music_video.duration_ms
    assert attrs["genreNames"] == library_music_video.genre_names
    assert attrs["releaseDate"] == library_music_video.release_date
    assert attrs["trackNumber"] == library_music_video.track_number
