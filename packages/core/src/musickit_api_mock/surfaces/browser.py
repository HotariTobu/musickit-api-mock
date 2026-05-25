"""Browser-side state DTO and resolver for the in-page shim.

The DTO holds the user-facing browser-shim state. The resolver exposes
per-request reads of every field (callable setters re-evaluated on each
access) for the internal HTTP endpoints that serve live values to the
shim. The resolver receives the DTO via a callback so user re-assignment
of ``mock.browser.<field>`` after construction is reflected on the next
lookup.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import cast

from musickit_api_mock.browser.authorize import (
    AuthorizeClose,
    AuthorizeDecline,
    AuthorizeResponse,
    AuthorizeSuccess,
    AuthorizeSwitchUserId,
    AuthorizeUnavailable,
)
from musickit_api_mock.json_value import _JSONValue
from musickit_api_mock.key_system import KeySystem

type AuthorizeResponseSetter = (
    AuthorizeResponse | Callable[[], AuthorizeResponse] | None
)
type EmeFlavorSetter = KeySystem | Callable[[], KeySystem] | None


@dataclass
class BrowserBehavior:
    """State that lives inside the page; the browser-side shim consumes it.

    Configures the in-page shim's runtime behavior, not HTTP responses.
    Fields default to ``None``; reading an unset value raises ``ValueError``.

    Attributes:
        authorize_response: Response the shim returns from the authorize
            flow MusicKit JS opens on sign-in. Accepts either a static
            response variant or a zero-argument callable returning one (the
            callable is re-evaluated on each authorize attempt, so a fresh
            value can be returned per popup).
        eme_flavor: DRM key system the shim reports as supported when
            MusicKit JS probes Encrypted Media Extensions. Use one of the
            three key-system identifier strings.
    """

    authorize_response: AuthorizeResponseSetter = None
    eme_flavor: EmeFlavorSetter = None


def _authorize_response_to_json(resp: AuthorizeResponse) -> dict[str, _JSONValue]:
    """Serialize an authorize response variant to its JSON shape for the shim."""
    if isinstance(resp, AuthorizeSuccess):
        return {
            "kind": "AuthorizeSuccess",
            "user_token": resp.user_token,
            "cid": resp.cid,
            "restricted": resp.restricted,
        }
    if isinstance(resp, AuthorizeDecline):
        return {"kind": "AuthorizeDecline"}
    if isinstance(resp, AuthorizeClose):
        return {"kind": "AuthorizeClose"}
    if isinstance(resp, AuthorizeSwitchUserId):
        return {"kind": "AuthorizeSwitchUserId"}
    if isinstance(resp, AuthorizeUnavailable):
        return {"kind": "AuthorizeUnavailable"}
    raise TypeError(f"Unexpected AuthorizeResponse: {type(resp).__name__}")


class _BrowserResolver:
    """Library-internal lookup over the browser-state DTO.

    Receives the DTO via a callback so user re-assignment of
    ``mock.browser.<field>`` after construction is reflected on the next
    lookup. Callable setters are re-evaluated on each access so the in-page
    shim can fetch a fresh value per popup-open via the internal endpoint.
    """

    def __init__(self, get_browser: Callable[[], BrowserBehavior]) -> None:
        """Bind to the browser-state DTO via a callback."""
        self._get_browser = get_browser

    def authorize_response(self) -> AuthorizeResponse:
        """Resolve the active ``authorize_response`` setter and return its value."""
        setter = self._get_browser().authorize_response
        if setter is None:
            raise ValueError("browser.authorize_response is not set")
        if callable(setter):
            fn = cast("Callable[[], AuthorizeResponse]", setter)
            return fn()
        return setter

    def eme_flavor(self) -> KeySystem:
        """Resolve the active ``eme_flavor`` setter and return its value."""
        setter = self._get_browser().eme_flavor
        if setter is None:
            raise ValueError("browser.eme_flavor is not set")
        if callable(setter):
            return setter()
        return setter
