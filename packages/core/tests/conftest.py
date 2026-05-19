from __future__ import annotations

import pytest
from musickit_api_mock import (
    Account,
    AccountResponseSuccess,
    Album,
    Artist,
    Artwork,
    Curator,
    Genre,
    Grouping,
    HlsChunk,
    HlsLayout,
    LibraryAlbum,
    LibraryArtist,
    LibraryMusicVideo,
    LibraryPlaylist,
    LibrarySong,
    MusicKitApiMock,
    MusicVideo,
    PersonalRecommendation,
    PersonalRecommendationContent,
    PersonalRecommendationDisplay,
    Playlist,
    Preview,
    RecordLabel,
    Song,
    Station,
    Storefront,
    StorefrontResponseSuccess,
)


def _artwork_catalog() -> Artwork:
    return Artwork(
        url="https://example.com/cover.jpg",
        width=640,
        height=640,
        bg_color="000000",
        text_color_1="ffffff",
        text_color_2="cccccc",
        text_color_3="999999",
        text_color_4="666666",
        has_p3=False,
    )


def _artwork_library() -> Artwork:
    return Artwork(url="https://example.com/lib.jpg", width=300, height=300)


@pytest.fixture
def artwork_catalog() -> Artwork:
    return _artwork_catalog()


@pytest.fixture
def artwork_library() -> Artwork:
    return _artwork_library()


@pytest.fixture
def song(artwork_catalog: Artwork) -> Song:
    return Song(
        title="Test Song",
        artist="Test Artist",
        album="Test Album",
        duration_ms=180_000,
        artwork=artwork_catalog,
        genres=["Pop"],
        release_date="2020-01-01",
        track_number=1,
        disc_number=1,
        composer="Test Composer",
        has_lyrics=False,
        audio_locale="en-US",
        audio_traits=["lossless"],
        has_time_synced_lyrics=False,
        is_apple_digital_master=True,
        is_mastered_for_itunes=True,
        is_vocal_attenuation_allowed=True,
        url="https://music.apple.com/us/song/1",
        hls_layout=HlsLayout(
            target_duration_sec=2,
            init_byte_offset=0,
            init_byte_length=4,
            chunks=(HlsChunk(duration_sec=2.0, byte_offset=4, byte_length=0),),
        ),
        hls_segment=b"\x00\x00\x00\x00",
        preview_audio=b"\x00\x00\x00\x00",
        bitrate=256,
        sample_rate=44100,
        file_size=1000,
        album_ids=["a1"],
        artist_ids=["ar1"],
        composer_ids=["ar1"],
        genre_ids=["20"],
        music_video_ids=["mv1"],
        station_id="ra.978194965",
        library_song_id="i.s1",
    )


@pytest.fixture
def album(artwork_catalog: Artwork) -> Album:
    return Album(
        name="Test Album",
        artist_name="Test Artist",
        artwork=artwork_catalog,
        genre_names=["Pop"],
        release_date="2020-01-01",
        track_count=1,
        copyright="(c) 2020",
        record_label="Indie",
        upc="000000000001",
        is_compilation=False,
        is_complete=True,
        is_mastered_for_itunes=True,
        is_single=False,
        is_prerelease=False,
        audio_traits=["lossless"],
        url="https://music.apple.com/us/album/a1",
        track_ids=["1"],
        artist_ids=["ar1"],
        genre_ids=["20"],
        record_label_ids=["rl1"],
        library_album_id="l.a1",
        editorial_artwork={
            "superHeroTall": Artwork(
                url="https://example.com/edit-tall.jpg",
                width=1680,
                height=2240,
                bg_color="111111",
            ),
        },
    )


@pytest.fixture
def artist(artwork_catalog: Artwork) -> Artist:
    return Artist(
        name="Test Artist",
        artwork=artwork_catalog,
        genre_names=["Pop"],
        url="https://music.apple.com/us/artist/ar1",
        album_ids=["a1"],
        genre_ids=["20"],
        music_video_ids=["mv1"],
        playlist_ids=["pl1"],
        station_id="ra.978194965",
    )


@pytest.fixture
def music_video(artwork_catalog: Artwork) -> MusicVideo:
    return MusicVideo(
        name="Test MV",
        artist_name="Test Artist",
        artwork=artwork_catalog,
        duration_ms=210_000,
        genre_names=["Pop"],
        has_4k=False,
        has_hdr=False,
        isrc="USABC0000001",
        release_date="2020-01-01",
        url="https://music.apple.com/us/music-video/mv1",
        previews=[Preview(url="https://example.com/preview.mp4")],
        video_traits=["hdr"],
        album_ids=["a1"],
        artist_ids=["ar1"],
        genre_ids=["20"],
        song_ids=["1"],
        library_music_video_id="i.mv1",
    )


@pytest.fixture
def playlist(artwork_catalog: Artwork) -> Playlist:
    return Playlist(
        name="Test Playlist",
        playlist_type="user-shared",
        curator_name="Test Curator",
        has_collaboration=False,
        is_chart=False,
        audio_traits=[],
        supports_sing=False,
        url="https://music.apple.com/us/playlist/pl1",
        artwork=artwork_catalog,
        last_modified="2024-01-01",
        track_ids=["1"],
        curator_id="cu1",
        library_playlist_id="p.pl1",
    )


@pytest.fixture
def curator(artwork_catalog: Artwork) -> Curator:
    return Curator(
        name="Apple Music Pop",
        type="apple-curators",
        short_name="Pop",
        kind="Genre",
        url="https://music.apple.com/us/curator/apple-music-pop/cu1",
        artwork=artwork_catalog,
        playlist_ids=["pl1"],
        grouping_id="gp1",
    )


