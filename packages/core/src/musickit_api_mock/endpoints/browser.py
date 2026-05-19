"""Handler for the in-page ``authorize-response`` endpoint exposed by the shim."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.surfaces import _authorize_response_to_json
from musickit_api_mock.transport.response_builders import _json_response

if TYPE_CHECKING:
    from musickit_api_mock.mock import MusicKitApiMock
    from musickit_api_mock.transport.http import Response


def _handle_authorize_response(mock: MusicKitApiMock) -> Response:
    resp = mock._browser_resolver.authorize_response()
    return _json_response(_authorize_response_to_json(resp))
