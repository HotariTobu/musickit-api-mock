from __future__ import annotations

import json

import pytest
from musickit_api_mock import (
    MusicKitApiMock,
    Request,
    Response,
    StorefrontResponseSuccess,
)
from musickit_api_mock.endpoints.response_language import (
    _language_link,
    _localize_links,
    _normalize_response_language,
    _response_language,
)
from musickit_api_mock.endpoints.storefront_languages import _STOREFRONT_LANGUAGES


@pytest.mark.parametrize(
    ("storefront", "tag", "expected"),
    [
        ("us", "fr", "fr-FR"),
        ("us", "fr-CA", "en-US"),
        ("us", "de", "en-US"),
        ("us", "es", "en-US"),
        ("us", "es-mx", "es-MX"),
        ("us", "EN-us", "en-US"),
        ("us", "en-AU", "en-US"),
        ("us", "ja", "en-US"),
        ("us", "zh", "zh-Hans-CN"),
        ("us", "zh-TW", "zh-Hant-TW"),
        ("us", "pt-br", "pt-BR"),
        ("us", "ko", "ko"),
        ("jp", "en", "en-US"),
        ("jp", "en-AU", "ja"),
        ("jp", "ja", "ja"),
        ("jp", "fr", "ja"),
        ("jp", "zh", "ja"),
        ("ca", "fr", "en-CA"),
        ("ca", "fr-CA", "fr-CA"),
        ("ca", "fr-ca", "fr-CA"),
        ("fr", "ja", "fr-FR"),
        ("gb", "EN-gb", "en-GB"),
        ("cn", "zh-hans-cn", "zh-Hans-CN"),
        ("ch", "de-ch", "de-CH"),
        ("nz", "en-AU", "en-AU"),
        ("in", "hi", "hi"),
        ("dk", "fr", "en-GB"),
        ("xx", "es-mx", "es-mx"),
        (None, "fr", "fr"),
    ],
)
def test_response_language_mapping(
    storefront: str | None, tag: str, expected: str
) -> None:
    assert _normalize_response_language(tag, storefront) == expected
    assert _normalize_response_language(expected, storefront) == expected


@pytest.mark.parametrize("storefront", sorted(_STOREFRONT_LANGUAGES))
def test_documented_profile_matching(storefront: str) -> None:
    profile = _STOREFRONT_LANGUAGES[storefront]
    assert profile
    assert len(profile) == len(set(profile))
    for tag in profile:
        assert _normalize_response_language(tag.swapcase(), storefront) == tag
    assert _normalize_response_language("zz-unlisted", storefront) == profile[0]


def test_unknown_storefront_explicit_profile() -> None:
    assert (
        _normalize_response_language("fr-ca", "xx", languages=["ja", "fr-CA"])
        == "fr-CA"
    )
    assert _normalize_response_language("en", "xx", languages=["ja", "fr-CA"]) == "ja"


@pytest.mark.parametrize(
    ("link", "expected"),
    [
        ("/v1/me/library/songs", "/v1/me/library/songs?l=fr-FR"),
        ("/x?offset=1", "/x?l=fr-FR&offset=1"),
        ("/x?l=fr&offset=1&l=en", "/x?l=fr-FR&offset=1"),
        ("/x?%6c=fr&ids=a%2Cb&x=&x=1#part", "/x?l=fr-FR&ids=a%2Cb&x=&x=1#part"),
        (
            "https://api.music.apple.com/x?offset=2",
            "https://api.music.apple.com/x?l=fr-FR&offset=2",
        ),
    ],
)
def test_link_query_preservation(link: str, expected: str) -> None:
    assert _language_link(link, "fr-FR") == expected


def test_unknown_tag_is_query_encoded() -> None:
    assert (
        _language_link("/x?offset=1", "en&offset=900")
        == "/x?l=en%26offset%3D900&offset=1"
    )


