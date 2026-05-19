"""JS scenarios + assertions for the boundary-surface intercept tests.

Each scenario is a JS string passed to ``page.evaluate`` and an assertion
function operating on the result. Both are shared between
``test_intercept_sync.py`` and ``test_intercept_async.py``.
"""

from __future__ import annotations

import base64
import json
from typing import TypedDict


class _FetchTextResult(TypedDict):
    status: int
    body: str


class _AuthorizeResponseBody(TypedDict, total=False):
    kind: str
    user_token: str


class _FetchAuthorizeResult(TypedDict):
    status: int
    body: _AuthorizeResponseBody


class _LicenseFetchResult(TypedDict, total=False):
    status: int
    license: str


class _PostMessageData(TypedDict, total=False):
    method: str
    params: list[str]


class _FetchOutcomeResult(TypedDict, total=False):
    kind: str
    status: int


FETCH_STOREFRONT = """async () => {
    const r = await fetch('https://api.music.apple.com/v1/me/storefront');
    return { status: r.status, body: await r.text() };
}"""


def assert_storefront_response(result: _FetchTextResult) -> None:
    assert result["status"] == 200
    parsed = json.loads(result["body"])
    assert parsed["data"][0]["id"] == "us"
    assert parsed["data"][0]["attributes"]["name"] == "United States"


FETCH_GENRE_SINGULAR = """async () => {
    const r = await fetch('https://api.music.apple.com/v1/catalog/us/genres/20');
    return { status: r.status, body: await r.text() };
}"""


def assert_genre_singular_response(result: _FetchTextResult) -> None:
    assert result["status"] == 200
    parsed = json.loads(result["body"])
    assert parsed["data"][0]["type"] == "genres"
    assert parsed["data"][0]["id"] == "20"
    assert parsed["data"][0]["attributes"]["name"] == "Pop"


FETCH_RECOMMENDATION_SINGULAR = """async () => {
    const r = await fetch('https://api.music.apple.com/v1/me/recommendations/rec1');
    return { status: r.status, body: await r.text() };
}"""


def assert_recommendation_singular_response(result: _FetchTextResult) -> None:
    assert result["status"] == 200
    parsed = json.loads(result["body"])
    assert parsed["data"][0]["type"] == "personal-recommendation"
    assert parsed["data"][0]["id"] == "rec1"
    rels = parsed["data"][0]["relationships"]
    assert rels["contents"]["data"][0]["type"] == "playlists"


FETCH_SONG_LIBRARY = """async () => {
    const r = await fetch('https://api.music.apple.com/v1/catalog/us/songs/1/library');
    return { status: r.status, body: await r.text() };
}"""


def assert_song_library_response(result: _FetchTextResult) -> None:
    assert result["status"] == 200
    parsed = json.loads(result["body"])
    assert parsed["data"][0]["type"] == "library-songs"
    assert parsed["data"][0]["id"] == "i.s1"


FETCH_ARTIST_STATION = """async () => {
    const r = await fetch('https://api.music.apple.com/v1/catalog/us/artists/ar1/station');
    return { status: r.status, body: await r.text() };
}"""


def assert_artist_station_response(result: _FetchTextResult) -> None:
    assert result["status"] == 200
    parsed = json.loads(result["body"])
    assert parsed["data"][0]["type"] == "stations"
    assert parsed["data"][0]["id"] == "ra.978194965"


FETCH_MUSIC_VIDEO_SONGS = """async () => {
    const r = await fetch('https://api.music.apple.com/v1/catalog/us/music-videos/mv1/songs');
    return { status: r.status, body: await r.text() };
}"""


def assert_music_video_songs_response(result: _FetchTextResult) -> None:
    assert result["status"] == 200
    parsed = json.loads(result["body"])
    assert [x["id"] for x in parsed["data"]] == ["1"]


FETCH_ALBUM_RECORD_LABELS = """async () => {
    const r = await fetch('https://api.music.apple.com/v1/catalog/us/albums/a1/record-labels');
    return { status: r.status, body: await r.text() };
}"""


def assert_album_record_labels_response(result: _FetchTextResult) -> None:
    assert result["status"] == 200
    parsed = json.loads(result["body"])
    assert [x["id"] for x in parsed["data"]] == ["rl1"]
    assert parsed["data"][0]["type"] == "record-labels"


FETCH_APPLE_CURATOR_PLAYLISTS = """async () => {
    const r = await fetch('https://api.music.apple.com/v1/catalog/us/apple-curators/cu1/playlists');
    return { status: r.status, body: await r.text() };
}"""


def assert_apple_curator_playlists_response(result: _FetchTextResult) -> None:
    assert result["status"] == 200
    parsed = json.loads(result["body"])
    assert [x["id"] for x in parsed["data"]] == ["pl1"]
    assert parsed["data"][0]["type"] == "playlists"


FETCH_LIBRARY_ARTIST_ALBUMS = """async () => {
    const r = await fetch('https://api.music.apple.com/v1/me/library/artists/r.ar1/albums');
    return { status: r.status, body: await r.text() };
}"""


