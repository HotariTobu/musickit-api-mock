"""Async parity for ``test_intercept_sync.py``: raw ``fetch`` / EME boundary."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from musickit_api_mock import (
    Account,
    AccountResponseSuccess,
    Album,
    Artist,
    Artwork,
    AuthorizeSuccess,
    Curator,
    Genre,
    HlsChunk,
    HlsLayout,
    LibraryAlbum,
    LibraryArtist,
    LibrarySong,
    LicenseResponseGeoBlock,
    LicenseResponseSuccess,
    MusicKitApiMock,
    MusicVideo,
    PersonalRecommendation,
    PersonalRecommendationContent,
    Playlist,
    Preview,
    RecordLabel,
    Song,
    Station,
    Storefront,
    StorefrontResponseSuccess,
)

from tests.scenarios_intercept import (
    EVAL_EME_FLAVOR,
    FETCH_ALBUM_RECORD_LABELS,
    FETCH_APPLE_CURATOR_PLAYLISTS,
    FETCH_ARTIST_STATION,
    FETCH_AUTHORIZE_RESPONSE,
    FETCH_GENRE_SINGULAR,
    FETCH_LIBRARY_ARTIST_ALBUMS,
    FETCH_LICENSE,
    FETCH_MUSIC_VIDEO_SONGS,
    FETCH_RECOMMENDATION_SINGULAR,
    FETCH_SONG_LIBRARY,
    FETCH_STATION_RADIO_SHOW,
    FETCH_STOREFRONT,
    FETCH_STOREFRONT_AND_REPORT_OUTCOME,
    FETCH_UNRELATED_APPLE_URL,
    OPEN_OAUTH_POPUP_AND_RECEIVE,
    REQUEST_PLAYREADY_ACCESS,
    REQUEST_WIDEVINE_ACCESS,
    UNRELATED_APPLE_URL,
    assert_album_record_labels_response,
    assert_apple_curator_playlists_response,
    assert_artist_station_response,
    assert_authorize_message,
    assert_authorize_response_success,
    assert_eme_flavor,
    assert_fetch_aborted,
    assert_genre_singular_response,
    assert_library_artist_albums_response,
    assert_license_failure,
    assert_license_success_b64,
    assert_music_video_songs_response,
    assert_not_supported_error,
    assert_recommendation_singular_response,
    assert_song_library_response,
    assert_station_radio_show_response,
    assert_storefront_response,
    assert_widevine_granted,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from playwright.async_api import Page as AsyncPage
    from playwright.async_api import Route as AsyncRoute


pytestmark = pytest.mark.async_test


async def test_storefront_request_intercepted(
    mount_async_page: Callable[..., Awaitable[AsyncPage]], page_url: str
) -> None:
    mock = MusicKitApiMock()
    mock.endpoints.storefront = StorefrontResponseSuccess(
        storefront=Storefront(
            id="us",
            name="United States",
            default_language_tag="en-US",
            supported_language_tags=["en-US"],
            explicit_content_policy="allowed",
        )
    )
    mock.endpoints.account = AccountResponseSuccess(
        account=Account(subscription_active=True, subscription_storefront="us")
    )
    page = await mount_async_page(mock)
    await page.goto(page_url)
    assert_storefront_response(await page.evaluate(FETCH_STOREFRONT))


async def test_unintercepted_apple_unrelated_url_falls_through(
    mount_async_page: Callable[..., Awaitable[AsyncPage]], page_url: str
) -> None:
    mock = MusicKitApiMock()
    caught: list[str] = []

    async def catcher(route: AsyncRoute) -> None:
        caught.append(route.request.url)
        await route.fulfill(status=200)

    async def _register_catcher(p: AsyncPage) -> None:
        await p.route(UNRELATED_APPLE_URL, catcher)

    page = await mount_async_page(mock, _register_catcher)
    await page.goto(page_url)
    await page.evaluate(FETCH_UNRELATED_APPLE_URL)
    assert caught == [UNRELATED_APPLE_URL]


async def test_license_failure_injection(
    mount_async_page: Callable[..., Awaitable[AsyncPage]], page_url: str
) -> None:
    mock = MusicKitApiMock()
    mock.endpoints.license_catalog_song = LicenseResponseGeoBlock()
    page = await mount_async_page(mock)
    await page.goto(page_url)
    assert_license_failure(await page.evaluate(FETCH_LICENSE), -1017)


async def test_license_success_returns_base64(
    mount_async_page: Callable[..., Awaitable[AsyncPage]], page_url: str
) -> None:
    mock = MusicKitApiMock()
    mock.endpoints.license_catalog_song = LicenseResponseSuccess(license=b"hello")
    page = await mount_async_page(mock)
    await page.goto(page_url)
    assert_license_success_b64(await page.evaluate(FETCH_LICENSE), b"hello")


async def test_shim_injects_eme_flavor(
    mount_async_page: Callable[..., Awaitable[AsyncPage]], page_url: str
) -> None:
    mock = MusicKitApiMock()
    mock.browser.eme_flavor = "com.widevine.alpha"
    page = await mount_async_page(mock)
    await page.goto(page_url)
    assert_eme_flavor(await page.evaluate(EVAL_EME_FLAVOR), "com.widevine.alpha")


async def test_authorize_response_endpoint_serves_live_value(
    mount_async_page: Callable[..., Awaitable[AsyncPage]], page_url: str
) -> None:
    mock = MusicKitApiMock()
    mock.browser.authorize_response = AuthorizeSuccess(
        user_token="ut", cid="cid", restricted=0
    )
    page = await mount_async_page(mock)
    await page.goto(page_url)
    assert_authorize_response_success(
        await page.evaluate(FETCH_AUTHORIZE_RESPONSE), "ut"
    )


async def test_shim_overrides_request_media_key_system_access(
    mount_async_page: Callable[..., Awaitable[AsyncPage]], page_url: str
) -> None:
    mock = MusicKitApiMock()
    mock.browser.eme_flavor = "com.widevine.alpha"
    page = await mount_async_page(mock)
    await page.goto(page_url)
    assert_widevine_granted(await page.evaluate(REQUEST_WIDEVINE_ACCESS))


async def test_shim_rejects_non_active_flavor(
    mount_async_page: Callable[..., Awaitable[AsyncPage]], page_url: str
) -> None:
    mock = MusicKitApiMock()
    mock.browser.eme_flavor = "com.widevine.alpha"
    page = await mount_async_page(mock)
    await page.goto(page_url)
    assert_not_supported_error(await page.evaluate(REQUEST_PLAYREADY_ACCESS))


async def test_oauth_popup_shim_dispatches_authorize_message(
    mount_async_page: Callable[..., Awaitable[AsyncPage]], page_url: str
) -> None:
    mock = MusicKitApiMock()
    mock.browser.authorize_response = AuthorizeSuccess(
        user_token="my-token", cid="my-cid", restricted=0
    )
    page = await mount_async_page(mock)
    await page.goto(page_url)
    assert_authorize_message(
        await page.evaluate(OPEN_OAUTH_POPUP_AND_RECEIVE), "my-token", "my-cid"
    )


async def test_handler_error_aborts_fetch(
    mount_async_page: Callable[..., Awaitable[AsyncPage]], page_url: str
) -> None:
    """Mock raising during request handling aborts the route, failing the fetch.

    A bare ``MusicKitApiMock()`` has every endpoint setter unset, so the
    storefront resolver raises ``ValueError`` when reached. The adapter
    catches that and calls ``route.abort``; the browser sees a network
    failure rather than a stray status or a hang.
    """
    mock = MusicKitApiMock()  # storefront unset → resolver raises on lookup
    page = await mount_async_page(mock)
    await page.goto(page_url)
    assert_fetch_aborted(await page.evaluate(FETCH_STOREFRONT_AND_REPORT_OUTCOME))


def _basic_storefront(mock: MusicKitApiMock) -> None:
    mock.endpoints.storefront = StorefrontResponseSuccess(
        storefront=Storefront(
            id="us",
            name="United States",
            default_language_tag="en-US",
            supported_language_tags=["en-US"],
            explicit_content_policy="allowed",
        )
    )
    mock.endpoints.account = AccountResponseSuccess(
        account=Account(subscription_active=True, subscription_storefront="us")
    )


async def test_genre_singular_endpoint_intercepted(
    mount_async_page: Callable[..., Awaitable[AsyncPage]], page_url: str
) -> None:
    mock = MusicKitApiMock()
    _basic_storefront(mock)
    mock.data.genres = {
        "20": Genre(name="Pop", url="https://music.apple.com/us/genre/20")
    }
    page = await mount_async_page(mock)
    await page.goto(page_url)
    assert_genre_singular_response(await page.evaluate(FETCH_GENRE_SINGULAR))


async def test_recommendation_singular_endpoint_intercepted(
    mount_async_page: Callable[..., Awaitable[AsyncPage]], page_url: str
) -> None:
    mock = MusicKitApiMock()
    _basic_storefront(mock)
    mock.data.personal_recommendations = {
        "rec1": PersonalRecommendation(
            title="Recommended Playlists",
            is_group_recommendation=False,
            kind="music-recommendations",
            contents=[PersonalRecommendationContent(type="playlists", id="pl1")],
        )
    }
    mock.data.playlists = {
        "pl1": Playlist(
            name="P",
            playlist_type="editorial",
            curator_name="C",
            has_collaboration=False,
            is_chart=False,
            audio_traits=[],
            supports_sing=False,
            url="https://music.apple.com/us/playlist/pl1",
        )
    }
    page = await mount_async_page(mock)
    await page.goto(page_url)
    assert_recommendation_singular_response(
        await page.evaluate(FETCH_RECOMMENDATION_SINGULAR)
    )


async def test_catalog_song_library_endpoint_intercepted(
    mount_async_page: Callable[..., Awaitable[AsyncPage]], page_url: str
) -> None:
    mock = MusicKitApiMock()
    _basic_storefront(mock)
    art = Artwork(url="https://example.com/a.jpg", width=640, height=640)
    mock.data.songs = {
        "1": Song(
            title="T",
            artist="A",
            album="Al",
            duration_ms=1,
            artwork=art,
            genres=[],
            has_lyrics=False,
            audio_locale="en-US",
            audio_traits=[],
            has_time_synced_lyrics=False,
            is_apple_digital_master=False,
            is_mastered_for_itunes=False,
            is_vocal_attenuation_allowed=False,
            url="https://music.apple.com/us/song/1",
            hls_layout=HlsLayout(
                target_duration_sec=1,
                init_byte_offset=0,
                init_byte_length=0,
                chunks=(HlsChunk(duration_sec=1.0, byte_offset=0, byte_length=0),),
            ),
            hls_segment=b"",
            preview_audio=b"",
            bitrate=256,
            sample_rate=44100,
            file_size=0,
            library_song_id="i.s1",
        )
    }
    mock.data.library_songs = {
        "i.s1": LibrarySong(
            name="LT",
            artist_name="LA",
            artwork=Artwork(url="https://example.com/lib.jpg", width=300, height=300),
            duration_ms=1,
            genre_names=[],
            has_lyrics=False,
        )
    }
    page = await mount_async_page(mock)
    await page.goto(page_url)
    assert_song_library_response(await page.evaluate(FETCH_SONG_LIBRARY))


def _catalog_artwork() -> Artwork:
    return Artwork(url="https://example.com/a.jpg", width=640, height=640)


def _library_artwork() -> Artwork:
    return Artwork(url="https://example.com/lib.jpg", width=300, height=300)


def _make_artist(*, station_id: str | None = None) -> Artist:
    return Artist(
        name="A",
        genre_names=[],
        url="https://music.apple.com/us/artist/ar1",
        station_id=station_id,
    )


def _make_station() -> Station:
    return Station(
        name="St",
        artwork=_catalog_artwork(),
        is_live=False,
        media_kind="audio",
        url="https://music.apple.com/us/station/ra.978194965",
        is_tracks_station=False,
        has_drm=False,
        kind="radio",
        radio_url="https://itsliveradio.apple.com/x/index-cmaf.m3u8",
        requires_subscription=False,
        radio_show_id="cu1",
    )


def _make_minimal_song() -> Song:
    return Song(
        title="T",
        artist="A",
        album="Al",
        duration_ms=1,
        artwork=_catalog_artwork(),
        genres=[],
        has_lyrics=False,
        audio_locale="en-US",
        audio_traits=[],
        has_time_synced_lyrics=False,
        is_apple_digital_master=False,
        is_mastered_for_itunes=False,
        is_vocal_attenuation_allowed=False,
        url="https://music.apple.com/us/song/1",
        hls_layout=HlsLayout(
            target_duration_sec=1,
            init_byte_offset=0,
            init_byte_length=0,
            chunks=(HlsChunk(duration_sec=1.0, byte_offset=0, byte_length=0),),
        ),
        hls_segment=b"",
        preview_audio=b"",
        bitrate=256,
        sample_rate=44100,
        file_size=0,
    )


async def test_artist_station_endpoint_intercepted(
    mount_async_page: Callable[..., Awaitable[AsyncPage]], page_url: str
) -> None:
    mock = MusicKitApiMock()
    _basic_storefront(mock)
    mock.data.artists = {"ar1": _make_artist(station_id="ra.978194965")}
    mock.data.stations = {"ra.978194965": _make_station()}
    page = await mount_async_page(mock)
    await page.goto(page_url)
    assert_artist_station_response(await page.evaluate(FETCH_ARTIST_STATION))


async def test_music_video_songs_endpoint_intercepted(
    mount_async_page: Callable[..., Awaitable[AsyncPage]], page_url: str
) -> None:
    mock = MusicKitApiMock()
    _basic_storefront(mock)
    mock.data.music_videos = {
        "mv1": MusicVideo(
            name="MV",
            artist_name="A",
            artwork=_catalog_artwork(),
            duration_ms=1,
            genre_names=[],
            has_4k=False,
            has_hdr=False,
            url="https://music.apple.com/us/music-video/mv1",
            previews=[Preview(url="https://example.com/p.mp4")],
            video_traits=[],
            song_ids=["1"],
        )
    }
    mock.data.songs = {"1": _make_minimal_song()}
    page = await mount_async_page(mock)
    await page.goto(page_url)
    assert_music_video_songs_response(await page.evaluate(FETCH_MUSIC_VIDEO_SONGS))


async def test_album_record_labels_endpoint_intercepted(
    mount_async_page: Callable[..., Awaitable[AsyncPage]], page_url: str
) -> None:
    mock = MusicKitApiMock()
    _basic_storefront(mock)
    mock.data.albums = {
        "a1": Album(
            name="Al",
            artist_name="A",
            artwork=_catalog_artwork(),
            genre_names=[],
            track_count=0,
            is_compilation=False,
            is_complete=True,
            is_mastered_for_itunes=False,
            is_single=True,
            is_prerelease=False,
            audio_traits=[],
            url="https://music.apple.com/us/album/a1",
            record_label_ids=["rl1"],
        )
    }
    mock.data.record_labels = {
        "rl1": RecordLabel(
            name="Label",
            url="https://music.apple.com/us/record-label/rl1",
        )
    }
    page = await mount_async_page(mock)
    await page.goto(page_url)
    assert_album_record_labels_response(await page.evaluate(FETCH_ALBUM_RECORD_LABELS))


async def test_apple_curator_playlists_endpoint_intercepted(
    mount_async_page: Callable[..., Awaitable[AsyncPage]], page_url: str
) -> None:
    mock = MusicKitApiMock()
    _basic_storefront(mock)
    mock.data.curators = {
        "cu1": Curator(
            name="C",
            type="apple-curators",
            url="https://music.apple.com/us/curator/c/cu1",
            artwork=_catalog_artwork(),
            playlist_ids=["pl1"],
        )
    }
    mock.data.playlists = {
        "pl1": Playlist(
            name="P",
            playlist_type="editorial",
            curator_name="C",
            has_collaboration=False,
            is_chart=False,
            audio_traits=[],
            supports_sing=False,
            url="https://music.apple.com/us/playlist/pl1",
            curator_id="cu1",
        )
    }
    page = await mount_async_page(mock)
    await page.goto(page_url)
    assert_apple_curator_playlists_response(
        await page.evaluate(FETCH_APPLE_CURATOR_PLAYLISTS)
    )


async def test_library_artist_albums_endpoint_intercepted(
    mount_async_page: Callable[..., Awaitable[AsyncPage]], page_url: str
) -> None:
    mock = MusicKitApiMock()
    _basic_storefront(mock)
    mock.data.library_artists = {"r.ar1": LibraryArtist(name="LA", album_ids=["l.a1"])}
    mock.data.library_albums = {
        "l.a1": LibraryAlbum(
            name="LAlbum",
            artist_name="LA",
            artwork=_library_artwork(),
            genre_names=[],
            track_count=0,
        )
    }
    page = await mount_async_page(mock)
    await page.goto(page_url)
    assert_library_artist_albums_response(
        await page.evaluate(FETCH_LIBRARY_ARTIST_ALBUMS)
    )


async def test_station_radio_show_endpoint_intercepted(
    mount_async_page: Callable[..., Awaitable[AsyncPage]], page_url: str
) -> None:
    mock = MusicKitApiMock()
    _basic_storefront(mock)
    mock.data.stations = {"ra.978194965": _make_station()}
    mock.data.curators = {
        "cu1": Curator(
            name="Radio Host",
            type="apple-curators",
            url="https://music.apple.com/us/curator/host/cu1",
            artwork=_catalog_artwork(),
        )
    }
    page = await mount_async_page(mock)
    await page.goto(page_url)
    assert_station_radio_show_response(await page.evaluate(FETCH_STATION_RADIO_SHOW))
