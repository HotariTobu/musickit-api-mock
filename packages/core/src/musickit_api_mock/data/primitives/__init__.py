"""Resource composition primitives shared across multiple resource types."""

from musickit_api_mock.data.primitives.artwork import Artwork
from musickit_api_mock.data.primitives.description import Description
from musickit_api_mock.data.primitives.editorial_notes import EditorialNotes
from musickit_api_mock.data.primitives.preview import Preview
from musickit_api_mock.data.primitives.station_context_play_asset import (
    StationContextPlayAsset,
)

__all__ = [
    "Artwork",
    "Description",
    "EditorialNotes",
    "Preview",
    "StationContextPlayAsset",
]
