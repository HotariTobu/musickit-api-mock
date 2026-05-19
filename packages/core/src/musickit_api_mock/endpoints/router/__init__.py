"""URL routing: build the Werkzeug Map and dispatch matched endpoints to handlers."""

from musickit_api_mock.endpoints.router.dispatch import _dispatch
from musickit_api_mock.endpoints.router.url_map import _build_url_map

__all__ = ["_build_url_map", "_dispatch"]
