"""Browser-side state DTO + serializer for the in-page shim.

The DTO holds the user-facing browser-shim state. Serializer functions
carry the static fields the JS shim consumes at page load. The resolver
exposes per-request reads of dynamic fields (callable setters re-evaluated
on each access) for the internal HTTP endpoint that serves live values to
the shim.

The resolver receives the DTO via a callback so user re-assignment of
``mock.browser.<field>`` after construction is reflected on the next lookup.
"""

import json
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


@dataclass
class BrowserBehavior:
    """State that lives inside the page (browser-side shim consumes it).

    Configures the in-page shim's runtime behavior, not HTTP responses.
    """

    authorize_response: AuthorizeResponseSetter = None
    eme_flavor: KeySystem | None = None


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


def _serialize_browser_state(behavior: BrowserBehavior) -> dict[str, _JSONValue]:
    """Project the static fields of the browser behavior DTO into the JSON the shim reads at load."""
    return {"eme_flavor": behavior.eme_flavor}


def _browser_state_init_script(behavior: BrowserBehavior) -> str:
    """Build the JS init script that exposes the serialized state to the in-page shim."""
    state_json = json.dumps(_serialize_browser_state(behavior))
    return (
        "(function(){"
        "var ns = window.__musickitApiMock = window.__musickitApiMock || {};"
        "ns.browser = " + state_json + ";"
        "})();"
    )


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
