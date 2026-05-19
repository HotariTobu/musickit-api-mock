"""Build a ``Song`` from an audio file: metadata extraction, HLS layout, preview range."""

from __future__ import annotations

import base64
import re
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Literal, overload

from av.stream import Disposition
from av.video.codeccontext import VideoCodecContext

from musickit_api_mock.data.primitives.artwork import Artwork
from musickit_api_mock.data.song import HlsChunk, HlsLayout

if TYPE_CHECKING:
    from av.container import InputContainer

    from musickit_api_mock.data.song import PreviewRange, Song, SongMetadataFallback


def _meta_get(meta: dict[str, str], *names: str) -> str | None:
    for name in names:
        if name in meta:
            value = meta[name]
            if value:
                return value
    return None


def _parse_int_field(raw: str | None) -> int | None:
    if raw is None:
        return None
    head = raw.split("/")[0].strip()
    try:
        return int(head)
    except ValueError:
        return None


def _meta_genres(meta: dict[str, str]) -> list[str] | None:
    raw = _meta_get(meta, "genre", "GENRE")
    if raw is None:
        return None
    return [s.strip() for s in raw.split(",") if s.strip()]


_STR_FILE_FIELDS: dict[str, tuple[str, ...]] = {
    "title": ("title",),
    "artist": ("artist",),
    "album": ("album",),
    "release_date": ("date", "year", "creation_time"),
    "composer": ("composer",),
    "isrc": ("ISRC", "isrc"),
}

_INT_FILE_FIELDS: dict[str, tuple[str, ...]] = {
    "track_number": ("track",),
    "disc_number": ("disc",),
}


def _missing(field: str) -> ValueError:
    return ValueError(
        f"Song.from_file: missing {field!r}. Set via SongMetadataFallback."
    )


def _wrong_type(field: str, expected: str, actual: object) -> TypeError:
    return TypeError(
        f"SongMetadataFallback.{field} must be {expected} or None, "
        f"got {type(actual).__name__}"
    )


@overload
def _pick_str(
    meta: dict[str, str],
    fallback: SongMetadataFallback,
    field: str,
    *,
    required: Literal[True],
) -> str: ...
@overload
def _pick_str(
    meta: dict[str, str],
    fallback: SongMetadataFallback,
    field: str,
    *,
    required: Literal[False],
) -> str | None: ...
def _pick_str(
    meta: dict[str, str],
    fallback: SongMetadataFallback,
    field: str,
    *,
    required: bool,
) -> str | None:
    keys = _STR_FILE_FIELDS.get(field)
    if keys is not None:
        v = _meta_get(meta, *keys)
        if v is not None:
            return v
    fb_val: object = getattr(fallback, field)
    if isinstance(fb_val, str):
        return fb_val
    if fb_val is None:
        if required:
            raise _missing(field)
        return None
    raise _wrong_type(field, "str", fb_val)


@overload
def _pick_int(
    meta: dict[str, str],
    fallback: SongMetadataFallback,
    field: str,
    *,
    required: Literal[True],
) -> int: ...
@overload
def _pick_int(
    meta: dict[str, str],
    fallback: SongMetadataFallback,
    field: str,
    *,
    required: Literal[False],
) -> int | None: ...
def _pick_int(
    meta: dict[str, str],
    fallback: SongMetadataFallback,
    field: str,
    *,
    required: bool,
) -> int | None:
    keys = _INT_FILE_FIELDS.get(field)
    if keys is not None:
        v = _parse_int_field(_meta_get(meta, *keys))
        if v is not None:
            return v
    fb_val: object = getattr(fallback, field)
    if isinstance(fb_val, bool):
        raise _wrong_type(field, "int", fb_val)
    if isinstance(fb_val, int):
        return fb_val
    if fb_val is None:
        if required:
            raise _missing(field)
        return None
    raise _wrong_type(field, "int", fb_val)


@overload
def _pick_list_str(
    meta: dict[str, str],
    fallback: SongMetadataFallback,
    field: str,
    *,
    required: Literal[True],
) -> list[str]: ...
@overload
def _pick_list_str(
    meta: dict[str, str],
    fallback: SongMetadataFallback,
    field: str,
    *,
    required: Literal[False],
) -> list[str] | None: ...
def _pick_list_str(
    meta: dict[str, str],
    fallback: SongMetadataFallback,
    field: str,
    *,
    required: bool,
) -> list[str] | None:
    if field == "genres":
        v = _meta_genres(meta)
        if v is not None:
            return v
    fb_val: object = getattr(fallback, field)
    if isinstance(fb_val, list):
        if all(isinstance(x, str) for x in fb_val):
            return fb_val
        raise _wrong_type(field, "list[str]", fb_val)
    if fb_val is None:
        if required:
            raise _missing(field)
        return None
    raise _wrong_type(field, "list[str]", fb_val)


