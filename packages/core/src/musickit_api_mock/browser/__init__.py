"""Browser-side authorize flow result variants."""

from musickit_api_mock.browser.authorize import (
    AuthorizeClose,
    AuthorizeDecline,
    AuthorizeResponse,
    AuthorizeSuccess,
    AuthorizeSwitchUserId,
    AuthorizeUnavailable,
)

__all__ = [
    "AuthorizeClose",
    "AuthorizeDecline",
    "AuthorizeResponse",
    "AuthorizeSuccess",
    "AuthorizeSwitchUserId",
    "AuthorizeUnavailable",
]
