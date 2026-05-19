"""HLS manifest content: structural directives and key-system branching.

The manifest is emitted as bytes by ``hls.manifest`` handler. The shape
under test is the small set of directives MusicKit JS / hls.js parse:
``EXT-X-VERSION``, ``EXT-X-TARGETDURATION``, ``EXT-X-MAP``,
``EXTINF`` / ``EXT-X-BYTERANGE`` per chunk, ``EXT-X-ENDLIST``, plus the
``EXT-X-KEY`` directive whose method depends on the configured
``browser.eme_flavor``. The tests verify each directive's structural
presence (not its exact byte sequence) so manifest formatting tweaks
that preserve semantics don't break the assertions.
"""

from __future__ import annotations

from typing import cast

from musickit_api_mock import MusicKitApiMock, Request, Song


def _fetch_manifest(mock: MusicKitApiMock, song_id: str) -> str:
    resp = mock.handle_request(
        Request(
            method="GET",
            url=f"https://aod-ssl.itunes.apple.com/itunes-assets/{song_id}/index.m3u8",
            headers={},
            body=None,
        )
    )
    assert resp is not None
    assert resp.status == 200
    return resp.body.decode("ascii")


def test_manifest_emits_required_directives(mock: MusicKitApiMock) -> None:
    body = _fetch_manifest(mock, "1")
    assert body.startswith("#EXTM3U")
    assert "#EXT-X-VERSION:" in body
    assert "#EXT-X-TARGETDURATION:" in body
    assert "#EXT-X-MAP:" in body
    assert body.rstrip("\n").endswith("#EXT-X-ENDLIST")


def test_manifest_target_duration_matches_layout(
    mock: MusicKitApiMock,
) -> None:
    """Target duration in manifest equals ``Song.hls_layout.target_duration_sec``."""
    body = _fetch_manifest(mock, "1")
    songs = cast("dict[str, Song]", mock.data.songs)
    expected = songs["1"].hls_layout.target_duration_sec
    assert f"#EXT-X-TARGETDURATION:{expected}" in body


def test_manifest_emits_one_chunk_block_per_layout_chunk(
    mock: MusicKitApiMock,
) -> None:
    """Each ``HlsChunk`` produces one ``EXTINF`` + one ``EXT-X-BYTERANGE``."""
    body = _fetch_manifest(mock, "1")
    songs = cast("dict[str, Song]", mock.data.songs)
    expected_chunks = len(songs["1"].hls_layout.chunks)
    assert body.count("#EXTINF:") == expected_chunks
    assert body.count("#EXT-X-BYTERANGE:") == expected_chunks


def test_manifest_widevine_emits_iso_23001_7_method(
    mock: MusicKitApiMock,
) -> None:
    mock.browser.eme_flavor = "com.widevine.alpha"
    body = _fetch_manifest(mock, "1")
    assert "#EXT-X-KEY:" in body
    assert "METHOD=ISO-23001-7" in body


def test_manifest_fairplay_emits_sample_aes_method(
    mock: MusicKitApiMock,
) -> None:
    mock.browser.eme_flavor = "com.apple.fps"
    body = _fetch_manifest(mock, "1")
    assert "#EXT-X-KEY:" in body
    assert "METHOD=SAMPLE-AES" in body
    assert 'KEYFORMAT="com.apple.streamingkeydelivery"' in body


def test_manifest_playready_emits_iso_23001_7_with_keyformat(
    mock: MusicKitApiMock,
) -> None:
    mock.browser.eme_flavor = "com.microsoft.playready"
    body = _fetch_manifest(mock, "1")
    assert "#EXT-X-KEY:" in body
    assert "METHOD=ISO-23001-7" in body
    assert 'KEYFORMAT="com.microsoft.playready"' in body


def test_manifest_no_eme_flavor_omits_key_directive(
    mock: MusicKitApiMock,
) -> None:
    """When no ``eme_flavor`` is set, no ``EXT-X-KEY`` directive is emitted."""
    mock.browser.eme_flavor = None
    body = _fetch_manifest(mock, "1")
    assert "#EXT-X-KEY:" not in body


def test_manifest_kid_differs_per_song_id() -> None:
    """The KID (and thus the data: URI) is derived deterministically from the song id."""
    from musickit_api_mock import (
        Artwork,
        HlsChunk,
        HlsLayout,
        Song,
    )

    def _song(title: str) -> Song:
        return Song(
            title=title,
            artist="A",
            album="Al",
            duration_ms=1,
            artwork=Artwork(url="x", width=1, height=1),
            genres=[],
            has_lyrics=False,
            audio_locale="en-US",
            audio_traits=[],
            has_time_synced_lyrics=False,
            is_apple_digital_master=False,
            is_mastered_for_itunes=False,
            is_vocal_attenuation_allowed=False,
            url="x",
            hls_layout=HlsLayout(
                target_duration_sec=1,
                init_byte_offset=0,
                init_byte_length=0,
                chunks=(HlsChunk(duration_sec=1.0, byte_offset=0, byte_length=0),),
            ),
            hls_segment=b"",
            preview_audio=b"",
            bitrate=1,
            sample_rate=1,
            file_size=1,
        )

    m = MusicKitApiMock()
    m.data.songs = {"alpha": _song("A"), "beta": _song("B")}
    m.browser.eme_flavor = "com.widevine.alpha"
    a = _fetch_manifest(m, "alpha")
    b = _fetch_manifest(m, "beta")
    # Both manifests carry an EXT-X-KEY but with distinct payloads.
    assert "#EXT-X-KEY:" in a
    assert "#EXT-X-KEY:" in b
    assert a != b
