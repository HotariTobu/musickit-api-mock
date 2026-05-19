"""End-to-end tests that load real MusicKit JS and exercise its public API.

Distinguished from ``test_intercept_sync.py`` (which calls ``fetch`` / EME APIs
directly). These tests verify that MusicKit JS, going through its actual
internal request chain, is fully served by the mock — including the all-intercept
guarantee that no musickit-related request leaks past the mock.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from musickit_api_mock import (
    Account,
    AccountResponseSuccess,
    Album,
    Artwork,
    AuthorizeSuccess,
    FairPlayCertResponseSuccess,
    LibraryMusicVideo,
    LicenseResponse,
    LicenseResponseAuthorizationError,
    LicenseResponseDeviceLimit,
    LicenseResponseGeoBlock,
    LicenseResponseMediaLicense,
    LicenseResponseNotFound,
    LicenseResponsePlayReadyCbcEncryptionError,
    LicenseResponseStreamUpsell,
    LicenseResponseSuccess,
    LicenseResponseTokenExpired,
    LicenseResponseWidevineCdmExpired,
    MusicKitApiMock,
    MusicVideo,
    Playlist,
    Storefront,
    StorefrontResponseSuccess,
    WebPlaybackAsset,
    WebPlaybackResponseSuccess,
    WebPlaybackSong,
    WidevineCertResponseSuccess,
)

from tests.helpers import make_playback_ready_mock
from tests.scenarios_musickit import (
    AUTHORIZE,
    LOAD_AND_CONFIGURE,
    PLAY_AND_AWAIT_ERROR,
    PLAY_AND_AWAIT_PLAYING,
    PLAY_AND_SKIP_TO_NEXT,
    SET_QUEUE_AND_GET_ITEM,
    SET_QUEUE_AND_RECORD_FETCHES,
    SET_QUEUE_FROM_ALBUM,
    SET_QUEUE_FROM_PLAYLIST,
    UNAUTHORIZE,
    assert_authorize_succeeded,
    assert_configured,
    assert_playback_error,
    assert_playback_error_code,
    assert_queue_contains_ids,
    assert_queue_item_resolved,
    assert_queue_resolved_without_chain,
    assert_reached_playing,
    assert_skipped_to_next,
    assert_unauthorize_clears,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from musickit_api_mock import Song
    from playwright.sync_api import Page


pytestmark = [
    pytest.mark.sync_test,
    pytest.mark.usefixtures("assert_no_musickit_leaks"),
]


def test_configure_succeeds(
    mount_sync_page: Callable[..., Page],
    page_url: str,
    dev_token: str,
) -> None:
    mock = MusicKitApiMock()
    page = mount_sync_page(mock)
    page.goto(page_url)
    assert_configured(page.evaluate(LOAD_AND_CONFIGURE, dev_token), "us")


def test_set_queue_resolves_song(
    mount_sync_page: Callable[..., Page],
    page_url: str,
    silence_song: Song,
    dev_token: str,
) -> None:
    mock = MusicKitApiMock()
    mock.data.songs = {"s1": silence_song}
    page = mount_sync_page(mock)
    page.goto(page_url)
    page.evaluate(LOAD_AND_CONFIGURE, dev_token)
    assert_queue_item_resolved(page.evaluate(SET_QUEUE_AND_GET_ITEM, "s1"), "s1")


def test_authorize_completes(
    mount_sync_page: Callable[..., Page],
    page_url: str,
    dev_token: str,
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
    mock.browser.authorize_response = AuthorizeSuccess(
        user_token="user-token", cid="cid", restricted=0
    )
    page = mount_sync_page(mock)
    page.goto(page_url)
    page.evaluate(LOAD_AND_CONFIGURE, dev_token)
    assert_authorize_succeeded(page.evaluate(AUTHORIZE), "user-token")


def test_unauthorize_clears_authorization(
    mount_sync_page: Callable[..., Page],
    page_url: str,
    dev_token: str,
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
    mock.browser.authorize_response = AuthorizeSuccess(
        user_token="user-token", cid="cid", restricted=0
    )
    page = mount_sync_page(mock)
    page.goto(page_url)
    page.evaluate(LOAD_AND_CONFIGURE, dev_token)
    assert_unauthorize_clears(page.evaluate(UNAUTHORIZE))


def test_drm_playback_reaches_playing(
    mount_sync_page: Callable[..., Page],
    page_url: str,
    silence_song: Song,
    browser_name: str,
    dev_token: str,
) -> None:
    is_webkit = browser_name == "webkit"
    flavor = "30:cbcp256" if is_webkit else "30:ctrp256"
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
    mock.data.songs = {"s1": silence_song}
    mock.endpoints.web_playback = WebPlaybackResponseSuccess(
        song_list=[
            WebPlaybackSong(
                song_id="s1",
                hls_key_cert_url="https://s.mzstatic.com/skdtool_2021_certbundle.bin",
                hls_key_server_url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/acquireWebPlaybackLicense",
                widevine_cert_url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/widevineCert",
                assets=[
                    WebPlaybackAsset(
                        flavor=flavor,
                        url="https://aod-ssl.itunes.apple.com/itunes-assets/s1/index.m3u8",
                    )
                ],
            )
        ]
    )
    if is_webkit:
        mock.endpoints.fairplay_cert = FairPlayCertResponseSuccess(cert=b"")
    else:
        mock.endpoints.widevine_cert = WidevineCertResponseSuccess(cert=b"")
    mock.endpoints.license_catalog_song = LicenseResponseSuccess(license=b"")
    mock.browser.eme_flavor = "com.apple.fps" if is_webkit else "com.widevine.alpha"
    mock.browser.authorize_response = AuthorizeSuccess(
        user_token="user-token", cid="cid", restricted=0
    )
    page = mount_sync_page(mock)
    page.goto(page_url)
    page.evaluate(LOAD_AND_CONFIGURE, dev_token)
    page.evaluate(AUTHORIZE)
    assert_reached_playing(page.evaluate(PLAY_AND_AWAIT_PLAYING, "s1"))


def test_license_failure_aborts_playback(
    mount_sync_page: Callable[..., Page],
    page_url: str,
    silence_song: Song,
    browser_name: str,
    dev_token: str,
) -> None:
    mock = make_playback_ready_mock(
        {"s1": silence_song}, browser_name, license_response=LicenseResponseGeoBlock()
    )
    page = mount_sync_page(mock)
    page.goto(page_url)
    page.evaluate(LOAD_AND_CONFIGURE, dev_token)
    page.evaluate(AUTHORIZE)
    assert_playback_error(page.evaluate(PLAY_AND_AWAIT_ERROR, "s1"))


@pytest.mark.parametrize(
    ("license_response_factory", "expected_code"),
    [
        (LicenseResponseMediaLicense, "MEDIA_LICENSE"),
        (LicenseResponseDeviceLimit, "DEVICE_LIMIT"),
        (LicenseResponseNotFound, "NOT_FOUND"),
        (LicenseResponseAuthorizationError, "AUTHORIZATION_ERROR"),
        (LicenseResponseTokenExpired, "TOKEN_EXPIRED"),
        (LicenseResponseStreamUpsell, "STREAM_UPSELL"),
        (LicenseResponsePlayReadyCbcEncryptionError, "PLAYREADY_CBC_ENCRYPTION_ERROR"),
        (LicenseResponseWidevineCdmExpired, "WIDEVINE_CDM_EXPIRED"),
    ],
)
def test_license_failure_variant_surfaces_as_media_playback_error(
    mount_sync_page: Callable[..., Page],
    page_url: str,
    silence_song: Song,
    browser_name: str,
    dev_token: str,
    license_response_factory: Callable[[], LicenseResponse],
    expected_code: str,
) -> None:
    """Each license failure code MusicKit JS surfaces as ``mediaPlaybackError``.

    The codes here are the ones empirically confirmed (see
    ``test_probe_c_failure_codes.py``) to dispatch
    ``mediaPlaybackError`` with the matching ``errorCode`` string. The
    silent codes ``SubscriptionError`` (3063) / ``ContentUnavailable``
    (3076) / ``ContentRestricted`` (3082) / ``ServerError`` (5002) are
    intentionally omitted: MusicKit JS does not dispatch
    ``mediaPlaybackError`` for those, and the same firing/silent split
    holds across chromium / firefox / webkit (browser-independent).
    """
    mock = make_playback_ready_mock(
        {"s1": silence_song},
        browser_name,
        license_response=license_response_factory(),
    )
    page = mount_sync_page(mock)
    page.goto(page_url)
    page.evaluate(LOAD_AND_CONFIGURE, dev_token)
    page.evaluate(AUTHORIZE)
    assert_playback_error_code(page.evaluate(PLAY_AND_AWAIT_ERROR, "s1"), expected_code)


def test_skip_to_next_in_multi_track_queue(
    mount_sync_page: Callable[..., Page],
    page_url: str,
    silence_song: Song,
    browser_name: str,
    dev_token: str,
) -> None:
    """Multi-song queue + ``skipToNextItem`` advances to a fresh license POST + new now-playing."""
    mock = make_playback_ready_mock(
        {"s1": silence_song, "s2": silence_song}, browser_name
    )
    page = mount_sync_page(mock)
    page.goto(page_url)
    page.evaluate(LOAD_AND_CONFIGURE, dev_token)
    page.evaluate(AUTHORIZE)
    assert_skipped_to_next(page.evaluate(PLAY_AND_SKIP_TO_NEXT, ["s1", "s2"]))


def test_set_queue_from_album_resolves_tracks(
    mount_sync_page: Callable[..., Page],
    page_url: str,
    silence_song: Song,
    dev_token: str,
) -> None:
    """``mk.setQueue({ album })`` resolves to the album's track ids."""
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
    mock.data.songs = {"s1": silence_song, "s2": silence_song}
    mock.data.albums = {
        "a1": Album(
            name="Test Album",
            artist_name="Test Artist",
            artwork=Artwork(url="https://example.com/a.jpg", width=1, height=1),
            genre_names=[],
            track_count=2,
            is_compilation=False,
            is_complete=True,
            is_mastered_for_itunes=False,
            is_single=False,
            is_prerelease=False,
            audio_traits=[],
            url="https://music.apple.com/us/album/a1",
            track_ids=["s1", "s2"],
        )
    }
    page = mount_sync_page(mock)
    page.goto(page_url)
    page.evaluate(LOAD_AND_CONFIGURE, dev_token)
    assert_queue_contains_ids(page.evaluate(SET_QUEUE_FROM_ALBUM, "a1"), ["s1", "s2"])


