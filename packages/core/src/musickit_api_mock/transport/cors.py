"""CORS preflight response and per-request CORS header construction."""

from urllib.parse import urlparse

from musickit_api_mock.transport.http import Request, Response

_HOSTS_CREDENTIAL = frozenset({"play.itunes.apple.com"})
_ALLOW_HEADERS = (
    "Authorization, Music-User-Token, X-Apple-Music-User-Token, Content-Type"
)
_ALLOW_METHODS_API = "GET,HEAD,PUT,PATCH,POST,DELETE,OPTIONS,TRACE,CONNECT"
_ALLOW_METHODS_PLAY = "POST"


def _cors_headers(req: Request) -> dict[str, str]:
    host = (urlparse(req.url).hostname or "").lower()
    origin = req.headers.get("Origin") or req.headers.get("origin")
    if host in _HOSTS_CREDENTIAL and origin:
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
        }
    return {"Access-Control-Allow-Origin": "*"}


def _cors_preflight(req: Request) -> Response:
    host = (urlparse(req.url).hostname or "").lower()
    headers = _cors_headers(req)
    headers["Access-Control-Allow-Headers"] = _ALLOW_HEADERS
    headers["Access-Control-Max-Age"] = "86400"
    if host in _HOSTS_CREDENTIAL:
        headers["Access-Control-Allow-Methods"] = _ALLOW_METHODS_PLAY
    else:
        headers["Access-Control-Allow-Methods"] = _ALLOW_METHODS_API
    return Response(status=204, headers=headers, body=b"")
