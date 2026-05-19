"""Handler for ``/v1/me/play-activity``."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.endpoints.responses.play_activity import (
    PlayActivityResponseSuccess,
)
from musickit_api_mock.transport.response_builders import _json_response

if TYPE_CHECKING:
    from musickit_api_mock.mock import MusicKitApiMock
    from musickit_api_mock.transport.http import Response


def _handle_play_activity(mock: MusicKitApiMock) -> Response:
    resp = mock._endpoint_resolver.play_activity()
    if isinstance(resp, PlayActivityResponseSuccess):
        return _json_response({})
    raise TypeError(f"Unexpected play_activity response: {type(resp).__name__}")
