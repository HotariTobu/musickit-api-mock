"""Station play asset variant."""

from dataclasses import dataclass


@dataclass
class StationContextPlayAsset:
    """One bit-rate variant of a station's play asset."""

    bit_rate: int
    url: str
