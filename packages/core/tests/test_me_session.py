from __future__ import annotations

import json
from typing import TYPE_CHECKING

from musickit_api_mock import (
    AccountResponseFailure,
    AccountResponseSessionExpired,
    MusicKitApiMock,
    RenewTokenResponseUnauthorized,
    Request,
    StorefrontResponseFailure,
    StorefrontResponseSessionExpired,
)

if TYPE_CHECKING:
    from tests._apple_response import _AppleResponse


def _get(mock: MusicKitApiMock, url: str) -> tuple[int, _AppleResponse]:
    resp = mock.handle_request(Request(method="GET", url=url, headers={}, body=None))
    assert resp is not None
    return resp.status, json.loads(resp.body)


def test_a01_storefront(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/me/storefront")
    assert status == 200
    assert body["data"][0]["id"] == "us"
    assert body["data"][0]["attributes"]["name"] == "United States"


def test_p01_account(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/account?meta=subscription"
    )
    assert status == 200
    assert body["meta"]["subscription"] == {"active": True, "storefront": "us"}
    assert body["data"][0]["attributes"]["restrictions"] == {}


def test_a01_storefront_session_expired(mock: MusicKitApiMock) -> None:
    mock.endpoints.storefront = StorefrontResponseSessionExpired()
    status, body = _get(mock, "https://api.music.apple.com/v1/me/storefront")
    assert status == 403
    assert body["errors"][0]["code"] == "40300"


def test_a01_storefront_failure(mock: MusicKitApiMock) -> None:
    mock.endpoints.storefront = StorefrontResponseFailure()
    status, _body = _get(mock, "https://api.music.apple.com/v1/me/storefront")
    assert status == 500


def test_p01_account_session_expired(mock: MusicKitApiMock) -> None:
    mock.endpoints.account = AccountResponseSessionExpired()
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/account?meta=subscription"
    )
    assert status == 403
    assert body["errors"][0]["status"] == "403"


def test_p01_account_failure(mock: MusicKitApiMock) -> None:
    mock.endpoints.account = AccountResponseFailure()
    status, _body = _get(
        mock, "https://api.music.apple.com/v1/me/account?meta=subscription"
    )
    assert status == 500


def test_r01_renew_token_unauthorized(mock: MusicKitApiMock) -> None:
    mock.endpoints.renew_music_token = RenewTokenResponseUnauthorized()
    resp = mock.handle_request(
        Request(
            method="POST",
            url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/renewMusicToken",
            headers={},
            body=b"{}",
        )
    )
    assert resp is not None
    assert resp.status == 401
    body = json.loads(resp.body)
    assert "error_description" in body
