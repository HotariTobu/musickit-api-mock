"""Logout and renew-music-token success body builders."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.endpoints.schema.builders import _strip_none

if TYPE_CHECKING:
    from musickit_api_mock.json_value import _JSONValue


def _webplayer_logout_success_body() -> dict[str, _JSONValue]:
    return {"status": 0}


def _renew_music_token_success_body(music_token: str | None) -> dict[str, _JSONValue]:
    return _strip_none({"music-token": music_token})
