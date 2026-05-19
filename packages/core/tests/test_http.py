from dataclasses import FrozenInstanceError

import pytest
from musickit_api_mock import Request, Response


def test_request_is_frozen() -> None:
    r = Request(method="GET", url="https://x", headers={}, body=None)
    with pytest.raises(FrozenInstanceError):
        r.__setattr__("method", "POST")


def test_response_construct() -> None:
    r = Response(status=200, headers={"X": "y"}, body=b"hello")
    assert r.status == 200
    assert r.body == b"hello"