def assert_library_artist_albums_response(result: _FetchTextResult) -> None:
    assert result["status"] == 200
    parsed = json.loads(result["body"])
    assert [x["id"] for x in parsed["data"]] == ["l.a1"]
    assert parsed["data"][0]["type"] == "library-albums"


FETCH_STATION_RADIO_SHOW = """async () => {
    const r = await fetch('https://api.music.apple.com/v1/catalog/us/stations/ra.978194965/radio-show');
    return { status: r.status, body: await r.text() };
}"""


def assert_station_radio_show_response(result: _FetchTextResult) -> None:
    assert result["status"] == 200
    parsed = json.loads(result["body"])
    assert parsed["data"][0]["type"] == "apple-curators"
    assert parsed["data"][0]["id"] == "cu1"


UNRELATED_APPLE_URL = "https://idmsa.apple.com/should-not-exist-123"

FETCH_UNRELATED_APPLE_URL = f"""async () => {{
    try {{
        const r = await fetch('{UNRELATED_APPLE_URL}');
        return {{ status: r.status }};
    }} catch (e) {{
        return {{ error: String(e) }};
    }}
}}"""


FETCH_LICENSE = """async () => {
    const r = await fetch('https://play.itunes.apple.com/WebObjects/MZPlay.woa/wa/acquireWebPlaybackLicense', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 'key-system': 'com.widevine.alpha', adamId: '1', isLibrary: false }),
    });
    return await r.json();
}"""


def assert_license_failure(result: _LicenseFetchResult, expected_status: int) -> None:
    assert result["status"] == expected_status


def assert_license_success_b64(result: _LicenseFetchResult, expected: bytes) -> None:
    assert base64.b64decode(result["license"]) == expected


EVAL_EME_FLAVOR = """() => window.__musickitApiMock.browser.eme_flavor"""


FETCH_AUTHORIZE_RESPONSE = """async () => {
    const r = await fetch('https://musickit-api-mock.invalid/browser/authorize_response');
    return { status: r.status, body: await r.json() };
}"""


def assert_eme_flavor(result: str, expected_flavor: str) -> None:
    assert result == expected_flavor


def assert_authorize_response_success(
    result: _FetchAuthorizeResult, expected_user_token: str
) -> None:
    assert result["status"] == 200
    assert result["body"]["kind"] == "AuthorizeSuccess"
    assert result["body"]["user_token"] == expected_user_token


REQUEST_WIDEVINE_ACCESS = """async () => {
    const access = await navigator.requestMediaKeySystemAccess('com.widevine.alpha', [{
        initDataTypes: ['cenc'],
        videoCapabilities: [{ contentType: 'video/mp4;codecs="avc1.42E01E"' }],
        audioCapabilities: [{ contentType: 'audio/mp4;codecs="mp4a.40.2"' }],
    }]);
    return access.keySystem;
}"""


def assert_widevine_granted(result: str) -> None:
    assert result == "com.widevine.alpha"


REQUEST_PLAYREADY_ACCESS = """async () => {
    try {
        await navigator.requestMediaKeySystemAccess('com.microsoft.playready', [{
            initDataTypes: ['cenc'],
            videoCapabilities: [{ contentType: 'video/mp4;codecs="avc1.42E01E"' }],
        }]);
        return null;
    } catch (e) {
        return e.name;
    }
}"""


def assert_not_supported_error(result: str | None) -> None:
    assert result == "NotSupportedError"


OPEN_OAUTH_POPUP_AND_RECEIVE = """async () => {
    const got = new Promise((resolve) => {
        window.addEventListener('message', (ev) => {
            if (ev.origin === 'https://authorize.music.apple.com') {
                resolve(ev.data);
            }
        });
    });
    window.open('https://authorize.music.apple.com/woa?x=1', 'oauth', '');
    return await got;
}"""


def assert_authorize_message(
    result: _PostMessageData, expected_user_token: str, expected_cid: str
) -> None:
    assert result["method"] == "authorize"
    assert result["params"][0] == expected_user_token
    assert result["params"][2] == expected_cid


# Reports whether the fetch resolved into a Response or rejected with an
# error. Used to verify the adapter's handler-error path: when the mock
# raises (e.g. a setter is unset), the adapter must abort the route so the
# browser sees a network failure rather than a hung pending request or a
# stray HTTP status that collides with mock-produced responses.
FETCH_STOREFRONT_AND_REPORT_OUTCOME = """async () => {
    try {
        const r = await fetch('https://api.music.apple.com/v1/me/storefront');
        return { kind: 'response', status: r.status };
    } catch (_e) {
        return { kind: 'error' };
    }
}"""


def assert_fetch_aborted(result: _FetchOutcomeResult) -> None:
    """Assert the fetch was aborted (rejected) rather than returning a Response.

    The browser-side error name is intentionally not asserted — different
    browsers wrap aborted fetches in different ``Error`` subclasses, and the
    contract under test is only that no Response was produced.
    """
    assert result["kind"] == "error", (
        f"expected fetch to reject; got Response with status {result.get('status')!r}"
    )
