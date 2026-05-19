import json

from musickit_api_mock import (
    LogoutResponseSuccess,
    MusicKitApiMock,
    RenewTokenResponseSuccess,
    RenewTokenResponseUnauthorized,
    Request,
)


def test_a02_webplayer_logout_success(mock: MusicKitApiMock) -> None:
    mock.endpoints.webplayer_logout = LogoutResponseSuccess()
    resp = mock.handle_request(
        Request(
            method="POST",
            url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/webPlayerLogout",
            headers={},
            body=b"",
        )
    )
    assert resp is not None
    assert resp.status == 200
    assert json.loads(resp.body) == {"status": 0}


def test_r01_renew_token_success(mock: MusicKitApiMock) -> None:
    mock.endpoints.renew_music_token = RenewTokenResponseSuccess(
        music_token="new-token"
    )
    resp = mock.handle_request(
        Request(
            method="POST",
            url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/renewMusicToken",
            headers={},
            body=b"",
        )
    )
    assert resp is not None
    assert resp.status == 200
    assert json.loads(resp.body) == {"music-token": "new-token"}


def test_r01_renew_token_unauthorized(mock: MusicKitApiMock) -> None:
    mock.endpoints.renew_music_token = RenewTokenResponseUnauthorized()
    resp = mock.handle_request(
        Request(
            method="POST",
            url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/renewMusicToken",
            headers={},
            body=b"",
        )
    )
    assert resp is not None
    assert resp.status == 401