def test_recursive_links_and_nonlink_fields() -> None:
    body = {
        "data": [
            {
                "href": "/resource",
                "relationships": {
                    "tracks": {
                        "href": "/tracks",
                        "next": "/tracks?offset=1",
                        "data": [
                            {
                                "href": "/song",
                                "relationships": {"albums": {"href": "/albums"}},
                            }
                        ],
                    }
                },
                "attributes": {
                    "url": "https://example.com/?l=original",
                    "name": "next",
                },
            }
        ],
        "next": "/resources?offset=1",
        "meta": {"total": 2},
    }
    assert _localize_links(body, "es-MX") == {
        "data": [
            {
                "href": "/resource?l=es-MX",
                "relationships": {
                    "tracks": {
                        "href": "/tracks?l=es-MX",
                        "next": "/tracks?l=es-MX&offset=1",
                        "data": [
                            {
                                "href": "/song?l=es-MX",
                                "relationships": {
                                    "albums": {"href": "/albums?l=es-MX"}
                                },
                            }
                        ],
                    }
                },
                "attributes": {
                    "url": "https://example.com/?l=original",
                    "name": "next",
                },
            }
        ],
        "next": "/resources?l=es-MX&offset=1",
        "meta": {"total": 2},
    }
    assert body["next"] == "/resources?offset=1"


@pytest.mark.parametrize("query", ["", "?l=", "?l=en_US", "?l=invalid-XX"])
def test_nonvalid_tag_does_not_rewrite(mock: MusicKitApiMock, query: str) -> None:
    response = Response(200, {"Content-Type": "application/json"}, b'{"href":"/x"}')
    req = Request(
        "GET", f"https://api.music.apple.com/v1/catalog/us/songs{query}", {}, None
    )
    assert _response_language(mock, req, response) is response


@pytest.mark.parametrize(
    ("status", "content_type", "body"),
    [
        (400, "application/json", b'{"href":"/x"}'),
        (204, "application/json", b""),
        (200, "audio/mpeg", b"binary"),
    ],
)
def test_error_empty_and_binary_untouched(
    mock: MusicKitApiMock, status: int, content_type: str, body: bytes
) -> None:
    response = Response(status, {"Content-Type": content_type}, body)
    req = Request(
        "GET", "https://api.music.apple.com/v1/catalog/us/songs?l=fr", {}, None
    )
    assert _response_language(mock, req, response) is response


def test_storefront_callback_is_not_called_twice(mock: MusicKitApiMock) -> None:
    configured = mock.endpoints.storefront
    assert isinstance(configured, StorefrontResponseSuccess)
    calls = 0

    def storefront() -> StorefrontResponseSuccess:
        nonlocal calls
        calls += 1
        return configured

    mock.endpoints.storefront = storefront
    resp = mock.handle_request(
        Request("GET", "https://api.music.apple.com/v1/me/storefront?l=fr", {}, None)
    )
    assert resp is not None
    assert json.loads(resp.body) == {
        "data": [
            {
                "id": "us",
                "type": "storefronts",
                "href": "/v1/storefronts/us?l=fr-FR",
                "attributes": {
                    "name": "United States",
                    "defaultLanguageTag": "en-US",
                    "supportedLanguageTags": ["en-US"],
                    "explicitContentPolicy": "allowed",
                },
            }
        ]
    }
    assert calls == 1


def test_pagination_keeps_normalized_language(mock: MusicKitApiMock) -> None:
    from tests._expected import SONG_ATTRIBUTES

    assert isinstance(mock.data.albums, dict)
    assert isinstance(mock.data.songs, dict)
    mock.data.albums["a1"].track_ids = ["1", "2"]
    mock.data.songs["2"] = mock.data.songs["1"]
    first = mock.handle_request(
        Request(
            "GET",
            "https://api.music.apple.com/v1/catalog/us/albums/a1/tracks?l=fr&limit=1",
            {},
            None,
        )
    )
    assert first is not None
    assert json.loads(first.body) == {
        "data": [
            {
                "id": "1",
                "type": "songs",
                "href": "/v1/catalog/us/songs/1?l=fr-FR",
                "attributes": SONG_ATTRIBUTES,
            }
        ],
        "next": "/v1/catalog/us/albums/a1/tracks?l=fr-FR&offset=1",
    }
    second = mock.handle_request(
        Request(
            "GET",
            "https://api.music.apple.com/v1/catalog/us/albums/a1/tracks?l=fr-FR&offset=1",
            {},
            None,
        )
    )
    assert second is not None
    assert json.loads(second.body) == {
        "data": [
            {
                "id": "2",
                "type": "songs",
                "href": "/v1/catalog/us/songs/2?l=fr-FR",
                "attributes": {
                    **SONG_ATTRIBUTES,
                    "playParams": {"id": "2", "kind": "song"},
                    "previews": [
                        {"url": "https://audio-ssl.itunes.apple.com/preview/2.m4a"}
                    ],
                },
            }
        ],
    }


