from __future__ import annotations

import base64
import math
from array import array
from dataclasses import replace
from pathlib import Path
from typing import Protocol

import av
import pytest
from av.audio.frame import AudioFrame
from av.audio.resampler import AudioResampler
from av.packet import Packet
from av.stream import Disposition
from musickit_api_mock import (
    Artwork,
    CatalogSong,
    PreviewRange,
    SongMetadataFallback,
    UploadedLibrarySong,
)

_TINY_PNG = bytes.fromhex(
    "89504e470d0a1a0a"
    "0000000d49484452"
    "00000001000000010806000000"
    "1f15c489"
    "0000000d49444154"
    "789c63fcffff3f0000050001fffff7e2"
    "67d3a3e1"
    "0000000049454e44ae426082"
)


def _generate_audio(
    path: str,
    *,
    metadata: dict[str, str] | None,
    with_artwork: bool,
    suffix: str = "m4a",
) -> None:
    if suffix == "mp3":
        container = av.open(path, "w", format="mp3")
        audio = container.add_stream("mp3", rate=44100)
    else:
        container = av.open(path, "w", format="mp4")
        audio = container.add_stream("aac", rate=44100)
    if metadata:
        container.metadata.update(metadata)
    audio.layout = "mono"

    video = None
    if with_artwork:
        video = container.add_stream("png", rate=1)
        video.width = 1
        video.height = 1
        video.pix_fmt = "rgba"
        # av 17.0.1: stub types `Disposition` but the Cython setter requires int
        # coercion, and `Disposition` extends `Flag` (not `IntFlag`), so only
        # `.value` works at runtime. https://github.com/PyAV-Org/PyAV/issues/2256
        video.disposition = Disposition.attached_pic.value  # ty: ignore[invalid-assignment]

    sample_rate = 44100
    samples_per_frame = 1024
    silence = bytes(samples_per_frame * 4)
    pts = 0
    for _ in range(20):
        frame = AudioFrame(format="fltp", layout="mono", samples=samples_per_frame)
        frame.sample_rate = sample_rate
        frame.planes[0].update(silence)
        frame.pts = pts
        pts += samples_per_frame
        for pkt in audio.encode(frame):
            container.mux(pkt)
    for pkt in audio.encode(None):
        container.mux(pkt)

    if video is not None:
        pkt = Packet(_TINY_PNG)
        pkt.stream = video
        pkt.dts = 0
        pkt.pts = 0
        container.mux(pkt)

    container.close()


class AudioFactory(Protocol):
    def __call__(
        self,
        *,
        metadata: dict[str, str] | None = None,
        with_artwork: bool = False,
        suffix: str = "m4a",
    ) -> str: ...


@pytest.fixture
def make_audio(tmp_path: Path) -> AudioFactory:
    counter = 0

    def factory(
        *,
        metadata: dict[str, str] | None = None,
        with_artwork: bool = False,
        suffix: str = "m4a",
    ) -> str:
        nonlocal counter
        counter += 1
        out = tmp_path / f"song_{counter}.{suffix}"
        _generate_audio(
            str(out), metadata=metadata, with_artwork=with_artwork, suffix=suffix
        )
        return str(out)

    return factory


def _full_fallback(artwork: Artwork) -> SongMetadataFallback:
    return SongMetadataFallback(
        artwork=artwork,
        isrc="USABC1234567",
        has_lyrics=True,
        is_apple_digital_master=False,
        url="https://music.apple.com/us/song/x",
    )


def test_extracts_metadata_from_file(
    make_audio: AudioFactory, artwork_library: Artwork
) -> None:
    path = make_audio(
        metadata={
            "title": "File Title",
            "artist": "File Artist",
            "album": "File Album",
            "date": "2023-05-17",
            "track": "5",
            "disc": "2",
            "genre": "Rock",
            "composer": "File Composer",
        },
        with_artwork=True,
    )
    song = CatalogSong.from_file(path, fallback=_full_fallback(artwork_library))
    assert song.title == "File Title"
    assert song.artist == "File Artist"
    assert song.album == "File Album"
    assert song.release_date == "2023-05-17"
    assert song.track_number == 5
    assert song.disc_number == 2
    assert song.genres == ["Rock"]
    assert song.composer == "File Composer"


