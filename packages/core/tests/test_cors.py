from musickit_api_mock import (
    MusicKitApiMock,
    Request,
    WidevineCertResponseSuccess,
)


def test_options_preflight_api_host() -> None:
    m = MusicKitApiMock()
    req = Request(
        method="OPTIONS",
        url="https://api.music.apple.com/v1/catalog/us/songs",
        headers={"Origin": "http://localhost:3000"},
        body=None,
    )
    resp = m.handle_request(req)
    assert resp is not None
    assert resp.status == 204
    assert resp.headers["Access-Control-Allow-Origin"] == "*"
    assert "Access-Control-Allow-Credentials" not in resp.headers


def test_options_preflight_play_host_credentials() -> None:
    m = MusicKitApiMock()
    req = Request(
        method="OPTIONS",
        url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/webPlayback",
        headers={"Origin": "http://localhost:3000"},
        body=None,
    )
    resp = m.handle_request(req)
    assert resp is not None
    assert resp.status == 204
    assert resp.headers["Access-Control-Allow-Origin"] == "http://localhost:3000"
    assert resp.headers["Access-Control-Allow-Credentials"] == "true"


def test_normal_get_response_carries_cors_origin(
    mock: MusicKitApiMock,
) -> None:
    """Non-preflight responses also carry ``Access-Control-Allow-Origin``."""
    resp = mock.handle_request(
        Request(
            method="GET",
            url="https://api.music.apple.com/v1/me/storefront",
            headers={"Origin": "http://localhost:3000"},
            body=None,
        )
    )
    assert resp is not None
    assert resp.status == 200
    assert resp.headers.get("Access-Control-Allow-Origin") == "*"
    assert "Access-Control-Allow-Credentials" not in resp.headers


def test_normal_get_play_host_response_carries_credential_headers() -> None:
    """``play.itunes.apple.com`` responses echo Origin + Allow-Credentials."""
    m = MusicKitApiMock()
    m.endpoints.widevine_cert = WidevineCertResponseSuccess(cert=b"")
    resp = m.handle_request(
        Request(
            method="GET",
            url="https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/widevineCert",
            headers={"Origin": "http://localhost:3000"},
            body=None,
        )
    )
    assert resp is not None
    assert resp.status == 200
    assert resp.headers.get("Access-Control-Allow-Origin") == "http://localhost:3000"
    assert resp.headers.get("Access-Control-Allow-Credentials") == "true"
