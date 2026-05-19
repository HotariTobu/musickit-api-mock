"""Dispatch matrix for ``/v1/play/assets`` ``kind=radioStation`` requests.

The handler routes a ``radioStation`` request to one of three setters
based on the station's ``media_kind`` and ``has_drm`` fields:

- ``media_kind == "video"`` → ``play_assets_live_video``
- ``media_kind == "audio"`` and ``has_drm`` → ``play_assets_live_audio``
- ``media_kind == "audio"`` and not ``has_drm`` → ``play_assets_broadcast``

Plus two off-axis behaviors:

- ``kind == "song"`` routes to ``play_assets_catalog_song``
- ``kind`` not in {"song", "radioStation"} returns 404

A station id with no matching ``data.stations`` entry raises
``ValueError`` rather than dispatching on invented defaults.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Literal, cast

import pytest
from musickit_api_mock import (
    Artwork,
    MusicKitApiMock,
    PlayAssetsBroadcastAsset,
    PlayAssetsBroadcastContext,
    PlayAssetsBroadcastResponseSuccess,
    PlayAssetsCatalogSongAsset,
    PlayAssetsCatalogSongContext,
    PlayAssetsCatalogSongResponseSuccess,
    PlayAssetsLiveAudioAsset,
    PlayAssetsLiveAudioContext,
    PlayAssetsLiveAudioResponseSuccess,
    PlayAssetsLiveVideoAsset,
    PlayAssetsLiveVideoContext,
    PlayAssetsLiveVideoResponseSuccess,
    Request,
    Station,
)

if TYPE_CHECKING:
    from tests._apple_response import _AppleResponse


def _get(mock: MusicKitApiMock, url: str) -> tuple[int, _AppleResponse]:
    resp = mock.handle_request(Request(method="GET", url=url, headers={}, body=None))
    assert resp is not None
    return resp.status, json.loads(resp.body)


def _add_station(
    mock: MusicKitApiMock,
    station_id: str,
    *,
    media_kind: Literal["audio", "video"],
    has_drm: bool,
) -> None:
    stations = cast("dict[str, Station]", mock.data.stations)
    stations[station_id] = Station(
        name="X",
        artwork=Artwork(url="x", width=1, height=1),
        is_live=True,
        media_kind=media_kind,
        url="x",
        is_tracks_station=False,
        has_drm=has_drm,
        kind="radio",
        radio_url="x",
        requires_subscription=True,
    )


_DRM_ASSET_URLS = {
    "fair_play_key_certificate_url": "https://s.mzstatic.com/skdtool_2021_certbundle.bin",
    "key_server_url": "https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/acquireWebPlaybackLicense",
    "widevine_key_certificate_url": "https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/widevineCert",
}


def test_kind_song_dispatches_to_catalog_song_setter(mock: MusicKitApiMock) -> None:
    captured: list[str] = []

    def fn(ctx: PlayAssetsCatalogSongContext) -> PlayAssetsCatalogSongResponseSuccess:
        captured.append(ctx.adam_id)
        return PlayAssetsCatalogSongResponseSuccess(
            assets=[PlayAssetsCatalogSongAsset(url="x", **_DRM_ASSET_URLS)]
        )

    mock.endpoints.play_assets_catalog_song = fn
    status, _ = _get(mock, "https://api.music.apple.com/v1/play/assets?id=1&kind=song")
    assert status == 200
    assert captured == ["1"]


def test_radio_station_audio_with_drm_dispatches_to_live_audio(
    mock: MusicKitApiMock,
) -> None:
    _add_station(mock, "ra.audio_drm", media_kind="audio", has_drm=True)
    captured: list[str] = []

    def fn(ctx: PlayAssetsLiveAudioContext) -> PlayAssetsLiveAudioResponseSuccess:
        captured.append(ctx.station_id)
        return PlayAssetsLiveAudioResponseSuccess(
            assets=[PlayAssetsLiveAudioAsset(url="x", **_DRM_ASSET_URLS)]
        )

    mock.endpoints.play_assets_live_audio = fn
    status, _ = _get(
        mock,
        "https://api.music.apple.com/v1/play/assets?id=ra.audio_drm&kind=radioStation",
    )
    assert status == 200
    assert captured == ["ra.audio_drm"]


def test_radio_station_audio_no_drm_dispatches_to_broadcast(
    mock: MusicKitApiMock,
) -> None:
    _add_station(mock, "ra.bcast", media_kind="audio", has_drm=False)
    captured: list[str] = []

    def fn(ctx: PlayAssetsBroadcastContext) -> PlayAssetsBroadcastResponseSuccess:
        captured.append(ctx.station_id)
        return PlayAssetsBroadcastResponseSuccess(
            assets=[PlayAssetsBroadcastAsset(url="x")]
        )

    mock.endpoints.play_assets_broadcast = fn
    status, _ = _get(
        mock,
        "https://api.music.apple.com/v1/play/assets?id=ra.bcast&kind=radioStation",
    )
    assert status == 200
    assert captured == ["ra.bcast"]


def test_radio_station_video_with_drm_dispatches_to_live_video(
    mock: MusicKitApiMock,
) -> None:
    _add_station(mock, "ra.video_drm", media_kind="video", has_drm=True)
    captured: list[str] = []

    def fn(ctx: PlayAssetsLiveVideoContext) -> PlayAssetsLiveVideoResponseSuccess:
        captured.append(ctx.station_id)
        return PlayAssetsLiveVideoResponseSuccess(
            assets=[PlayAssetsLiveVideoAsset(url="x", **_DRM_ASSET_URLS)]
        )

    mock.endpoints.play_assets_live_video = fn
    status, _ = _get(
        mock,
        "https://api.music.apple.com/v1/play/assets?id=ra.video_drm&kind=radioStation",
    )
    assert status == 200
    assert captured == ["ra.video_drm"]


def test_radio_station_video_no_drm_still_dispatches_to_live_video(
    mock: MusicKitApiMock,
) -> None:
    """``media_kind == "video"`` takes precedence over ``has_drm``."""
    _add_station(mock, "ra.video_no_drm", media_kind="video", has_drm=False)
    captured: list[str] = []

    def fn(ctx: PlayAssetsLiveVideoContext) -> PlayAssetsLiveVideoResponseSuccess:
        captured.append(ctx.station_id)
        return PlayAssetsLiveVideoResponseSuccess(
            assets=[PlayAssetsLiveVideoAsset(url="x", **_DRM_ASSET_URLS)]
        )

    mock.endpoints.play_assets_live_video = fn
    status, _ = _get(
        mock,
        "https://api.music.apple.com/v1/play/assets?id=ra.video_no_drm&kind=radioStation",
    )
    assert status == 200
    assert captured == ["ra.video_no_drm"]


def test_radio_station_unknown_id_raises_valueerror(
    mock: MusicKitApiMock,
) -> None:
    """A station id absent from ``data.stations`` raises ``ValueError``."""
    mock.data.stations = {}
    with pytest.raises(ValueError, match="stations"):
        _get(
            mock,
            "https://api.music.apple.com/v1/play/assets?id=ra.unknown&kind=radioStation",
        )


def test_unknown_kind_returns_400_empty_body(mock: MusicKitApiMock) -> None:
    resp = mock.handle_request(
        Request(
            method="GET",
            url="https://api.music.apple.com/v1/play/assets?id=x&kind=movie",
            headers={},
            body=None,
        )
    )
    assert resp is not None
    assert resp.status == 400
    assert resp.body == b""