def test_extracts_artwork_from_file(
    make_audio: AudioFactory, artwork_library: Artwork
) -> None:
    path = make_audio(
        metadata={
            "title": "T",
            "artist": "A",
            "album": "Al",
            "date": "2024-01-01",
            "track": "1",
            "disc": "1",
            "genre": "P",
        },
        with_artwork=True,
    )
    song = CatalogSong.from_file(path, fallback=_full_fallback(artwork_library))
    assert song.artwork.url.startswith("data:image/png;base64,")
    assert song.artwork.width == 1
    assert song.artwork.height == 1


def test_falls_back_when_file_has_no_artwork(
    make_audio: AudioFactory, artwork_library: Artwork
) -> None:
    path = make_audio(
        metadata={
            "title": "T",
            "artist": "A",
            "album": "Al",
            "date": "2024-01-01",
            "track": "1",
            "disc": "1",
            "genre": "P",
        },
        with_artwork=False,
    )
    song = CatalogSong.from_file(path, fallback=_full_fallback(artwork_library))
    assert song.artwork == artwork_library


def test_falls_back_when_file_has_no_metadata(
    make_audio: AudioFactory, artwork_library: Artwork
) -> None:
    path = make_audio(metadata=None, with_artwork=True)
    fb = SongMetadataFallback(
        title="FB Title",
        artist="FB Artist",
        album="FB Album",
        isrc="USABC1234567",
        artwork=artwork_library,
        genres=["Pop"],
        release_date="2020-01-01",
        track_number=3,
        disc_number=1,
        has_lyrics=True,
        is_apple_digital_master=False,
        url="https://example.com/x",
    )
    song = CatalogSong.from_file(path, fallback=fb)
    assert song.title == "FB Title"
    assert song.artist == "FB Artist"
    assert song.album == "FB Album"
    assert song.genres == ["Pop"]
    assert song.release_date == "2020-01-01"
    assert song.track_number == 3
    assert song.disc_number == 1
    assert song.url == "https://example.com/x"


def test_track_number_with_total(
    make_audio: AudioFactory, artwork_library: Artwork
) -> None:
    path = make_audio(
        metadata={
            "title": "T",
            "artist": "A",
            "album": "Al",
            "date": "2024-01-01",
            "track": "3/12",
            "disc": "1/2",
            "genre": "P",
        },
        with_artwork=True,
    )
    song = CatalogSong.from_file(path, fallback=_full_fallback(artwork_library))
    assert song.track_number == 3
    assert song.disc_number == 1


def test_genre_comma_split(make_audio: AudioFactory, artwork_library: Artwork) -> None:
    path = make_audio(
        metadata={
            "title": "T",
            "artist": "A",
            "album": "Al",
            "date": "2024-01-01",
            "track": "1",
            "disc": "1",
            "genre": "Rock, Pop, Jazz",
        },
        with_artwork=True,
    )
    song = CatalogSong.from_file(path, fallback=_full_fallback(artwork_library))
    assert song.genres == ["Rock", "Pop", "Jazz"]


_RELEASE_DATE_BASE_TAGS = {
    "title": "T",
    "artist": "A",
    "album": "Al",
    "track": "1",
    "disc": "1",
    "genre": "P",
}


def test_release_date_prefers_original_release_tag(
    make_audio: AudioFactory, artwork_library: Artwork
) -> None:
    path = make_audio(
        metadata={**_RELEASE_DATE_BASE_TAGS, "TDOR": "2001-01-01", "date": "2023-05-17"},
        with_artwork=True,
        suffix="mp3",
    )
    song = CatalogSong.from_file(path, fallback=_full_fallback(artwork_library))
    assert song.release_date == "2001-01-01"


