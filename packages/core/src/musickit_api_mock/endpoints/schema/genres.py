"""Genre resource JSON shape builder."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.endpoints.schema.builders import _strip_none

if TYPE_CHECKING:
    from musickit_api_mock.data.genre import Genre
    from musickit_api_mock.json_value import _JSONValue


def _genre_resource(sf: str, genre_id: str, genre: Genre) -> dict[str, _JSONValue]:
    return {
        "id": genre_id,
        "type": "genres",
        "href": f"/v1/catalog/{sf}/genres/{genre_id}",
        "attributes": _strip_none(
            {
                "name": genre.name,
                "parentId": genre.parent_id,
                "parentName": genre.parent_name,
                "url": genre.url,
            }
        ),
    }
