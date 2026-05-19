"""Handlers for ``webplayer-logout`` and ``renew-music-token``."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.endpoints.responses.logout import LogoutResponseSuccess
from musickit_api_mock.endpoints.responses.renew_token import (
    RenewTokenResponseSuccess,
    RenewTokenResponseUnauthorized,
)
from musickit_api_mock.endpoints.schema import (
    _renew_music_token_success_body,
    _session_expired_renew_401_body,
    _webplayer_logout_success_body,
)
from musickit_api_mock.transport.response_builders import _json_response

if TYPE_CHECKING:
    from musickit_api_mock.mock import MusicKitApiMock
    from musickit_api_mock.transport.http import Response


def _handle_webplayer_logout(mock: MusicKitApiMock) -> Response:
    resp = mock._endpoint_resolver.webplayer_logout()
    if isinstance(resp, LogoutResponseSuccess):
        return _json_response(_webplayer_logout_success_body())
    raise TypeError(f"Unexpected webplayer_logout response: {type(resp).__name__}")


def _handle_renew_music_token(mock: MusicKitApiMock) -> Response:
    resp = mock._endpoint_resolver.renew_music_token()
    if isinstance(resp, RenewTokenResponseSuccess):
        return _json_response(_renew_music_token_success_body(resp.music_token))
    if isinstance(resp, RenewTokenResponseUnauthorized):
        return _json_response(_session_expired_renew_401_body(), status=401)
    raise TypeError(f"Unexpected renew_music_token response: {type(resp).__name__}")
