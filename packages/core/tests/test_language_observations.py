from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import TypedDict, cast
from urllib.parse import urlencode

import pytest
from musickit_api_mock import Genre, MusicKitApiMock, Request
from musickit_api_mock.endpoints.storefront_languages import _STOREFRONT_LANGUAGES

from tests._expected import ERROR_ID


class _StorefrontMetadata(TypedDict):
    id: str
    default_language_tag: str
    supported_language_tags: list[str]
    metadata_source: str


class _Observation(TypedDict):
    storefront: str
    requested_language: str | None
    status: int
    emitted_languages: list[str]
    hrefs: list[str]
    observed_at: str
    error_code: str | None


class _Probe(TypedDict):
    schema_version: int
    host: str
    resource: str
    started_at: str
    completed_at: str
    storefronts: list[_StorefrontMetadata]
    observations: list[_Observation]


_PROBE = cast(
    "_Probe",
    json.loads(
        (
            Path(__file__).parent / "fixtures" / "apple_language_observations.json"
        ).read_text(encoding="utf-8")
    ),
)


@pytest.fixture(scope="module")
def language_mock() -> MusicKitApiMock:
    mock = MusicKitApiMock()
    mock.data.genres = {"34": Genre(name="Music", url="https://example.com/music")}
    return mock


def test_observation_coverage_and_controls() -> None:
    assert _PROBE["schema_version"] == 1
    assert _PROBE["host"] == "api.music.apple.com"
    assert _PROBE["resource"] == "genres/34"
    observations = _PROBE["observations"]
    assert len(_PROBE["storefronts"]) == 172
    assert Counter(row["status"] for row in observations) == {
        200: 3600,
        400: 172,
        404: 23,
    }
    pairs = {(row["storefront"], row["requested_language"]) for row in observations}
    assert len(pairs) == len(observations) == 3795
    assert {row["storefront"] for row in observations if row["status"] == 404} == {"ru"}
    assert "ru" not in _STOREFRONT_LANGUAGES
    assert set(_STOREFRONT_LANGUAGES) == {
        row["storefront"] for row in observations if row["status"] == 200
    }
    assert {
        row["requested_language"] for row in observations if row["status"] == 400
    } == {"invalid-control"}
    for row in observations:
        assert _PROBE["started_at"] <= row["observed_at"] <= _PROBE["completed_at"]
        if row["requested_language"] in (None, ""):
            assert row["emitted_languages"] == []
    for storefront in _PROBE["storefronts"]:
        tags = storefront["supported_language_tags"]
        expected = {
            None,
            "",
            "invalid-control",
            "ja",
            "ja-JP",
            "en",
            "en-US",
            "en-GB",
            "en-AU",
            "fr",
            "fr-CA",
            "es",
            "es-MX",
            "de",
            "zh",
            "zh-TW",
            "pt-BR",
            "ko",
            *tags,
            *(tag.lower() for tag in tags),
            *(tag.upper() for tag in tags),
            *(tag.split("-", 1)[0] for tag in tags),
        }
        assert {(storefront["id"], tag) for tag in expected} <= pairs


@pytest.mark.parametrize(
    "observation",
    [row for row in _PROBE["observations"] if row["status"] == 200],
    ids=lambda row: f"{row['storefront']}-{row['requested_language']!r}",
)
def test_successful_observed_response_link(
    observation: _Observation, language_mock: MusicKitApiMock
) -> None:
    tag = observation["requested_language"]
    query = "" if tag is None else "?" + urlencode({"l": tag})
    response = language_mock.handle_request(
        Request(
            "GET",
            f"https://api.music.apple.com/v1/catalog/{observation['storefront']}/genres/34{query}",
            {},
            None,
        )
    )
    assert response is not None
    assert response.status == 200
    assert len(observation["hrefs"]) == 1
    assert json.loads(response.body) == {
        "data": [
            {
                "id": "34",
                "type": "genres",
                "href": observation["hrefs"][0],
                "attributes": {"name": "Music", "url": "https://example.com/music"},
            }
        ]
    }


@pytest.mark.parametrize("storefront", [row["id"] for row in _PROBE["storefronts"]])
def test_observed_invalid_control(
    storefront: str, language_mock: MusicKitApiMock
) -> None:
    response = language_mock.handle_request(
        Request(
            "GET",
            f"https://api.music.apple.com/v1/catalog/{storefront}/genres/34?l=invalid-control",
            {},
            None,
        )
    )
    assert response is not None
    assert response.status == 400
    assert json.loads(response.body) == {
        "errors": [
            {
                "id": ERROR_ID,
                "title": "Invalid Parameter Value",
                "detail": "Invalid language tag 'invalid-control'",
                "status": "400",
                "code": "40005",
                "source": {"parameter": "l"},
            }
        ]
    }
