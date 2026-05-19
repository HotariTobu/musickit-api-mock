"""HTTP request/response value types crossing the host adapter boundary."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Request:
    """HTTP request the host adapter forwards into the mock."""

    method: str
    url: str
    headers: dict[str, str]
    body: bytes | None


@dataclass(frozen=True)
class Response:
    """HTTP response the mock asks the host adapter to fulfill."""

    status: int
    headers: dict[str, str]
    body: bytes
