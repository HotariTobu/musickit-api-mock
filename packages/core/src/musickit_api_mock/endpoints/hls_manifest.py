"""HLS manifest composition with per-key-system EXT-X-KEY directives.

The manifest is composed at serve time so the EXT-X-KEY directive can be
selected from the active key system. EXT-X-KEY templates replicate Apple's
observed format; per-song values (KID, asset path) are derived from the song
id deterministically.
"""

from __future__ import annotations

import base64
import hashlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from musickit_api_mock.data.song import HlsLayout
    from musickit_api_mock.key_system import KeySystem

_SEGMENT_NAME = "index.m4s"


def _derive_kid(song_id: str) -> bytes:
    digest = hashlib.sha256(song_id.encode("utf-8")).digest()
    return b"\x00\x00\x00\x00" + digest[:12]


def _derive_asset_path(song_id: str) -> str:
    h = hashlib.sha256(song_id.encode("utf-8")).hexdigest()
    return f"{h[0:2]}/{h[2:4]}/{h[4:6]}/{h[6:14]}-{h[14:18]}-{h[18:22]}-{h[22:26]}-{h[26:38]}"


def _ext_x_key(key_system: KeySystem, song_id: str) -> str:
    if key_system == "com.widevine.alpha":
        kid_b64 = base64.b64encode(_derive_kid(song_id)).decode("ascii")
        return f'#EXT-X-KEY:METHOD=ISO-23001-7,URI="data:;base64,{kid_b64}"'
    if key_system == "com.apple.fps":
        path = _derive_asset_path(song_id)
        return (
            f"#EXT-X-KEY:METHOD=SAMPLE-AES,"
            f'URI="skd://itunes.apple.com/afs_{song_id}_31_a_/v4/{path}",'
            f'KEYFORMAT="com.apple.streamingkeydelivery",KEYFORMATVERSIONS="1"'
        )
    if key_system == "com.microsoft.playready":
        kid_b64 = base64.b64encode(_derive_kid(song_id)).decode("ascii")
        return (
            f'#EXT-X-KEY:METHOD=ISO-23001-7,URI="data:;base64,{kid_b64}",'
            f'KEYFORMAT="com.microsoft.playready"'
        )
    raise ValueError(f"Unsupported key_system: {key_system}")


def _compose_manifest(
    layout: HlsLayout, key_system: KeySystem | None, song_id: str
) -> bytes:
    lines = [
        "#EXTM3U",
        "#EXT-X-VERSION:7",
        f"#EXT-X-TARGETDURATION:{layout.target_duration_sec}",
        "#EXT-X-MEDIA-SEQUENCE:0",
        "#EXT-X-PLAYLIST-TYPE:VOD",
    ]
    if key_system is not None:
        lines.append(_ext_x_key(key_system, song_id))
    lines.append(
        f'#EXT-X-MAP:URI="{_SEGMENT_NAME}",'
        f'BYTERANGE="{layout.init_byte_length}@{layout.init_byte_offset}"'
    )
    for chunk in layout.chunks:
        lines.append(f"#EXTINF:{chunk.duration_sec:.6f},")
        lines.append(f"#EXT-X-BYTERANGE:{chunk.byte_length}@{chunk.byte_offset}")
        lines.append(_SEGMENT_NAME)
    lines.append("#EXT-X-ENDLIST")
    return ("\n".join(lines) + "\n").encode("ascii")
