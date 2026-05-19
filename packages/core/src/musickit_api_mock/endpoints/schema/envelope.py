"""Error and pagination envelope builders shared across endpoints."""

from __future__ import annotations

import http
import uuid
from typing import TYPE_CHECKING

from musickit_api_mock.endpoints.schema.builders import _strip_none

if TYPE_CHECKING:
    from collections.abc import Iterable

    from musickit_api_mock.endpoints.responses.continuous_stations import (
        ErrorEnvelope,
    )
    from musickit_api_mock.json_value import _JSONValue


def _batch_envelope(
    resources: Iterable[dict[str, _JSONValue]],
) -> dict[str, _JSONValue]:
    return {"data": list(resources)}


_LIBRARY_SONGS_DEAD_PATH_ERROR: dict[str, str] = {
    "title": "Invalid Path Value",
    "detail": "Unknown library resource type 'library-songs'",
    "status": "400",
    "code": "40008",
}


def _library_songs_dead_path_400_envelope() -> dict[str, _JSONValue]:
    """400 envelope for the ``library-songs`` dead-path batch case."""
    return {
        "errors": [{"id": uuid.uuid4().hex.upper(), **_LIBRARY_SONGS_DEAD_PATH_ERROR}]
    }


def _empty_ids_400_envelope() -> dict[str, _JSONValue]:
    return {
        "errors": [
            {
                "id": uuid.uuid4().hex.upper(),
                "title": "Invalid Parameter Value",
                "detail": "No id(s) supplied in the 'ids' query parameter",
                "status": "400",
                "code": "40005",
                "source": {"parameter": "ids"},
            }
        ]
    }


def _missing_ids_param_400_envelope() -> dict[str, _JSONValue]:
    return {
        "errors": [
            {
                "id": uuid.uuid4().hex.upper(),
                "title": "Missing Parameter",
                "detail": "No id(s) supplied on the request",
                "status": "400",
                "code": "40003",
                "source": {"parameter": "ids"},
            }
        ]
    }


def _resource_not_found_404_envelope() -> dict[str, _JSONValue]:
    return {
        "errors": [
            {
                "id": uuid.uuid4().hex.upper(),
                "title": "Resource Not Found",
                "detail": "Resource with requested id was not found",
                "status": "404",
                "code": "40400",
            }
        ]
    }


def _session_expired_403_envelope() -> dict[str, _JSONValue]:
    return {
        "errors": [
            {
                "id": uuid.uuid4().hex.upper(),
                "title": "Forbidden",
                "detail": "Invalid authentication",
                "status": "403",
                "code": "40300",
            }
        ]
    }


def _session_expired_renew_401_body() -> dict[str, _JSONValue]:
    return {
        "error_description": (
            "The token does not exist, it may have been revoked by the user."
        ),
        "error": "No token found",
    }


def _generic_error_envelope(status: int) -> dict[str, _JSONValue]:
    """Errors envelope for a generic non-2xx HTTP status."""
    try:
        title = http.HTTPStatus(status).phrase
    except ValueError:
        title = "Error"
    return {
        "errors": [
            {
                "id": uuid.uuid4().hex.upper(),
                "title": title,
                "status": str(status),
            }
        ]
    }


def _play_assets_403_envelope(
    error_code: str, title: str, detail: str
) -> dict[str, _JSONValue]:
    """403 errors envelope for the play-assets endpoints."""
    return {
        "errors": [
            {
                "id": uuid.uuid4().hex.upper(),
                "code": error_code,
                "title": title,
                "detail": detail,
                "status": "403",
            }
        ]
    }


def _continuous_stations_errors_envelope(
    errors: list[ErrorEnvelope],
) -> dict[str, _JSONValue]:
    """Errors envelope for the continuous-stations CONTENT_UNSUPPORTED case."""
    out: list[dict[str, _JSONValue]] = [
        _strip_none(
            {
                "id": uuid.uuid4().hex.upper(),
                "code": e.code,
                "title": e.title,
                "status": e.status,
                "detail": e.detail,
                "source": e.source,
            }
        )
        for e in errors
    ]
    return {"errors": out}


def _continuous_stations_no_station_envelope() -> dict[str, _JSONValue]:
    """Empty results envelope (``results.station`` missing) → CONTENT_UNAVAILABLE."""
    return {"results": {}}


def _parameter_invalid_envelope(parameter: str, detail: str) -> dict[str, _JSONValue]:
    """400 envelope for ``Invalid Parameter Value`` errors.

    ``parameter`` becomes ``source.parameter`` (e.g. ``"limit"`` or
    ``"limit[tracks]"``). ``detail`` carries the case-specific message
    (overflow / underflow / non-integer wording etc.).
    """
    return {
        "errors": [
            {
                "id": uuid.uuid4().hex.upper(),
                "title": "Invalid Parameter Value",
                "detail": detail,
                "status": "400",
                "code": "40005",
                "source": {"parameter": parameter},
            }
        ]
    }


def _limit_exceeded_envelope(max_limit: int, requested: int) -> dict[str, _JSONValue]:
    """400 envelope returned when ``?limit=N`` exceeds the endpoint cap."""
    return _parameter_invalid_envelope(
        "limit",
        f"Value must be an integer less than or equal to {max_limit}, "
        f"but was: {requested}",
    )


def _invalid_language_tag_envelope(tag: str) -> dict[str, _JSONValue]:
    """400 envelope returned when ``?l=`` is not a valid BCP 47 language tag."""
    return {
        "errors": [
            {
                "id": uuid.uuid4().hex.upper(),
                "title": "Invalid Parameter Value",
                "detail": f"Invalid language tag '{tag}'",
                "status": "400",
                "code": "40005",
                "source": {"parameter": "l"},
            }
        ]
    }