def test_set_queue_from_playlist_resolves_tracks(
    mount_sync_page: Callable[..., Page],
    page_url: str,
    silence_song: Song,
    dev_token: str,
) -> None:
    """``mk.setQueue({ playlist })`` resolves to the playlist's track ids."""
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
    mock.data.songs = {"s1": silence_song}
    mock.data.playlists = {
        "pl.test": Playlist(
            name="Test PL",
            playlist_type="user-shared",
            curator_name="Test Curator",
            has_collaboration=False,
            is_chart=False,
            audio_traits=[],
            supports_sing=False,
            url="https://music.apple.com/us/playlist/pl.test",
            artwork=Artwork(url="https://example.com/p.jpg", width=1, height=1),
            last_modified="2024-01-01",
            track_ids=["s1"],
        )
    }
    page = mount_sync_page(mock)
    page.goto(page_url)
    page.evaluate(LOAD_AND_CONFIGURE, dev_token)
    assert_queue_contains_ids(page.evaluate(SET_QUEUE_FROM_PLAYLIST, "pl.test"), ["s1"])


# These three tests pin the empirical fetch shape of setQueue for music-video
# and song sources: resolution completes via the batch / singular endpoint
# alone, without firing standalone relationship requests (the song composers
# endpoint, or the music-videos /<id>/{albums,artists} endpoints under both
# catalog and library). The recorded fetch window captures every request
# MusicKit JS issued between the call and its completion, so a future
# MusicKit JS version that starts emitting those paths during basic setQueue
# would surface here as a test failure.
def test_set_queue_from_music_video_no_relationship_chain(
    mount_sync_page: Callable[..., Page],
    page_url: str,
    dev_token: str,
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
    mock.data.music_videos = {
        "mv1": MusicVideo(
            name="Test MV",
            artist_name="Test Artist",
            artwork=Artwork(url="https://example.com/mv.jpg", width=1, height=1),
            duration_ms=30_000,
            genre_names=[],
            has_4k=False,
            has_hdr=False,
            url="https://music.apple.com/us/music-video/mv1",
            previews=[],
            video_traits=[],
            album_ids=["a1"],
            artist_ids=["ar1"],
        )
    }
    page = mount_sync_page(mock)
    page.goto(page_url)
    page.evaluate(LOAD_AND_CONFIGURE, dev_token)
    assert_queue_resolved_without_chain(
        page.evaluate(
            SET_QUEUE_AND_RECORD_FETCHES, {"kind": "musicVideo", "id": "mv1"}
        ),
        expected_ids=["mv1"],
        forbidden_substrings=(
            "/v1/catalog/us/music-videos/mv1/albums",
            "/v1/catalog/us/music-videos/mv1/artists",
        ),
    )


def test_set_queue_from_library_music_video_no_relationship_chain(
    mount_sync_page: Callable[..., Page],
    page_url: str,
    dev_token: str,
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
    mock.browser.authorize_response = AuthorizeSuccess(
        user_token="user-token", cid="cid", restricted=0
    )
    mock.data.library_music_videos = {
        "i.mv1": LibraryMusicVideo(
            name="Library MV",
            artist_name="Test Artist",
            artwork=Artwork(url="https://example.com/lmv.jpg", width=1, height=1),
            duration_ms=30_000,
            genre_names=[],
            album_ids=["l.a1"],
            artist_ids=["r.ar1"],
        )
    }
    page = mount_sync_page(mock)
    page.goto(page_url)
    page.evaluate(LOAD_AND_CONFIGURE, dev_token)
    page.evaluate(AUTHORIZE)
    assert_queue_resolved_without_chain(
        page.evaluate(
            SET_QUEUE_AND_RECORD_FETCHES, {"kind": "musicVideo", "id": "i.mv1"}
        ),
        expected_ids=["i.mv1"],
        forbidden_substrings=(
            "/v1/me/library/music-videos/i.mv1/albums",
            "/v1/me/library/music-videos/i.mv1/artists",
        ),
    )


def test_set_queue_from_song_no_composers_chain(
    mount_sync_page: Callable[..., Page],
    page_url: str,
    silence_song: Song,
    dev_token: str,
) -> None:
    mock = MusicKitApiMock()
    mock.data.songs = {"s1": silence_song}
    page = mount_sync_page(mock)
    page.goto(page_url)
    page.evaluate(LOAD_AND_CONFIGURE, dev_token)
    assert_queue_resolved_without_chain(
        page.evaluate(SET_QUEUE_AND_RECORD_FETCHES, {"kind": "song", "id": "s1"}),
        expected_ids=["s1"],
        forbidden_substrings=(
            "/v1/catalog/us/songs/s1/composers",
            "/v1/catalog/us/songs/s1/albums",
            "/v1/catalog/us/songs/s1/artists",
        ),
    )
