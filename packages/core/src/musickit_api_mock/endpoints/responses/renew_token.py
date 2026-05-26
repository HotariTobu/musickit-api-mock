"""Responses for the music-token renewal endpoint."""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class RenewTokenResponseSuccess:
    """200 success carrying the renewed music token.

    Attributes:
        music_token: Renewed music token. Leave unset to emit a 200 with no
            token body, matching Apple's no-renewal response.
    """

    music_token: str | None = None


@dataclass
class RenewTokenResponseUnauthorized:
    """401 response that triggers MusicKit's user-token revoke."""


RenewTokenResponse = RenewTokenResponseSuccess | RenewTokenResponseUnauthorized


type RenewTokenSetter = RenewTokenResponse | Callable[[], RenewTokenResponse] | None