def test_release_date_skips_tags_not_in_iso_form(
    make_audio: AudioFactory, artwork_library: Artwork
) -> None:
    path = make_audio(
        metadata={**_RELEASE_DATE_BASE_TAGS, "TDOR": "2001", "date": "2023-05-17"},
        with_artwork=True,
        suffix="mp3",
    )
    song = CatalogSong.from_file(path, fallback=_full_fallback(artwork_library))
    assert song.release_date == "2023-05-17"


def test_release_date_falls_back_when_no_tag_is_iso(
    make_audio: AudioFactory, artwork_library: Artwork
) -> None:
    path = make_audio(
        metadata={**_RELEASE_DATE_BASE_TAGS, "date": "2023"}, with_artwork=True
    )
    fb = replace(_full_fallback(artwork_library), release_date="2020-01-01")
    song = CatalogSong.from_file(path, fallback=fb)
    assert song.release_date == "2020-01-01"


def test_release_date_missing_raises(
    make_audio: AudioFactory, artwork_library: Artwork
) -> None:
    path = make_audio(
        metadata={**_RELEASE_DATE_BASE_TAGS, "date": "2023"}, with_artwork=True
    )
    with pytest.raises(ValueError, match="missing 'release_date'"):
        CatalogSong.from_file(path, fallback=_full_fallback(artwork_library))


def test_missing_required_field_raises(
    make_audio: AudioFactory, artwork_library: Artwork
) -> None:
    path = make_audio(metadata={"artist": "A"}, with_artwork=True)
    fb = SongMetadataFallback(
        artwork=artwork_library,
        album="A",
        genres=["P"],
        release_date="2024",
        track_number=1,
        disc_number=1,
        has_lyrics=False,
        is_apple_digital_master=False,
        url="x",
    )
    with pytest.raises(ValueError, match="missing 'title'"):
        CatalogSong.from_file(path, fallback=fb)


def test_bool_fields_from_fallback(
    make_audio: AudioFactory, artwork_library: Artwork
) -> None:
    path = make_audio(
        metadata={
            "title": "T",
            "artist": "A",
            "album": "Al",
            "date": "2024-01-01",
            "track": "1",
            "disc": "1",
            "genre": "P",
        },
        with_artwork=True,
    )
    fb = SongMetadataFallback(
        artwork=artwork_library,
        isrc="USABC1234567",
        has_lyrics=True,
        is_apple_digital_master=True,
        url="https://example.com/x",
    )
    song = CatalogSong.from_file(path, fallback=fb)
    assert song.has_lyrics is True
    assert song.is_apple_digital_master is True


def test_uploaded_library_song_from_file_extracts_metadata_and_audio(
    make_audio: AudioFactory,
) -> None:
    path = make_audio(
        metadata={
            "title": "Upload Title",
            "artist": "Upload Artist",
            "album": "Upload Album",
            "track": "3/10",
            "disc": "2",
            "genre": "Soundtrack, Pop ",
        },
        with_artwork=True,
    )
    song = UploadedLibrarySong.from_file(path)
    assert song.name == "Upload Title"
    assert song.artist_name == "Upload Artist"
    assert song.album_name == "Upload Album"
    assert song.track_number == 3
    assert song.disc_number == 2
    assert song.genre_names == ["Soundtrack, Pop "]
    assert song.has_lyrics is False
    assert song.duration_ms > 0
    assert song.audio[4:12] == b"ftypM4A "
    assert song.audio != Path(path).read_bytes()


def test_uploaded_library_song_from_file_artwork_is_original_bytes_at_fixed_size(
    make_audio: AudioFactory,
) -> None:
    path = make_audio(metadata=None, with_artwork=True)
    song = UploadedLibrarySong.from_file(path)
    assert song.artwork == Artwork(
        url=f"data:image/png;base64,{base64.b64encode(_TINY_PNG).decode('ascii')}",
        width=1200,
        height=1200,
    )


