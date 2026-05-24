"""Handlers for the internal in-page endpoints the shim fetches live state from."""

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


def _handle_eme_flavor(mock: MusicKitApiMock) -> Response:
    value = mock._browser_resolver.eme_flavor()
    return _json_response({"value": value})