@pytest.fixture
def non_apple_curator(artwork_catalog: Artwork) -> Curator:
    return Curator(
        name="Third Party Curator",
        type="curators",
        url="https://music.apple.com/us/curator/third-party/cu2",
        artwork=artwork_catalog,
        playlist_ids=["pl1"],
    )


@pytest.fixture
def station(artwork_catalog: Artwork) -> Station:
    return Station(
        name="Apple Music 1",
        artwork=artwork_catalog,
        is_live=True,
        media_kind="audio",
        url="https://music.apple.com/us/station/ra.978194965",
        is_tracks_station=False,
        has_drm=True,
        kind="radio",
        radio_url="https://itsliveradio.apple.com/gl/ra.978194965/index-cmaf.m3u8",
        requires_subscription=True,
        radio_show_id="cu1",
    )


@pytest.fixture
def library_song(artwork_library: Artwork) -> LibrarySong:
    return LibrarySong(
        name="Lib Song",
        artist_name="Lib Artist",
        album_name="Lib Album",
        artwork=artwork_library,
        disc_number=1,
        duration_ms=180_000,
        genre_names=["Pop"],
        has_lyrics=False,
        track_number=1,
        catalog_id="1",
        album_ids=["l.a1"],
        artist_ids=["r.ar1"],
    )


@pytest.fixture
def library_album(artwork_library: Artwork) -> LibraryAlbum:
    return LibraryAlbum(
        name="Lib Album",
        artist_name="Lib Artist",
        artwork=artwork_library,
        date_added="2024-01-01",
        genre_names=["Pop"],
        track_count=1,
        track_ids=["i.s1"],
        artist_ids=["r.ar1"],
        catalog_id="a1",
    )


@pytest.fixture
def library_playlist() -> LibraryPlaylist:
    return LibraryPlaylist(
        name="Lib Playlist",
        can_delete=True,
        can_edit=True,
        is_public=False,
        date_added="2024-01-01",
        last_modified_date="2024-01-02",
        has_catalog=False,
        has_collaboration=False,
        track_ids=["i.s1"],
        catalog_id="pl1",
    )


@pytest.fixture
def library_artist() -> LibraryArtist:
    return LibraryArtist(
        name="Lib Artist",
        album_ids=["l.a1"],
        catalog_id="ar1",
    )


@pytest.fixture
def library_music_video(artwork_library: Artwork) -> LibraryMusicVideo:
    return LibraryMusicVideo(
        name="Lib MV",
        artist_name="Lib Artist",
        artwork=artwork_library,
        duration_ms=200_000,
        genre_names=["Pop"],
        release_date="2020-01-01",
        track_number=1,
        album_ids=["l.a1"],
        artist_ids=["r.ar1"],
        catalog_id="mv1",
    )


@pytest.fixture
def genre() -> Genre:
    return Genre(
        name="Pop",
        url="https://music.apple.com/us/genre/20",
        parent_id="34",
        parent_name="Music",
    )


@pytest.fixture
def record_label() -> RecordLabel:
    return RecordLabel(
        name="Indie",
        url="https://music.apple.com/us/record-label/rl1",
    )


@pytest.fixture
def grouping() -> Grouping:
    return Grouping(
        name="Curators",
        url="https://music.apple.com/us/grouping/gp1",
    )


@pytest.fixture
def personal_recommendation() -> PersonalRecommendation:
    return PersonalRecommendation(
        title="Recommended Playlists",
        is_group_recommendation=False,
        kind="music-recommendations",
        next_update_date="2026-05-25T00:00:00Z",
        resource_types=["playlists"],
        contents=[PersonalRecommendationContent(type="playlists", id="pl1")],
        display=PersonalRecommendationDisplay(kind="MusicCoverShelf"),
        has_see_all=False,
        version=2,
    )


@pytest.fixture
def storefront() -> Storefront:
    return Storefront(
        id="us",
        name="United States",
        default_language_tag="en-US",
        supported_language_tags=["en-US"],
        explicit_content_policy="allowed",
    )


@pytest.fixture
def account() -> Account:
    return Account(subscription_active=True, subscription_storefront="us")


@pytest.fixture
def mock(
    song: Song,
    album: Album,
    artist: Artist,
    music_video: MusicVideo,
    playlist: Playlist,
    station: Station,
    curator: Curator,
    library_song: LibrarySong,
    library_album: LibraryAlbum,
    library_playlist: LibraryPlaylist,
    library_artist: LibraryArtist,
    library_music_video: LibraryMusicVideo,
    genre: Genre,
    record_label: RecordLabel,
    grouping: Grouping,
    personal_recommendation: PersonalRecommendation,
    non_apple_curator: Curator,
    storefront: Storefront,
    account: Account,
) -> MusicKitApiMock:
    m = MusicKitApiMock()
    m.data.songs = {"1": song}
    m.data.albums = {"a1": album}
    m.data.artists = {"ar1": artist}
    m.data.music_videos = {"mv1": music_video}
    m.data.playlists = {"pl1": playlist}
    m.data.stations = {"ra.978194965": station}
    m.data.curators = {"cu1": curator, "cu2": non_apple_curator}
    m.data.genres = {"20": genre}
    m.data.record_labels = {"rl1": record_label}
    m.data.groupings = {"gp1": grouping}
    m.data.personal_recommendations = {"rec1": personal_recommendation}
    m.data.library_songs = {"i.s1": library_song}
    m.data.library_albums = {"l.a1": library_album}
    m.data.library_playlists = {"p.pl1": library_playlist}
    m.data.library_artists = {"r.ar1": library_artist}
    m.data.library_music_videos = {"i.mv1": library_music_video}
    m.endpoints.storefront = StorefrontResponseSuccess(storefront=storefront)
    m.endpoints.account = AccountResponseSuccess(account=account)
    return m
