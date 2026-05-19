"""Handlers for ``/v1/me/storefront`` and ``/v1/me/account``."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.endpoints.query import (
    _parse_bracketed_param,
    _parse_csv_param,
)
from musickit_api_mock.endpoints.request_locale import _check_language_tag
from musickit_api_mock.endpoints.responses.account import (
    AccountResponseFailure,
    AccountResponseSessionExpired,
    AccountResponseSuccess,
)
from musickit_api_mock.endpoints.responses.storefront import (
    StorefrontResponseFailure,
    StorefrontResponseSessionExpired,
    StorefrontResponseSuccess,
)
from musickit_api_mock.endpoints.schema import (
    _account_envelope,
    _generic_error_envelope,
    _session_expired_403_envelope,
    _storefront_envelope,
)
from musickit_api_mock.transport.response_builders import _json_response

if TYPE_CHECKING:
    from musickit_api_mock.mock import MusicKitApiMock
    from musickit_api_mock.transport.http import Request, Response


_SESSION_EXPIRED_STATUS = 403
_GENERIC_FAILURE_STATUS = 500


def _handle_storefront(mock: MusicKitApiMock, req: Request) -> Response:
    if (err := _check_language_tag(req)) is not None:
        return err
    resp = mock._endpoint_resolver.storefront()
    if isinstance(resp, StorefrontResponseSuccess):
        return _json_response(_storefront_envelope(resp.storefront))
    if isinstance(resp, StorefrontResponseSessionExpired):
        return _json_response(
            _session_expired_403_envelope(), status=_SESSION_EXPIRED_STATUS
        )
    if isinstance(resp, StorefrontResponseFailure):
        return _json_response(
            _generic_error_envelope(_GENERIC_FAILURE_STATUS),
            status=_GENERIC_FAILURE_STATUS,
        )
    raise TypeError(f"Unexpected storefront response: {type(resp).__name__}")


def _handle_account(mock: MusicKitApiMock, req: Request) -> Response:
    if (err := _check_language_tag(req)) is not None:
        return err
    resp = mock._endpoint_resolver.account()
    if isinstance(resp, AccountResponseSuccess):
        emit_subscription = "subscription" in _parse_csv_param(req.url, "meta")
        challenge = _parse_bracketed_param(req.url, "challenge")
        raw_caps = challenge.get("subscriptionCapabilities", "")
        caps = [piece.strip() for piece in raw_caps.split(",") if piece.strip()]
        return _json_response(
            _account_envelope(
                resp.account,
                emit_subscription=emit_subscription,
                subscription_capabilities=caps or None,
            )
        )
    if isinstance(resp, AccountResponseSessionExpired):
        return _json_response(
            _session_expired_403_envelope(), status=_SESSION_EXPIRED_STATUS
        )
    if isinstance(resp, AccountResponseFailure):
        return _json_response(
            _generic_error_envelope(_GENERIC_FAILURE_STATUS),
            status=_GENERIC_FAILURE_STATUS,
        )
    raise TypeError(f"Unexpected account response: {type(resp).__name__}")