def test_uploaded_library_song_from_file_without_tags(
    make_audio: AudioFactory,
) -> None:
    path = make_audio(metadata=None, with_artwork=False)
    song = UploadedLibrarySong.from_file(path)
    assert song.name == Path(path).stem
    assert song.artist_name is None
    assert song.album_name is None
    assert song.genre_names == [""]
    assert song.track_number == 0
    assert song.disc_number == 0
    assert song.artwork is None


def test_uploaded_library_song_from_file_empty_tags_count_as_absent(
    make_audio: AudioFactory,
) -> None:
    path = make_audio(
        metadata={"title": "", "artist": "", "album": "", "genre": ""},
        suffix="mp3",
    )
    song = UploadedLibrarySong.from_file(path)
    assert song.name == Path(path).stem
    assert song.artist_name is None
    assert song.album_name is None
    assert song.genre_names == [""]


def test_uploaded_library_song_from_file_keeps_whitespace_only_tags(
    make_audio: AudioFactory,
) -> None:
    path = make_audio(
        metadata={"title": "   ", "artist": "   ", "album": "   ", "genre": "   "}
    )
    song = UploadedLibrarySong.from_file(path)
    assert song.name == "   "
    assert song.artist_name == "   "
    assert song.album_name == "   "
    assert song.genre_names == ["   "]


def test_uploaded_library_song_from_file_name_strips_last_extension_only(
    make_audio: AudioFactory, tmp_path: Path
) -> None:
    generated = Path(make_audio(metadata=None))
    path = tmp_path / "my.song.name.m4a"
    generated.rename(path)
    song = UploadedLibrarySong.from_file(str(path))
    assert song.name == "my.song.name"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("0", 0),
        ("07", 7),
        (" 7 ", 7),
        ("\t\n 7", 7),
        ("\u30007", 0),
        ("\u00a07", 0),
        ("3/12", 3),
        ("3 of 12", 3),
        ("12abc", 12),
        ("+3", 3),
        ("1_0", 1),
        ("\u0661\u0662", 0),
        ("abc", 0),
        ("32767", 32767),
        ("32768", 0),
        ("-1", 0),
        ("70000", 4464),
    ],
)
def test_uploaded_library_song_from_file_track_and_disc_numbers(
    make_audio: AudioFactory, raw: str, expected: int
) -> None:
    path = make_audio(metadata={"track": raw, "disc": raw}, suffix="mp3")
    song = UploadedLibrarySong.from_file(path)
    assert song.track_number == expected
    assert song.disc_number == expected


def _pcm_samples(
    first_sample: int, count: int, tone: tuple[float, float] | None
) -> bytes:
    if tone is None:
        return bytes(count * 2)
    start, end = (int(t * 44100) for t in tone)
    samples = array("h", bytes(count * 2))
    for i in range(count):
        n = first_sample + i
        if start <= n < end:
            samples[i] = int(16000 * math.sin(2 * math.pi * 440 * n / 44100))
    return samples.tobytes()


def _generate_wav(
    path: str, *, frames: int = 20, tone: tuple[float, float] | None = None
) -> None:
    container = av.open(path, "w", format="wav")
    audio = container.add_stream("pcm_s16le", rate=44100)
    audio.layout = "mono"
    samples_per_frame = 1024
    for i in range(frames):
        frame = AudioFrame(format="s16", layout="mono", samples=samples_per_frame)
        frame.sample_rate = 44100
        frame.planes[0].update(
            _pcm_samples(i * samples_per_frame, samples_per_frame, tone)
        )
        frame.pts = i * samples_per_frame
        for pkt in audio.encode(frame):
            container.mux(pkt)
    for pkt in audio.encode(None):
        container.mux(pkt)
    container.close()


