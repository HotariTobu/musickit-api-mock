"""Logout and renew-music-token success body builders."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from musickit_api_mock.endpoints.schema.shapes import (
        LogoutBody,
        RenewTokenBody,
    )


def _webplayer_logout_success_body() -> LogoutBody:
    return {"status": 0}


def _renew_music_token_success_body(music_token: str | None) -> RenewTokenBody:
    out: RenewTokenBody = {}
    if music_token is not None:
        out["music-token"] = music_token
    return out
