from __future__ import annotations

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
    UploadedLibrarySongMetadataFallback,
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
) -> None:
    container = av.open(path, "w", format="mp4")
    if metadata:
        container.metadata.update(metadata)

    audio = container.add_stream("aac", rate=44100)
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
        self, *, metadata: dict[str, str] | None = None, with_artwork: bool = False
    ) -> str: ...


@pytest.fixture
def make_audio(tmp_path: Path) -> AudioFactory:
    counter = 0

    def factory(
        *, metadata: dict[str, str] | None = None, with_artwork: bool = False
    ) -> str:
        nonlocal counter
        counter += 1
        out = tmp_path / f"song_{counter}.m4a"
        _generate_audio(str(out), metadata=metadata, with_artwork=with_artwork)
        return str(out)

    return factory


def _full_fallback(artwork: Artwork) -> SongMetadataFallback:
    return SongMetadataFallback(
        artwork=artwork,
        has_lyrics=True,
        audio_locale="en-US",
        audio_traits=["lossless"],
        has_time_synced_lyrics=False,
        is_apple_digital_master=False,
        is_mastered_for_itunes=True,
        is_vocal_attenuation_allowed=False,
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
            "date": "2023",
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
    assert song.release_date == "2023"
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
            "date": "2024",
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
            "date": "2024",
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
        artwork=artwork_library,
        genres=["Pop"],
        release_date="2020-01-01",
        track_number=3,
        disc_number=1,
        has_lyrics=True,
        audio_locale="en-US",
        audio_traits=["lossless"],
        has_time_synced_lyrics=False,
        is_apple_digital_master=False,
        is_mastered_for_itunes=True,
        is_vocal_attenuation_allowed=False,
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
            "date": "2024",
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
            "date": "2024",
            "track": "1",
            "disc": "1",
            "genre": "Rock, Pop, Jazz",
        },
        with_artwork=True,
    )
    song = CatalogSong.from_file(path, fallback=_full_fallback(artwork_library))
    assert song.genres == ["Rock", "Pop", "Jazz"]


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
        audio_locale="en-US",
        audio_traits=[],
        has_time_synced_lyrics=False,
        is_apple_digital_master=False,
        is_mastered_for_itunes=False,
        is_vocal_attenuation_allowed=False,
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
            "date": "2024",
            "track": "1",
            "disc": "1",
            "genre": "P",
        },
        with_artwork=True,
    )
    fb = SongMetadataFallback(
        artwork=artwork_library,
        has_lyrics=True,
        audio_locale="en-US",
        audio_traits=["lossless"],
        has_time_synced_lyrics=True,
        is_apple_digital_master=True,
        is_mastered_for_itunes=False,
        is_vocal_attenuation_allowed=True,
        url="https://example.com/x",
    )
    song = CatalogSong.from_file(path, fallback=fb)
    assert song.has_lyrics is True
    assert song.has_time_synced_lyrics is True
    assert song.is_apple_digital_master is True
    assert song.is_mastered_for_itunes is False
    assert song.is_vocal_attenuation_allowed is True


def test_uploaded_library_song_from_file_extracts_metadata_and_audio(
    make_audio: AudioFactory,
) -> None:
    path = make_audio(
        metadata={
            "title": "Upload Title",
            "artist": "Upload Artist",
            "album": "Upload Album",
            "track": "3/10",
            "disc": "1",
            "genre": "Soundtrack",
        },
        with_artwork=True,
    )
    song = UploadedLibrarySong.from_file(
        path, UploadedLibrarySongMetadataFallback(has_lyrics=False)
    )
    assert song.name == "Upload Title"
    assert song.artist_name == "Upload Artist"
    assert song.album_name == "Upload Album"
    assert song.track_number == 3
    assert song.disc_number == 1
    assert song.genre_names == ["Soundtrack"]
    assert song.has_lyrics is False
    assert song.duration_ms > 0
    assert song.audio[4:12] == b"ftypM4A "
    assert song.audio != Path(path).read_bytes()


def test_uploaded_library_song_from_file_falls_back_when_tags_missing(
    make_audio: AudioFactory, artwork_library: Artwork
) -> None:
    path = make_audio(metadata=None, with_artwork=False)
    song = UploadedLibrarySong.from_file(
        path,
        UploadedLibrarySongMetadataFallback(
            name="FB Name",
            artist_name="FB Artist",
            artwork=artwork_library,
            genre_names=["FB"],
            has_lyrics=True,
        ),
    )
    assert song.name == "FB Name"
    assert song.artist_name == "FB Artist"
    assert song.artwork == artwork_library
    assert song.genre_names == ["FB"]
    assert song.album_name is None


def test_uploaded_library_song_from_file_missing_required_field_raises(
    make_audio: AudioFactory, artwork_library: Artwork
) -> None:
    path = make_audio(metadata=None, with_artwork=False)
    with pytest.raises(ValueError, match="missing 'name'"):
        UploadedLibrarySong.from_file(
            path,
            UploadedLibrarySongMetadataFallback(
                artwork=artwork_library, genre_names=[], has_lyrics=False
            ),
        )


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


def test_uploaded_library_song_from_wav_serves_aac(
    tmp_path: Path, artwork_library: Artwork
) -> None:
    path = tmp_path / "input.wav"
    _generate_wav(str(path))
    song = UploadedLibrarySong.from_file(
        str(path),
        UploadedLibrarySongMetadataFallback(
            name="T",
            artist_name="A",
            artwork=artwork_library,
            genre_names=[],
            has_lyrics=False,
        ),
    )
    assert _audio_codec(song.audio, ".m4a", tmp_path) == "aac"