def _audio_codec(data: bytes, suffix: str, tmp_path: Path) -> str:
    probe_path = tmp_path / f"probe{suffix}"
    probe_path.write_bytes(data)
    with av.open(str(probe_path)) as container:
        return container.streams.audio[0].codec_context.name


def _transcode_to_aac(wav_path: str, m4a_path: str) -> None:
    with av.open(wav_path) as src, av.open(m4a_path, "w", format="mp4") as dst:
        out = dst.add_stream("aac", rate=44100)
        out.layout = "mono"
        for frame in src.decode(src.streams.audio[0]):
            for pkt in out.encode(frame):
                dst.mux(pkt)
        for pkt in out.encode(None):
            dst.mux(pkt)


def _decode_pcm(data: bytes, tmp_path: Path) -> array[int]:
    probe_path = tmp_path / "probe.m4a"
    probe_path.write_bytes(data)
    samples = array("h")
    resampler = AudioResampler(format="s16", layout="mono", rate=44100)

    def collect(frame: AudioFrame | None) -> None:
        for out in resampler.resample(frame):
            samples.frombytes(bytes(out.planes[0])[: out.samples * 2])

    with av.open(str(probe_path)) as container:
        for frame in container.decode(container.streams.audio[0]):
            collect(frame)
    collect(None)
    return samples


def _timeline(data: bytes, tmp_path: Path) -> tuple[int, float]:
    probe_path = tmp_path / "probe.m4a"
    probe_path.write_bytes(data)
    with av.open(str(probe_path)) as container:
        assert container.duration is not None
        return container.start_time, container.duration / av.time_base


def _rms(samples: array[int]) -> float:
    return math.sqrt(sum(s * s for s in samples) / len(samples))


@pytest.mark.parametrize("input_codec", ["pcm", "aac"])
def test_preview_range_starts_at_start_sec(
    tmp_path: Path, artwork_library: Artwork, input_codec: str
) -> None:
    path = tmp_path / "input.wav"
    _generate_wav(str(path), frames=431, tone=(3.0, 4.0))
    if input_codec == "aac":
        path = tmp_path / "input.m4a"
        _transcode_to_aac(str(tmp_path / "input.wav"), str(path))
    song = CatalogSong.from_file(
        str(path),
        replace(
            _full_fallback(artwork_library),
            title="T",
            artist="A",
            album="Al",
            genres=["G"],
            release_date="2020-01-01",
            track_number=1,
            disc_number=1,
        ),
        preview=PreviewRange(start_sec=3.0, duration_sec=2.0),
    )
    start_time, duration = _timeline(song.preview_audio, tmp_path)
    assert start_time == 0
    assert abs(duration - 2.0) < 0.1
    pcm = _decode_pcm(song.preview_audio, tmp_path)
    assert abs(len(pcm) / 44100 - 2.0) < 0.1
    assert _rms(pcm[: 44100 // 2]) > 1000
    assert _rms(pcm[-44100 // 2 :]) < 100


def test_catalog_song_from_wav_serves_aac(
    tmp_path: Path, artwork_library: Artwork
) -> None:
    path = tmp_path / "input.wav"
    _generate_wav(str(path))
    song = CatalogSong.from_file(
        str(path),
        replace(
            _full_fallback(artwork_library),
            title="T",
            artist="A",
            album="Al",
            genres=["G"],
            release_date="2020-01-01",
            track_number=1,
            disc_number=1,
        ),
    )
    assert _audio_codec(song.hls_segment, ".m4s", tmp_path) == "aac"
    assert _audio_codec(song.preview_audio, ".m4a", tmp_path) == "aac"


def test_uploaded_library_song_from_wav_serves_aac(tmp_path: Path) -> None:
    path = tmp_path / "input.wav"
    _generate_wav(str(path))
    song = UploadedLibrarySong.from_file(str(path))
    assert _audio_codec(song.audio, ".m4a", tmp_path) == "aac"
