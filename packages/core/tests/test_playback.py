from __future__ import annotations

import json
from typing import TYPE_CHECKING, cast

from musickit_api_mock import (
    Artwork,
    LibrarySong,
    MusicKitApiMock,
    PlayAssetsBroadcastAsset,
    PlayAssetsBroadcastResponseSuccess,
    PlayAssetsCatalogSongAsset,
    PlayAssetsCatalogSongResponseContentUnavailable,
    PlayAssetsCatalogSongResponseSuccess,
    PlayAssetsLiveAudioAsset,
    PlayAssetsLiveAudioResponseSubscriptionError,
    PlayAssetsLiveAudioResponseSuccess,
    PlayAssetsLiveVideoAsset,
    PlayAssetsLiveVideoResponseSuccess,
    Request,
    Station,
    UploadedLibrarySong,
    WebPlaybackAsset,
    WebPlaybackCatalogLibrarySong,
    WebPlaybackCatalogSong,
    WebPlaybackResponseGeoBlock,
    WebPlaybackResponseSuccess,
    WebPlaybackResponseUnsupportedError,
    WebPlaybackUploadedLibraryAsset,
    WebPlaybackUploadedLibraryAssetMetadata,
    WebPlaybackUploadedLibrarySong,
)

if TYPE_CHECKING:
    from tests._apple_response import WebPlaybackResponseBody


def test_p02_web_playback(mock: MusicKitApiMock) -> None:
    mock.endpoints.web_playback = WebPlaybackResponseSuccess(
        song_list=[
            WebPlaybackCatalogSong(
                song_id="1",
                hls_key_cert_url="https://s.mzstatic.com/skdtool_2021_certbundle.bin",
                hls_key_server_url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/acquireWebPlaybackLicense",
                widevine_cert_url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/widevineCert",
                assets=[
                    WebPlaybackAsset(
                        flavor="28:cbcp32",
                        url="https://aod-ssl.itunes.apple.com/itunes-assets/1/index.m3u8",
                    )
                ],
            )
        ]
    )
    body = json.dumps({"salableAdamId": "1"}).encode()
    resp = mock.handle_request(
        Request(
            method="POST",
            url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/webPlayback",
            headers={},
            body=body,
        )
    )
    assert resp is not None
    assert resp.status == 200
    parsed = json.loads(resp.body)
    assert parsed["status"] == 0
    assert parsed["songList"][0]["songId"] == "1"


def test_p03_play_assets_catalog_song(mock: MusicKitApiMock) -> None:
    mock.endpoints.play_assets_catalog_song = PlayAssetsCatalogSongResponseSuccess(
        assets=[
            PlayAssetsCatalogSongAsset(
                url="https://aod-ssl.itunes.apple.com/itunes-assets/1/index.m3u8",
                fair_play_key_certificate_url="https://s.mzstatic.com/skdtool_2021_certbundle.bin",
                key_server_url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/acquireWebPlaybackLicense",
                widevine_key_certificate_url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/widevineCert",
            )
        ]
    )
    resp = mock.handle_request(
        Request(
            method="GET",
            url="https://api.music.apple.com/v1/play/assets?id=1&kind=song&includeLicenseUrls=true&hlsEncryption=CBC",
            headers={},
            body=None,
        )
    )
    assert resp is not None
    assert resp.status == 200
    parsed = json.loads(resp.body)
    assert "assets" in parsed["results"]
    assert parsed["results"]["assets"][0]["url"].startswith("https://aod-ssl")


def test_p03_play_assets_live_audio_dispatch(mock: MusicKitApiMock) -> None:
    mock.endpoints.play_assets_live_audio = PlayAssetsLiveAudioResponseSuccess(
        assets=[
            PlayAssetsLiveAudioAsset(
                url="https://itsliveradio.apple.com/gl/ra.978194965/index-cmaf.m3u8",
                fair_play_key_certificate_url="https://s.mzstatic.com/skdtool_2021_certbundle.bin",
                key_server_url="https://linear.tv.apple.com/v1/radio/streaming-key-delivery",
                widevine_key_certificate_url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/widevineCert",
            )
        ]
    )
    resp = mock.handle_request(
        Request(
            method="GET",
            url="https://api.music.apple.com/v1/play/assets?id=ra.978194965&kind=radioStation&keyFormat=web",
            headers={},
            body=None,
        )
    )
    assert resp is not None
    assert resp.status == 200


