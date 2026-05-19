"""Construct ``Response`` instances for JSON, byte, or empty bodies."""

import json

from musickit_api_mock.transport.http import Response


def _json_response(
    body: object, *, status: int = 200, extra_headers: dict[str, str] | None = None
) -> Response:
    headers = {"Content-Type": "application/json;charset=utf-8"}
    if extra_headers:
        headers.update(extra_headers)
    return Response(
        status=status,
        headers=headers,
        body=json.dumps(body, separators=(",", ":")).encode("utf-8"),
    )


def _empty_response(status: int = 200, *, content_type: str | None = None) -> Response:
    headers: dict[str, str] = {}
    if content_type is not None:
        headers["Content-Type"] = content_type
    return Response(status=status, headers=headers, body=b"")


def _bytes_response(
    body: bytes,
    *,
    status: int = 200,
    content_type: str = "application/octet-stream",
) -> Response:
    return Response(
        status=status,
        headers={"Content-Type": content_type},
        body=body,
    )
