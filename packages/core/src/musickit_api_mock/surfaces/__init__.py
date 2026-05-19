"""Mock configuration surfaces (DTO + library-internal lookup composer pairs).

Three surfaces, one file each, all sharing the same shape: a user-facing DTO
plus a callback-based ``Resolver`` composer that gates unset reads with
``ValueError`` (design principle 1, "no implicit defaults").
"""

from musickit_api_mock.surfaces.browser import (
    BrowserBehavior,
    _authorize_response_to_json,
    _browser_state_init_script,
    _BrowserResolver,
    _serialize_browser_state,
)
from musickit_api_mock.surfaces.data import DataSources, _DataResolver
from musickit_api_mock.surfaces.endpoint import EndpointResponses, _EndpointResolver

__all__ = [
    "BrowserBehavior",
    "DataSources",
    "EndpointResponses",
    "_BrowserResolver",
    "_DataResolver",
    "_EndpointResolver",
    "_authorize_response_to_json",
    "_browser_state_init_script",
    "_serialize_browser_state",
]
