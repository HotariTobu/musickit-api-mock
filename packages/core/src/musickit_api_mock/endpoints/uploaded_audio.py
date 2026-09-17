"""Handler for fetching the audio file of an uploaded library song."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.data.library_song import UploadedLibrarySong
from musickit_api_mock.data.lookup import LookupContext
from musickit_api_mock.transport.response_builders import (
    _bytes_response,
    _empty_response,
)

if TYPE_CHECKING:
    from musickit_api_mock.mock import MusicKitApiMock
    from musickit_api_mock.transport.http import Response


def _handle_uploaded_audio(mock: MusicKitApiMock, library_song_id: str) -> Response:
    library_song = mock._data_resolver.library_song.get(
        LookupContext(library_song_id, None)
    )
    if not isinstance(library_song, UploadedLibrarySong):
        return _empty_response(status=404)
    return _bytes_response(library_song.audio, content_type="audio/x-m4a")
