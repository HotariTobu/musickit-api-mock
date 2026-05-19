"""Preview building block shared across resource types."""

from dataclasses import dataclass

from musickit_api_mock.data.primitives.artwork import Artwork


@dataclass
class Preview:
    """Preview asset reference (audio or video)."""

    url: str
    hls_url: str | None = None
    artwork: Artwork | None = None
