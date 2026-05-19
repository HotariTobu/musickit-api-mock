"""Library artist resource JSON shape builder."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from musickit_api_mock.data.library_artist import LibraryArtist
    from musickit_api_mock.json_value import _JSONValue


def _library_artist_resource(
    library_artist_id: str,
    library_artist: LibraryArtist,
    *,
    relationships: dict[str, _JSONValue] | None = None,
) -> dict[str, _JSONValue]:
    out: dict[str, _JSONValue] = {
        "id": library_artist_id,
        "type": "library-artists",
        "href": f"/v1/me/library/artists/{library_artist_id}",
        "attributes": {"name": library_artist.name},
    }
    if relationships is not None:
        out["relationships"] = relationships
    return out
