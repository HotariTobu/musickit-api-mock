"""Library entry point: MusicKitApiMock and its request handling."""

import json
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


def _build_browser_snapshot_script(browser: BrowserBehavior) -> str:
    eme_flavor = browser.eme_flavor
    if not isinstance(eme_flavor, str):
        return ""
    return (
        "(function () {\n"
        "  var ns = (window.__musickitApiMock = window.__musickitApiMock || {});\n"
        "  ns.browser = ns.browser || {};\n"
        f"  ns.browser.eme_flavor = {json.dumps(eme_flavor)};\n"
        "})();\n;\n"
    )


class MusicKitApiMock:
    """In-process Apple Music API mock for MusicKit JS.

    Configuration is split into surfaces with distinct semantics, not just
    distinct fields. The split is load-bearing:

    - ``mock.data`` — shared resource sources read by multiple endpoints.
    - ``mock.endpoints`` — per-endpoint response overrides and endpoint-only state.
    - ``mock.browser`` — state consumed by the in-page shim.

    Field-level design axes for each surface live on the surface objects.

    Attributes:
        data: Shared resource sources (catalog and library) read by multiple
            endpoints. Assign per-resource sources as ``mock.data.<field>``.
        endpoints: Per-endpoint response overrides and endpoint-only state.
            Assign per-endpoint setters as ``mock.endpoints.<field>``.
        browser: State consumed by the in-page shim. Assign per-field
            behavior as ``mock.browser.<field>``.
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
        """Match a request against the mock and return a response, or pass through.

        Host adapters call this with each intercepted request. The mock matches
        on host, path, and method; for matched requests it produces a response,
        for unmatched requests it returns nothing so the adapter can let the
        request continue to the network.

        Args:
            req: The intercepted HTTP request.

        Returns:
            The response the host adapter should fulfill, or ``None`` if the
            request did not match any handled path (the adapter should let it
            pass through).
        """
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
        """Report whether a request looks MusicKit-related.

        Used by host adapters to decide which requests to log or surface as
        "possibly should have been mocked" when no handler matched.

        Args:
            req: The request to classify.

        Returns:
            ``True`` if the request targets a MusicKit-recognized host or
            carries the MusicKit authorization header, ``False`` otherwise.
        """
        return _is_musickit_related(req)

    def get_shim_script(self) -> str:
        """Return the JS init script the host adapter must inject into the page.

        Prepends a synchronous snapshot of any browser-state field whose
        current value is static (non-callable). Sync legacy paths in the
        shim install before the async fetch resolves when a snapshot is
        present; callable forms are evaluated per-probe via the internal
        endpoint and are not snapshotted.

        Returns:
            JavaScript source ready to be added as a page init script (e.g.
            via Playwright's ``add_init_script``).
        """
        return _build_browser_snapshot_script(self.browser) + _load_shim_script()
