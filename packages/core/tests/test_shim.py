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

    from musickit_api_mock.key_system import KeySystem

_AUTHORIZE_URL = "https://musickit-api-mock.invalid/browser/authorize_response"
_EME_FLAVOR_URL = "https://musickit-api-mock.invalid/browser/eme_flavor"


def _get_authorize_response(mock: MusicKitApiMock) -> dict[str, object]:
    resp = mock.handle_request(
        Request(method="GET", url=_AUTHORIZE_URL, headers={}, body=None)
    )
    assert resp is not None
    assert resp.status == 200
    return json.loads(resp.body)


def _get_eme_flavor(mock: MusicKitApiMock) -> dict[str, object]:
    resp = mock.handle_request(
        Request(method="GET", url=_EME_FLAVOR_URL, headers={}, body=None)
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


def test_shim_script_includes_static_eme_flavor_snapshot() -> None:
    m = MusicKitApiMock()
    m.browser.eme_flavor = "com.apple.fps"
    s = m.get_shim_script()
    # The snapshot must precede the shim body so the sync legacy-path
    # install sees the value before the async fetch resolves.
    snapshot_idx = s.find('ns.browser.eme_flavor = "com.apple.fps"')
    setup_idx = s.find("function setup()")
    assert snapshot_idx != -1
    assert setup_idx != -1
    assert snapshot_idx < setup_idx


def test_shim_script_omits_snapshot_for_callable_eme_flavor() -> None:
    m = MusicKitApiMock()
    m.browser.eme_flavor = lambda: "com.apple.fps"
    s = m.get_shim_script()
    # Callable forms are evaluated per-probe via the internal endpoint;
    # snapshotting the callable's identity would freeze a stale value. The
    # shim body assigns ns.browser.eme_flavor from the fetch result, so the
    # snapshot is identified by the literal-string assignment shape.
    assert 'ns.browser.eme_flavor = "' not in s


def test_shim_script_omits_snapshot_when_eme_flavor_unset() -> None:
    m = MusicKitApiMock()
    s = m.get_shim_script()
    assert 'ns.browser.eme_flavor = "' not in s


def test_eme_flavor_endpoint_returns_static_value() -> None:
    m = MusicKitApiMock()
    m.browser.eme_flavor = "com.widevine.alpha"
    body = _get_eme_flavor(m)
    assert body == {"value": "com.widevine.alpha"}


def test_eme_flavor_endpoint_evaluates_callable_per_call() -> None:
    m = MusicKitApiMock()
    counter = {"n": 0}
    flavors: list[KeySystem] = ["com.widevine.alpha", "com.apple.fps"]

    def pick_flavor() -> KeySystem:
        flavor = flavors[counter["n"] % len(flavors)]
        counter["n"] += 1
        return flavor

    m.browser.eme_flavor = pick_flavor
    first = _get_eme_flavor(m)
    second = _get_eme_flavor(m)
    assert first == {"value": "com.widevine.alpha"}
    assert second == {"value": "com.apple.fps"}


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
