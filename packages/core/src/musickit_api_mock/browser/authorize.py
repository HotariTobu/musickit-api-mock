"""Authorize flow result variants the in-page shim returns to MusicKit JS."""

from dataclasses import dataclass


@dataclass
class AuthorizeSuccess:
    """User accepted the authorize prompt; carries the issued user token.

    Attributes:
        user_token: Apple Music user token MusicKit JS stores and sends as
            the music-user-token header on subsequent requests.
        cid: The cid Apple's authorize service issues alongside the token.
        restricted: Integer the shim forwards as the restricted argument
            of MusicKit JS's authorize callback. Leave unset to forward 0.
    """

    user_token: str
    cid: str
    restricted: int | None = None


@dataclass
class AuthorizeDecline:
    """User declined the authorize prompt."""


@dataclass
class AuthorizeClose:
    """User closed the authorize prompt without choosing."""


@dataclass
class AuthorizeSwitchUserId:
    """User switched Apple ID mid-flow; MusicKit JS retries authorization."""


@dataclass
class AuthorizeUnavailable:
    """Authorize flow is not available (e.g. service unavailable)."""


AuthorizeResponse = (
    AuthorizeSuccess
    | AuthorizeDecline
    | AuthorizeClose
    | AuthorizeSwitchUserId
    | AuthorizeUnavailable
)
