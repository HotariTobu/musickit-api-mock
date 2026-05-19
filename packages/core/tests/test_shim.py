from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
from musickit_api_mock import (
    AuthorizeClose,
    AuthorizeDecline,
    AuthorizeResponse,
    AuthorizeSuccess,
    AuthorizeSwitchUserId,
    AuthorizeUnavailable,
    MusicKitApiMock,
    Request,
)

if TYPE_CHECKING:
    from collections.abc import Callable

_AUTHORIZE_URL = "https://musickit-api-mock.invalid/browser/authorize_response"


def _get_authorize_response(mock: MusicKitApiMock) -> dict[str, object]:
    resp = mock.handle_request(
        Request(method="GET", url=_AUTHORIZE_URL, headers={}, body=None)
    )
    assert resp is not None
    assert resp.status == 200
    return json.loads(resp.body)


def test_shim_script_contains_overrides() -> None:
    m = MusicKitApiMock()
    s = m.get_shim_script()
    assert "requestMediaKeySystemAccess" in s
    assert "WebKitMediaKeys" in s
    assert "MSMediaKeys" in s
    assert "authorize.music.apple.com" in s
    assert "__musickitApiMock" in s


def test_shim_script_embeds_eme_flavor() -> None:
    m = MusicKitApiMock()
    m.browser.eme_flavor = "com.widevine.alpha"
    s = m.get_shim_script()
    assert "com.widevine.alpha" in s


def test_authorize_response_endpoint_returns_static_value() -> None:
    m = MusicKitApiMock()
    m.browser.authorize_response = AuthorizeSuccess(
        user_token="ut", cid="cid", restricted=0
    )
    body = _get_authorize_response(m)
    assert body == {
        "kind": "AuthorizeSuccess",
        "user_token": "ut",
        "cid": "cid",
        "restricted": 0,
    }


def test_authorize_response_endpoint_evaluates_callable_per_call() -> None:
    m = MusicKitApiMock()
    counter = {"n": 0}

    def make_response() -> AuthorizeSuccess:
        counter["n"] += 1
        return AuthorizeSuccess(
            user_token=f"ut-{counter['n']}", cid="cid", restricted=0
        )

    m.browser.authorize_response = make_response
    first = _get_authorize_response(m)
    second = _get_authorize_response(m)
    assert first["user_token"] == "ut-1"
    assert second["user_token"] == "ut-2"


@pytest.mark.parametrize(
    ("variant_cls", "expected_kind"),
    [
        (AuthorizeDecline, "AuthorizeDecline"),
        (AuthorizeClose, "AuthorizeClose"),
        (AuthorizeSwitchUserId, "AuthorizeSwitchUserId"),
        (AuthorizeUnavailable, "AuthorizeUnavailable"),
    ],
)
def test_authorize_response_non_success_variants_emit_kind_tag(
    variant_cls: Callable[[], AuthorizeResponse], expected_kind: str
) -> None:
    m = MusicKitApiMock()
    m.browser.authorize_response = variant_cls()
    body = _get_authorize_response(m)
    assert body == {"kind": expected_kind}
