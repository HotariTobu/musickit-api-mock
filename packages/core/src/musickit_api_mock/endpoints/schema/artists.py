"""Artist resource JSON shape builder."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.endpoints.schema.builders import (
    _artwork,
    _strip_none,
)

if TYPE_CHECKING:
    from musickit_api_mock.data.artist import Artist
    from musickit_api_mock.json_value import _JSONValue


def _artist_resource(
    sf: str,
    artist_id: str,
    artist: Artist,
    *,
    relationships: dict[str, _JSONValue] | None = None,
) -> dict[str, _JSONValue]:
    attrs: dict[str, _JSONValue] = _strip_none(
        {
            "name": artist.name,
            "artwork": _artwork(artist.artwork) if artist.artwork is not None else None,
            "genreNames": artist.genre_names,
            "url": artist.url,
        }
    )
    out: dict[str, _JSONValue] = {
        "id": artist_id,
        "type": "artists",
        "href": f"/v1/catalog/{sf}/artists/{artist_id}",
        "attributes": attrs,
    }
    if relationships:
        out["relationships"] = relationships
    return out