def _pick_bool(fallback: SongMetadataFallback, field: str) -> bool:
    fb_val: object = getattr(fallback, field)
    if isinstance(fb_val, bool):
        return fb_val
    if fb_val is None:
        raise _missing(field)
    raise _wrong_type(field, "bool", fb_val)


def _extract_artwork(container: InputContainer) -> Artwork | None:
    for stream in container.streams:
        cc = stream.codec_context
        if not isinstance(cc, VideoCodecContext):
            continue
        if not (stream.disposition & Disposition.attached_pic):
            continue
        for packet in container.demux(stream):
            payload = bytes(packet)
            if not payload:
                continue
            codec_name = cc.codec.name if cc.codec else ""
            mime = "image/jpeg" if codec_name == "mjpeg" else "image/png"
            return Artwork(
                url=f"data:{mime};base64,{base64.b64encode(payload).decode('ascii')}",
                width=cc.width or 0,
                height=cc.height or 0,
            )
    return None


_BYTERANGE_RE = re.compile(r"^(\d+)(?:@(\d+))?")


def _parse_hls_layout(manifest_text: str) -> HlsLayout:
    target_duration = 0
    init_offset = 0
    init_length = 0
    chunks: list[HlsChunk] = []
    pending_duration: float | None = None
    last_chunk_end = 0
    for line in manifest_text.splitlines():
        if line.startswith("#EXT-X-TARGETDURATION:"):
            target_duration = int(line.split(":", 1)[1])
        elif line.startswith("#EXT-X-MAP:"):
            m = re.search(r'BYTERANGE="(\d+)(?:@(\d+))?"', line)
            if m is None:
                raise ValueError(f"EXT-X-MAP missing BYTERANGE: {line!r}")
            init_length = int(m.group(1))
            init_offset = int(m.group(2)) if m.group(2) else 0
        elif line.startswith("#EXTINF:"):
            duration_str = line[len("#EXTINF:") :].rstrip(",").strip()
            pending_duration = float(duration_str)
        elif line.startswith("#EXT-X-BYTERANGE:"):
            m = _BYTERANGE_RE.match(line[len("#EXT-X-BYTERANGE:") :])
            if m is None or pending_duration is None:
                raise ValueError(f"Unexpected EXT-X-BYTERANGE: {line!r}")
            length = int(m.group(1))
            offset = int(m.group(2)) if m.group(2) else last_chunk_end
            chunks.append(
                HlsChunk(
                    duration_sec=pending_duration,
                    byte_offset=offset,
                    byte_length=length,
                )
            )
            last_chunk_end = offset + length
            pending_duration = None
    if init_length == 0:
        raise ValueError("HLS layout parse: missing EXT-X-MAP")
    if not chunks:
        raise ValueError("HLS layout parse: no chunks")
    return HlsLayout(
        target_duration_sec=target_duration,
        init_byte_offset=init_offset,
        init_byte_length=init_length,
        chunks=tuple(chunks),
    )


def _build_byte_range_hls(audio_path: str) -> tuple[HlsLayout, bytes]:
    import av

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        m3u8_path = tmp_dir / "index.m3u8"
        in_container = av.open(audio_path)
        try:
            in_stream = in_container.streams.audio[0]
            out_container = av.open(
                m3u8_path,
                "w",
                format="hls",
                options={
                    "hls_flags": "single_file",
                    "hls_segment_type": "fmp4",
                    "hls_time": "2",
                    "hls_playlist_type": "vod",
                    "hls_list_size": "0",
                },
            )
            try:
                out_stream = out_container.add_stream_from_template(in_stream)
                for packet in in_container.demux(in_stream):
                    if packet.dts is None:
                        continue
                    packet.stream = out_stream
                    out_container.mux(packet)
            finally:
                out_container.close()
        finally:
            in_container.close()
        manifest_text = m3u8_path.read_text()
        seg_path = tmp_dir / "index.m4s"
        segment = seg_path.read_bytes()
        layout = _parse_hls_layout(manifest_text)
        return layout, segment


