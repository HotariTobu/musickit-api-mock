"""License success and failure body builders."""

from __future__ import annotations

import base64
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from musickit_api_mock.endpoints.responses.license import LicenseResponseSuccess
    from musickit_api_mock.endpoints.schema.shapes import LicenseBody


def _license_success_body(resp: LicenseResponseSuccess) -> LicenseBody:
    out: LicenseBody = {
        "license": base64.b64encode(resp.license).decode("ascii"),
        "errorCode": 0,
        "status": 0,
    }
    if resp.renew_after is not None:
        out["renew-after"] = resp.renew_after
    if resp.stkn is not None:
        out["stkn"] = resp.stkn
    return out


def _license_failure_body(code: int) -> LicenseBody:
    """Failure body keyed by Apple ``errorCode`` numeric code."""
    return {"license": "", "errorCode": code, "status": code}
