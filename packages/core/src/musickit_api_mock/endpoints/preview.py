"""Handler for fetching preview audio bytes for a song."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.data.lookup import LookupContext
from musickit_api_mock.transport.response_builders import (
    _bytes_response,
    _empty_response,
)

if TYPE_CHECKING:
    from musickit_api_mock.mock import MusicKitApiMock
    from musickit_api_mock.transport.http import Response


def _handle_preview(mock: MusicKitApiMock, song_id: str) -> Response:
    song = mock._data_resolver.song.get(LookupContext(song_id, None))
    if song is None:
        return _empty_response(status=404)
    return _bytes_response(song.preview_audio, content_type="audio/mp4")