def test_repeated_request_language_uses_last_value(mock: MusicKitApiMock) -> None:
    from tests._expected import GENRE

    response = mock.handle_request(
        Request(
            "GET",
            "https://api.music.apple.com/v1/catalog/us/genres?ids=20&l=en-US&l=fr",
            {},
            None,
        )
    )
    assert response is not None
    assert json.loads(response.body) == {
        "data": [{**GENRE, "href": "/v1/catalog/us/genres/20?l=fr-FR"}]
    }


def test_library_with_unset_storefront_preserves_tag(mock: MusicKitApiMock) -> None:
    from tests._expected import LIBRARY_MUSIC_VIDEO

    mock.endpoints.storefront = None
    response = mock.handle_request(
        Request(
            "GET",
            "https://api.music.apple.com/v1/me/library/music-videos/i.mv1?l=es-mx",
            {},
            None,
        )
    )
    assert response is not None
    assert json.loads(response.body) == {
        "data": [
            {**LIBRARY_MUSIC_VIDEO, "href": "/v1/me/library/music-videos/i.mv1?l=es-mx"}
        ]
    }


def test_library_catalog_and_links_share_storefront_snapshot(
    mock: MusicKitApiMock,
) -> None:
    from dataclasses import replace

    from tests._expected import LIBRARY_SONG, SONG

    configured = mock.endpoints.storefront
    assert isinstance(configured, StorefrontResponseSuccess)
    calls = 0

    def storefront() -> StorefrontResponseSuccess:
        nonlocal calls
        calls += 1
        return (
            configured
            if calls == 1
            else StorefrontResponseSuccess(
                storefront=replace(
                    configured.storefront, id="jp", default_language_tag="ja"
                )
            )
        )

    mock.endpoints.storefront = storefront
    request = Request(
        "GET",
        "https://api.music.apple.com/v1/me/library/songs/i.s1?include=catalog&l=fr",
        {},
        None,
    )
    first = mock.handle_request(request)
    assert first is not None
    assert calls == 1
    assert json.loads(first.body) == {
        "data": [
            {
                **LIBRARY_SONG,
                "href": "/v1/me/library/songs/i.s1?l=fr-FR",
                "relationships": {
                    "catalog": {
                        "href": "/v1/me/library/songs/i.s1/catalog?l=fr-FR",
                        "data": [{**SONG, "href": "/v1/catalog/us/songs/1?l=fr-FR"}],
                    }
                },
            }
        ]
    }
    second = mock.handle_request(request)
    assert second is not None
    assert calls == 2
    assert json.loads(second.body) == {
        "data": [
            {
                **LIBRARY_SONG,
                "href": "/v1/me/library/songs/i.s1?l=ja",
                "relationships": {
                    "catalog": {
                        "href": "/v1/me/library/songs/i.s1/catalog?l=ja",
                        "data": [{**SONG, "href": "/v1/catalog/jp/songs/1?l=ja"}],
                    }
                },
            }
        ]
    }


def test_storefront_scope_restores_after_nested_scope_and_exception(
    mock: MusicKitApiMock,
) -> None:
    configured = mock.endpoints.storefront
    assert isinstance(configured, StorefrontResponseSuccess)
    calls = 0

    def storefront() -> StorefrontResponseSuccess:
        nonlocal calls
        calls += 1
        return configured

    mock.endpoints.storefront = storefront
    resolver = mock._endpoint_resolver

    def interrupted_request() -> None:
        with resolver.request_scope():
            assert resolver.storefront() is configured
            assert calls == 2
            raise RuntimeError("interrupted nested request")

    with resolver.request_scope():
        assert resolver.storefront() is configured
        with pytest.raises(RuntimeError):
            interrupted_request()
        assert resolver.storefront() is configured
        assert calls == 2
    with resolver.request_scope():
        assert resolver.storefront() is configured
        assert calls == 3