def _build_preview(
    audio_path: str, start_sec: float, duration_sec: float | None
) -> bytes:
    import av

    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "preview.m4a"
        in_container = av.open(audio_path)
        try:
            in_stream = in_container.streams.audio[0]
            if start_sec > 0:
                in_container.seek(
                    int(start_sec * 1_000_000),
                    backward=True,
                    any_frame=False,
                    stream=in_stream,
                )
            out_container = av.open(out_path, "w", format="ipod")
            try:
                out_stream = out_container.add_stream(
                    "aac", rate=in_stream.rate or 44100
                )
                end_sec = start_sec + duration_sec if duration_sec is not None else None
                done = False
                for packet in in_container.demux(in_stream):
                    if done:
                        break
                    if packet.pts is None:
                        continue
                    for frame in packet.decode():
                        if frame.pts is None or frame.time_base is None:
                            t = 0.0
                        else:
                            t = float(frame.pts) * float(frame.time_base)
                        if t < start_sec:
                            continue
                        if end_sec is not None and t >= end_sec:
                            done = True
                            break
                        for outp in out_stream.encode(frame):
                            out_container.mux(outp)
                for outp in out_stream.encode(None):
                    out_container.mux(outp)
            finally:
                out_container.close()
        finally:
            in_container.close()
        return out_path.read_bytes()


def _song_from_file(
    cls: type,
    audio_path: str,
    fallback: SongMetadataFallback | None = None,
    *,
    preview: PreviewRange | bytes | None = None,
) -> Song:
    import av

    from musickit_api_mock.data.song import PreviewRange, SongMetadataFallback

    f = fallback or SongMetadataFallback()
    container = av.open(audio_path)
    try:
        audio_stream = container.streams.audio[0]
        duration_us = container.duration or 0
        duration_ms = int(duration_us / 1000) if duration_us else 0
        bitrate_bps = audio_stream.bit_rate or 0
        bitrate_kbps = int(bitrate_bps // 1000) if bitrate_bps else 0
        sample_rate = audio_stream.rate or 0
        meta = container.metadata
        file_artwork = _extract_artwork(container)
    finally:
        container.close()

    file_size = Path(audio_path).stat().st_size
    hls_layout, hls_segment = _build_byte_range_hls(audio_path)

    if isinstance(preview, bytes):
        preview_audio = preview
    elif isinstance(preview, PreviewRange):
        preview_audio = _build_preview(
            audio_path, preview.start_sec, preview.duration_sec
        )
    else:
        preview_audio = _build_preview(audio_path, 0.0, None)

    artwork = file_artwork if file_artwork is not None else f.artwork
    if artwork is None:
        raise ValueError(
            "Song.from_file: missing artwork. Provide via SongMetadataFallback.artwork."
        )

    return cls(
        title=_pick_str(meta, f, "title", required=True),
        artist=_pick_str(meta, f, "artist", required=True),
        album=_pick_str(meta, f, "album", required=True),
        artwork=artwork,
        genres=_pick_list_str(meta, f, "genres", required=True),
        release_date=_pick_str(meta, f, "release_date", required=True),
        track_number=_pick_int(meta, f, "track_number", required=True),
        disc_number=_pick_int(meta, f, "disc_number", required=True),
        composer=_pick_str(meta, f, "composer", required=False),
        has_lyrics=_pick_bool(f, "has_lyrics"),
        isrc=_pick_str(meta, f, "isrc", required=False),
        content_rating=_pick_str(meta, f, "content_rating", required=False),
        audio_locale=_pick_str(meta, f, "audio_locale", required=True),
        audio_traits=_pick_list_str(meta, f, "audio_traits", required=True),
        has_time_synced_lyrics=_pick_bool(f, "has_time_synced_lyrics"),
        is_apple_digital_master=_pick_bool(f, "is_apple_digital_master"),
        is_mastered_for_itunes=_pick_bool(f, "is_mastered_for_itunes"),
        is_vocal_attenuation_allowed=_pick_bool(f, "is_vocal_attenuation_allowed"),
        url=_pick_str(meta, f, "url", required=True),
        duration_ms=duration_ms,
        bitrate=bitrate_kbps,
        sample_rate=sample_rate,
        file_size=file_size,
        hls_layout=hls_layout,
        hls_segment=hls_segment,
        preview_audio=preview_audio,
    )