def test_p03_play_assets_live_video_dispatch(mock: MusicKitApiMock) -> None:
    stations = cast("dict[str, Station]", mock.data.stations)
    stations["ra.live_video"] = Station(
        name="Live Video",
        artwork=stations["ra.978194965"].artwork,
        is_live=True,
        media_kind="video",
        url="https://example.com/x",
        is_tracks_station=False,
        has_drm=True,
        kind="radio",
        radio_url="https://example.com/x",
        requires_subscription=True,
    )
    mock.endpoints.play_assets_live_video = PlayAssetsLiveVideoResponseSuccess(
        assets=[
            PlayAssetsLiveVideoAsset(
                url="https://events.applemusic.com/fps/x/platform.m3u8",
                fair_play_key_certificate_url="https://s.mzstatic.com/skdtool_2021_certbundle.bin",
                key_server_url="https://linear.tv.apple.com/v1/radio/streaming-key-delivery",
                widevine_key_certificate_url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/widevineCert",
            )
        ]
    )
    resp = mock.handle_request(
        Request(
            method="GET",
            url="https://api.music.apple.com/v1/play/assets?id=ra.live_video&kind=radioStation&keyFormat=web",
            headers={},
            body=None,
        )
    )
    assert resp is not None
    assert resp.status == 200


def test_p03_play_assets_broadcast_dispatch(mock: MusicKitApiMock) -> None:
    stations = cast("dict[str, Station]", mock.data.stations)
    stations["ra.bbc"] = Station(
        name="BBC",
        artwork=stations["ra.978194965"].artwork,
        is_live=True,
        media_kind="audio",
        url="https://example.com/bbc",
        is_tracks_station=False,
        has_drm=False,
        kind="radio",
        radio_url="https://example.com/bbc",
        requires_subscription=False,
    )
    mock.endpoints.play_assets_broadcast = PlayAssetsBroadcastResponseSuccess(
        assets=[
            PlayAssetsBroadcastAsset(
                url="https://a.files.bbci.co.uk/foo.m3u8",
            )
        ]
    )
    resp = mock.handle_request(
        Request(
            method="GET",
            url="https://api.music.apple.com/v1/play/assets?id=ra.bbc&kind=radioStation&keyFormat=web",
            headers={},
            body=None,
        )
    )
    assert resp is not None
    assert resp.status == 200


def test_p03_play_assets_catalog_song_content_unavailable(
    mock: MusicKitApiMock,
) -> None:
    mock.endpoints.play_assets_catalog_song = (
        PlayAssetsCatalogSongResponseContentUnavailable()
    )
    resp = mock.handle_request(
        Request(
            method="GET",
            url="https://api.music.apple.com/v1/play/assets?id=1&kind=song&includeLicenseUrls=true",
            headers={},
            body=None,
        )
    )
    assert resp is not None
    assert resp.status == 200
    parsed = json.loads(resp.body)
    assert parsed["results"]["assets"] == []


def test_p03_play_assets_live_audio_subscription_error(mock: MusicKitApiMock) -> None:
    mock.endpoints.play_assets_live_audio = (
        PlayAssetsLiveAudioResponseSubscriptionError()
    )
    resp = mock.handle_request(
        Request(
            method="GET",
            url="https://api.music.apple.com/v1/play/assets?id=ra.978194965&kind=radioStation&keyFormat=web",
            headers={},
            body=None,
        )
    )
    assert resp is not None
    assert resp.status == 403
    parsed = json.loads(resp.body)
    assert parsed["errors"][0]["code"] == "40303"


def test_p02_web_playback_geo_block(mock: MusicKitApiMock) -> None:
    mock.endpoints.web_playback = WebPlaybackResponseGeoBlock()
    body = json.dumps({"salableAdamId": "1"}).encode()
    resp = mock.handle_request(
        Request(
            method="POST",
            url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/webPlayback",
            headers={},
            body=body,
        )
    )
    assert resp is not None
    assert resp.status == 200
    parsed = json.loads(resp.body)
    assert parsed["failureType"] == -1017


def test_p02_web_playback_unsupported_error(mock: MusicKitApiMock) -> None:
    mock.endpoints.web_playback = WebPlaybackResponseUnsupportedError()
    body = json.dumps({"salableAdamId": "1"}).encode()
    resp = mock.handle_request(
        Request(
            method="POST",
            url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/webPlayback",
            headers={},
            body=body,
        )
    )
    assert resp is not None
    assert resp.status == 200
    parsed = json.loads(resp.body)
    assert parsed["songList"] == []


def _drm_fields() -> dict[str, str]:
    return {
        "hls_key_cert_url": "https://s.mzstatic.com/skdtool_2021_certbundle.bin",
        "hls_key_server_url": "https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/acquireWebPlaybackLicense",
        "widevine_cert_url": "https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/widevineCert",
    }


