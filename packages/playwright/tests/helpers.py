"""Test helpers: JWT generator, silence audio, playback-ready mock builder."""

from __future__ import annotations

import base64
import json
import secrets
import time
from typing import TYPE_CHECKING

import av
from av.audio.frame import AudioFrame
from musickit_api_mock import (
    Account,
    AccountResponseSuccess,
    AuthorizeSuccess,
    FairPlayCertResponseSuccess,
    LicenseResponseSuccess,
    MusicKitApiMock,
    PlayActivityResponseSuccess,
    Storefront,
    StorefrontResponseSuccess,
    WebPlaybackAsset,
    WebPlaybackResponse,
    WebPlaybackResponseSuccess,
    WebPlaybackSong,
    WidevineCertResponseSuccess,
)

if TYPE_CHECKING:
    from pathlib import Path

    from musickit_api_mock import LicenseResponse, Song


def make_test_jwt(
    team_id: str = "TESTTEAM",
    key_id: str = "TESTKEY",
    ttl_sec: int = 3600,
) -> str:
    """ES256 JWT for MusicKit.configure(). Signature is not verified by MusicKit."""

    def b64u(b: bytes) -> str:
        return base64.urlsafe_b64encode(b).decode("ascii").rstrip("=")

    header = b64u(
        json.dumps({"alg": "ES256", "kid": key_id}, separators=(",", ":")).encode()
    )
    now = int(time.time())
    payload = b64u(
        json.dumps(
            {"iss": team_id, "iat": now, "exp": now + ttl_sec},
            separators=(",", ":"),
        ).encode()
    )
    sig = b64u(secrets.token_bytes(64))
    return f"{header}.{payload}.{sig}"


def build_silence_m4a(
    out_path: Path,
    duration_sec: float = 2.0,
    sample_rate: int = 44100,
) -> None:
    """Generate a silent AAC m4a. Mono fltp, zero-initialized frames."""
    container = av.open(str(out_path), "w", format="mp4")
    audio = container.add_stream("aac", rate=sample_rate)
    audio.layout = "mono"
    samples_per_frame = 1024
    total = int(duration_sec * sample_rate)
    silence_full = bytes(samples_per_frame * 4)
    pts = 0
    while pts < total:
        n = min(samples_per_frame, total - pts)
        frame = AudioFrame(format="fltp", layout="mono", samples=n)
        frame.sample_rate = sample_rate
        frame.planes[0].update(silence_full if n == samples_per_frame else bytes(n * 4))
        frame.pts = pts
        for pkt in audio.encode(frame):
            container.mux(pkt)
        pts += n
    for pkt in audio.encode(None):
        container.mux(pkt)
    container.close()


def make_playback_ready_mock(
    songs: dict[str, Song],
    browser_name: str,
    *,
    license_response: LicenseResponse | None = None,
) -> MusicKitApiMock:
    """Wire a mock with the DRM playback chain pre-configured for one or more songs.

    Sets storefront, account, songs, the per-song ``web_playback`` dict
    (one entry keyed by song id), the browser-appropriate cert (FairPlay
    on webkit, Widevine elsewhere), the license setter (defaults to
    success; pass ``license_response`` to inject a failure), the matching
    ``eme_flavor``, and a stock ``authorize_response``.
    """
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
    mock.data.songs = songs
    web_playback_map: dict[str, WebPlaybackResponse] = {
        song_id: WebPlaybackResponseSuccess(
            song_list=[
                WebPlaybackSong(
                    song_id=song_id,
                    hls_key_cert_url="https://s.mzstatic.com/skdtool_2021_certbundle.bin",
                    hls_key_server_url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/acquireWebPlaybackLicense",
                    widevine_cert_url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/widevineCert",
                    assets=[
                        WebPlaybackAsset(
                            flavor=flavor,
                            url=f"https://aod-ssl.itunes.apple.com/itunes-assets/{song_id}/index.m3u8",
                        )
                    ],
                )
            ]
        )
        for song_id in songs
    }
    mock.endpoints.web_playback = web_playback_map
    if is_webkit:
        mock.endpoints.fairplay_cert = FairPlayCertResponseSuccess(cert=b"")
    else:
        mock.endpoints.widevine_cert = WidevineCertResponseSuccess(cert=b"")
    mock.endpoints.license_catalog_song = (
        license_response
        if license_response is not None
        else LicenseResponseSuccess(license=b"")
    )
    # MusicKit JS POSTs play activity once playback enters the playing state,
    # even when the license return path is a non-fatal failure code. Wiring
    # the setter here keeps the adapter from aborting that POST and surfacing
    # noise in stderr during DRM tests.
    mock.endpoints.play_activity = PlayActivityResponseSuccess()
    mock.browser.eme_flavor = "com.apple.fps" if is_webkit else "com.widevine.alpha"
    mock.browser.authorize_response = AuthorizeSuccess(
        user_token="user-token", cid="cid", restricted=0
    )
    return mock
