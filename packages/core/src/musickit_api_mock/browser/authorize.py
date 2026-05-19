"""Authorize flow result variants the in-page shim returns to MusicKit JS."""

from dataclasses import dataclass


@dataclass
class AuthorizeSuccess:
    """User accepted the authorize prompt; carries the issued user token and cid."""

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
