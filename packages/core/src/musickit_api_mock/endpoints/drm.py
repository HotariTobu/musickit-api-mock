"""Handlers for DRM cert fetch and license-acquire endpoints."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, cast

from musickit_api_mock.endpoints.playback_failure_codes import (
    _LICENSE_FAILURE_CODES,
)
from musickit_api_mock.endpoints.responses.fairplay_cert import (
    FairPlayCertResponseFailure,
    FairPlayCertResponseSuccess,
)
from musickit_api_mock.endpoints.responses.license import (
    LicenseCatalogSongContext,
    LicenseHlsOffersContext,
    LicenseLiveRadioContext,
    LicenseResponse,
    LicenseResponseSuccess,
)
from musickit_api_mock.endpoints.responses.widevine_cert import (
    WidevineCertResponseFailure,
    WidevineCertResponseSuccess,
)
from musickit_api_mock.endpoints.schema import (
    _license_failure_body,
    _license_success_body,
)
from musickit_api_mock.transport.response_builders import (
    _bytes_response,
    _empty_response,
    _json_response,
)

if TYPE_CHECKING:
    from musickit_api_mock.json_value import _JSONValue
    from musickit_api_mock.key_system import KeySystem
    from musickit_api_mock.mock import MusicKitApiMock
    from musickit_api_mock.transport.http import Request, Response


_CERT_FAILURE_STATUS = 500


def _handle_widevine_cert(mock: MusicKitApiMock) -> Response:
    resp = mock._endpoint_resolver.widevine_cert()
    if isinstance(resp, WidevineCertResponseSuccess):
        return _bytes_response(resp.cert)
    if isinstance(resp, WidevineCertResponseFailure):
        return _empty_response(status=_CERT_FAILURE_STATUS)
    raise TypeError(f"Unexpected widevine_cert response: {type(resp).__name__}")


def _handle_fairplay_cert(mock: MusicKitApiMock) -> Response:
    resp = mock._endpoint_resolver.fairplay_cert()
    if isinstance(resp, FairPlayCertResponseSuccess):
        return _bytes_response(resp.cert)
    if isinstance(resp, FairPlayCertResponseFailure):
        return _empty_response(status=_CERT_FAILURE_STATUS)
    raise TypeError(f"Unexpected fairplay_cert response: {type(resp).__name__}")


def _decode_license_body(body: bytes | None) -> dict[str, _JSONValue]:
    if not body:
        return {}
    text = body.decode("utf-8", errors="replace").strip()
    if not text:
        return {}
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return {}
    if not isinstance(parsed, dict):
        return {}
    return parsed


def _license_failure_body_code(resp: LicenseResponse) -> int:
    code = _LICENSE_FAILURE_CODES.get(type(resp))
    if code is None:
        raise TypeError(f"Unexpected license response: {type(resp).__name__}")
    return code


def _serialize_license_response(resp: LicenseResponse) -> Response:
    if isinstance(resp, LicenseResponseSuccess):
        return _json_response(_license_success_body(resp))
    return _json_response(_license_failure_body(_license_failure_body_code(resp)))


def _handle_acquire_web_playback_license(
    mock: MusicKitApiMock, req: Request
) -> Response:
    body = _decode_license_body(req.body)
    if "key-system" not in body:
        raise ValueError("license request body missing 'key-system'")
    key_system = cast("KeySystem", body["key-system"])
    requests = body.get("license-requests")
    if isinstance(requests, list) and requests:
        first = requests[0]
        if isinstance(first, dict):
            first_dict = cast("dict[str, _JSONValue]", first)
            adam_id = str(first_dict.get("adam-id", ""))
        else:
            adam_id = ""
        resp = mock._endpoint_resolver.license_hls_offers(
            LicenseHlsOffersContext(adam_id=adam_id, key_system=key_system)
        )
    else:
        adam_id = str(body.get("adamId", ""))
        if adam_id.startswith("ra."):
            resp = mock._endpoint_resolver.license_live_radio(
                LicenseLiveRadioContext(station_id=adam_id, key_system=key_system)
            )
        else:
            resp = mock._endpoint_resolver.license_catalog_song(
                LicenseCatalogSongContext(
                    adam_id=adam_id,
                    key_system=key_system,
                    is_library=bool(body.get("isLibrary", False)),
                )
            )
    return _serialize_license_response(resp)


def _handle_streaming_key_delivery(mock: MusicKitApiMock, req: Request) -> Response:
    body = _decode_license_body(req.body)
    if "key-system" not in body:
        raise ValueError("license request body missing 'key-system'")
    key_system = cast("KeySystem", body["key-system"])
    adam_id = str(body.get("adamId", ""))
    resp = mock._endpoint_resolver.license_live_radio(
        LicenseLiveRadioContext(station_id=adam_id, key_system=key_system)
    )
    return _serialize_license_response(resp)
