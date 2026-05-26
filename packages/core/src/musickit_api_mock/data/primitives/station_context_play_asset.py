"""Station play asset variant."""

from dataclasses import dataclass


@dataclass
class StationContextPlayAsset:
    """One bit-rate variant of a station's play asset.

    Attributes:
        bit_rate: Bitrate of the variant in kilobits per second.
        url: URL of the variant's media.
    """

    bit_rate: int
    url: str
