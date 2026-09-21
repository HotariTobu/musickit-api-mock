from __future__ import annotations

import json

from musickit_api_mock import (
    AccountResponseFailure,
    AccountResponseSessionExpired,
    MusicKitApiMock,
    RenewTokenResponseUnauthorized,
    Request,
    StorefrontResponseFailure,
    StorefrontResponseSessionExpired,
)

from tests._expected import ACCOUNT, ERROR_ID, STOREFRONT

_SESSION_EXPIRED_BODY = {
    "errors": [
        {
            "id": ERROR_ID,
            "title": "Forbidden",
            "detail": "Invalid authentication",
            "status": "403",
            "code": "40300",
        }
    ]
}

_FAILURE_BODY = {
    "errors": [
        {
            "id": ERROR_ID,
            "title": "Internal Server Error",
            "status": "500",
        }
    ]
}


def _get(mock: MusicKitApiMock, url: str) -> tuple[int, object]:
    resp = mock.handle_request(Request(method="GET", url=url, headers={}, body=None))
    assert resp is not None
    return resp.status, json.loads(resp.body)


def test_a01_storefront(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/me/storefront")
    assert status == 200
    assert body == {"data": [STOREFRONT]}


def test_p01_account(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/account?meta=subscription"
    )
    assert status == 200
    assert body == {
        "data": [ACCOUNT],
        "meta": {"subscription": {"active": True, "storefront": "us"}},
    }


def test_a01_storefront_session_expired(mock: MusicKitApiMock) -> None:
    mock.endpoints.storefront = StorefrontResponseSessionExpired()
    status, body = _get(mock, "https://api.music.apple.com/v1/me/storefront")
    assert status == 403
    assert body == _SESSION_EXPIRED_BODY


def test_a01_storefront_failure(mock: MusicKitApiMock) -> None:
    mock.endpoints.storefront = StorefrontResponseFailure()
    status, body = _get(mock, "https://api.music.apple.com/v1/me/storefront")
    assert status == 500
    assert body == _FAILURE_BODY


def test_p01_account_session_expired(mock: MusicKitApiMock) -> None:
    mock.endpoints.account = AccountResponseSessionExpired()
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/account?meta=subscription"
    )
    assert status == 403
    assert body == _SESSION_EXPIRED_BODY


def test_p01_account_failure(mock: MusicKitApiMock) -> None:
    mock.endpoints.account = AccountResponseFailure()
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/account?meta=subscription"
    )
    assert status == 500
    assert body == _FAILURE_BODY


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
    assert json.loads(resp.body) == {
        "error": "No token found",
        "error_description": (
            "The token does not exist, it may have been revoked by the user."
        ),
    }
