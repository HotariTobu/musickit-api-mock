"""HTTP request/response value types crossing the host adapter boundary."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Request:
    """HTTP request the host adapter forwards into the mock.

    Attributes:
        method: HTTP method (e.g. ``GET``, ``POST``, ``OPTIONS``).
        url: Absolute request URL including scheme, host, path, and query.
        headers: Request headers as a flat name/value mapping.
        body: Raw request body, or ``None`` for requests with no body.
    """

    method: str
    url: str
    headers: dict[str, str]
    body: bytes | None


@dataclass(frozen=True)
class Response:
    """HTTP response the mock asks the host adapter to fulfill.

    Attributes:
        status: HTTP status code.
        headers: Response headers as a flat name/value mapping.
        body: Raw response body bytes.
    """

    status: int
    headers: dict[str, str]
    body: bytes
