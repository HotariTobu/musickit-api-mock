"""Preview building block shared across resource types."""

from dataclasses import dataclass

from musickit_api_mock.data.primitives.artwork import Artwork


@dataclass
class Preview:
    """Preview asset reference (audio or video).

    Attributes:
        url: Progressive download URL for the preview asset.
        hls_url: HLS playlist URL when an HLS variant is available.
        artwork: Preview-specific artwork (e.g. video poster frame).
    """

    url: str
    hls_url: str | None = None
    artwork: Artwork | None = None
