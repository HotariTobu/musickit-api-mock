"""Library entry point: MusicKitApiMock and its request handling."""

from typing import cast
from urllib.parse import urlparse

from werkzeug.exceptions import MethodNotAllowed, NotFound
from werkzeug.routing import Map, MapAdapter

from musickit_api_mock.endpoints.router import _build_url_map, _dispatch
from musickit_api_mock.shim.loader import _load_shim_script
from musickit_api_mock.surfaces import (
    BrowserBehavior,
    DataSources,
    EndpointResponses,
    _browser_state_init_script,
    _BrowserResolver,
    _DataResolver,
    _EndpointResolver,
)
from musickit_api_mock.transport.cors import _cors_headers, _cors_preflight
from musickit_api_mock.transport.heuristics import _is_musickit_related
from musickit_api_mock.transport.http import Request, Response


def _warn_possibly_musickit_related(req: Request) -> None:
    print(
        f"[musickit-api-mock] Possibly MusicKit-related: "
        f"{req.method} {req.url} — file an issue if this should be handled."
    )


class MusicKitApiMock:
    """In-process Apple Music API mock for MusicKit JS.

    Configuration is split into surfaces with distinct semantics, not just
    distinct fields. The split is load-bearing:

    - ``data`` — shared resource sources read by multiple endpoints.
    - ``endpoints`` — per-endpoint response overrides and endpoint-only state.
    - ``browser`` — state consumed by the in-page shim.

    Field-level design axes for each surface live in the corresponding
    surface class docstrings.
    """

    data: DataSources
    endpoints: EndpointResponses
    browser: BrowserBehavior

    _data_resolver: _DataResolver
    _endpoint_resolver: _EndpointResolver
    _browser_resolver: _BrowserResolver
    _url_map: Map

    def __init__(self) -> None:
        """Initialize all three surfaces with empty defaults and build the URL map."""
        self.data = DataSources()
        self.endpoints = EndpointResponses()
        self.browser = BrowserBehavior()
        self._data_resolver = _DataResolver(lambda: self.data)
        self._endpoint_resolver = _EndpointResolver(lambda: self.endpoints)
        self._browser_resolver = _BrowserResolver(lambda: self.browser)
        self._url_map = _build_url_map()

    def handle_request(self, req: Request) -> Response | None:
        """Match a request against the mock and return a response, or None to pass through."""
        if req.method == "OPTIONS":
            return _cors_preflight(req)

        parsed = urlparse(req.url)
        host = (parsed.hostname or "").lower()
        urls: MapAdapter = self._url_map.bind(server_name=host)
        try:
            endpoint, kwargs = urls.match(parsed.path, method=req.method)
        except (NotFound, MethodNotAllowed):
            if _is_musickit_related(req):
                _warn_possibly_musickit_related(req)
            return None

        # All path placeholders use the default str converter.
        resp = _dispatch(self, req, endpoint, cast("dict[str, str]", dict(kwargs)))
        if resp is None:
            return None
        merged = {**_cors_headers(req), **resp.headers}
        return Response(status=resp.status, headers=merged, body=resp.body)

    def is_musickit_related(self, req: Request) -> bool:
        """Return True if the request looks MusicKit-related (host or auth header)."""
        return _is_musickit_related(req)

    def get_shim_script(self) -> str:
        """Return the JS init script the host adapter must inject into the page."""
        return _browser_state_init_script(self.browser) + "\n;\n" + _load_shim_script()
