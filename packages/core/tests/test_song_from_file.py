from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

import av
import pytest
from av.audio.frame import AudioFrame
from av.packet import Packet
from av.stream import Disposition
from musickit_api_mock import Artwork, Song, SongMetadataFallback

if TYPE_CHECKING:
    from pathlib import Path

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
    song = Song.from_file(path, fallback=_full_fallback(artwork_library))
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
    song = Song.from_file(path, fallback=_full_fallback(artwork_library))
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
    song = Song.from_file(path, fallback=_full_fallback(artwork_library))
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
    song = Song.from_file(path, fallback=fb)
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
    song = Song.from_file(path, fallback=_full_fallback(artwork_library))
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
    song = Song.from_file(path, fallback=_full_fallback(artwork_library))
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
        Song.from_file(path, fallback=fb)


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
    song = Song.from_file(path, fallback=fb)
    assert song.has_lyrics is True
    assert song.has_time_synced_lyrics is True
    assert song.is_apple_digital_master is True
    assert song.is_mastered_for_itunes is False
    assert song.is_vocal_attenuation_allowed is True
