"""License success and failure body builders."""

from __future__ import annotations

import base64
from typing import TYPE_CHECKING

from musickit_api_mock.endpoints.schema.builders import _strip_none

if TYPE_CHECKING:
    from musickit_api_mock.endpoints.responses.license import LicenseResponseSuccess
    from musickit_api_mock.json_value import _JSONValue


def _license_success_body(resp: LicenseResponseSuccess) -> dict[str, _JSONValue]:
    return _strip_none(
        {
            "license": base64.b64encode(resp.license).decode("ascii"),
            "errorCode": 0,
            "status": 0,
            "renew-after": resp.renew_after,
            "stkn": resp.stkn,
        }
    )


def _license_failure_body(code: int) -> dict[str, _JSONValue]:
    """Failure body keyed by Apple ``errorCode`` numeric code."""
    return {"license": "", "errorCode": code, "status": code}