def _web_playback(
    mock: MusicKitApiMock, body: dict[str, str]
) -> WebPlaybackResponseBody:
    resp = mock.handle_request(
        Request(
            method="POST",
            url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/webPlayback",
            headers={},
            body=json.dumps(body).encode(),
        )
    )
    assert resp is not None
    assert resp.status == 200
    return cast("WebPlaybackResponseBody", json.loads(resp.body))


def test_p02_web_playback_catalog_song_omits_playback_reporting(
    mock: MusicKitApiMock,
) -> None:
    mock.endpoints.web_playback = WebPlaybackResponseSuccess(
        song_list=[
            WebPlaybackCatalogSong(
                song_id="1",
                assets=[
                    WebPlaybackAsset(
                        flavor="28:cbcp32",
                        url="https://aod-ssl.itunes.apple.com/itunes-assets/1/index.m3u8",
                    )
                ],
                **_drm_fields(),
            )
        ]
    )
    song = _web_playback(mock, {"salableAdamId": "1"})["songList"][0]
    assert song["songId"] == "1"
    assert "needsPlaybackReporting" not in song


def test_p02_web_playback_catalog_library_song_needs_playback_reporting(
    mock: MusicKitApiMock,
) -> None:
    mock.endpoints.web_playback = WebPlaybackResponseSuccess(
        song_list=[
            WebPlaybackCatalogLibrarySong(
                song_id="1",
                assets=[
                    WebPlaybackAsset(
                        flavor="28:cbcp32",
                        url="https://aod-ssl.itunes.apple.com/itunes-assets/1/index.m3u8",
                    )
                ],
                **_drm_fields(),
            )
        ]
    )
    song = _web_playback(
        mock, {"subscriptionAdamId": "1", "universalLibraryId": "i.abc"}
    )["songList"][0]
    assert song["songId"] == "1"
    assert song["needsPlaybackReporting"] is True
    assert "hls-key-cert-url" in song


def test_p02_web_playback_uploaded_library_song_shape(mock: MusicKitApiMock) -> None:
    mock.endpoints.web_playback = WebPlaybackResponseSuccess(
        song_list=[
            WebPlaybackUploadedLibrarySong(
                asset=WebPlaybackUploadedLibraryAsset(
                    url="https://store-001.blobstore.apple.com/bucket/i.abc/audio",
                    metadata=WebPlaybackUploadedLibraryAssetMetadata(
                        item_name="Uploaded",
                        artist_name="Someone",
                        playlist_name="Home Recordings",
                        duration=128373,
                        kind="song",
                        cloud_id=182939138,
                    ),
                ),
                artwork_url="https://store-001.blobstore.apple.com/bucket/i.abc/image",
            )
        ]
    )
    song = _web_playback(mock, {"universalLibraryId": "i.abc"})["songList"][0]
    assert song["songId"] == -1
    assert song["needsPlaybackReporting"] is False
    assert "hls-key-cert-url" not in song
    assert (
        song["artworkURL"] == "https://store-001.blobstore.apple.com/bucket/i.abc/image"
    )
    asset = song["assets"][0]
    assert asset["URL"] == "https://store-001.blobstore.apple.com/bucket/i.abc/audio"
    assert "flavor" not in asset
    assert asset["metadata"] == {
        "itemName": "Uploaded",
        "artistName": "Someone",
        "playlistName": "Home Recordings",
        "duration": 128373,
        "kind": "song",
        "cloud-id": 182939138,
    }


def test_uploaded_audio_route_serves_library_song_audio(
    mock: MusicKitApiMock, artwork_library: Artwork
) -> None:
    mock.data.library_songs = {
        "i.abc": UploadedLibrarySong(
            name="Uploaded",
            artist_name="Someone",
            artwork=artwork_library,
            duration_ms=1000,
            genre_names=[],
            has_lyrics=False,
            audio=b"m4a-bytes",
            disc_number=0,
            track_number=0,
        )
    }
    resp = mock.handle_request(
        Request(
            method="GET",
            url="https://store-033.blobstore.apple.com/sq-mq-us-033-0001/i.abc/audio?X-Amz-Signature=x",
            headers={},
            body=None,
        )
    )
    assert resp is not None
    assert resp.status == 200
    assert resp.headers["Content-Type"] == "audio/x-m4a"
    assert resp.body == b"m4a-bytes"


def test_uploaded_audio_route_404_for_catalog_library_song(
    mock: MusicKitApiMock, library_song: LibrarySong
) -> None:
    mock.data.library_songs = {"i.abc": library_song}
    resp = mock.handle_request(
        Request(
            method="GET",
            url="https://store-033.blobstore.apple.com/bucket/i.abc/audio",
            headers={},
            body=None,
        )
    )
    assert resp is not None
    assert resp.status == 404
