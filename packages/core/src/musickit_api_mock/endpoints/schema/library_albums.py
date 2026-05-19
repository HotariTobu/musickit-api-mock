"""Library album resource JSON shape builder."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.endpoints.schema.builders import (
    _artwork,
    _strip_none,
)
from musickit_api_mock.endpoints.schema.play_params import _play_params_library_album

if TYPE_CHECKING:
    from musickit_api_mock.data.library_album import LibraryAlbum
    from musickit_api_mock.json_value import _JSONValue


def _library_album_resource(
    library_album_id: str,
    library_album: LibraryAlbum,
    *,
    relationships: dict[str, _JSONValue] | None = None,
) -> dict[str, _JSONValue]:
    attrs: dict[str, _JSONValue] = _strip_none(
        {
            "name": library_album.name,
            "artistName": library_album.artist_name,
            "artwork": _artwork(library_album.artwork),
            "dateAdded": library_album.date_added,
            "genreNames": library_album.genre_names,
            "playParams": _play_params_library_album(library_album_id),
            "releaseDate": library_album.release_date,
            "trackCount": library_album.track_count,
        }
    )
    out: dict[str, _JSONValue] = {
        "id": library_album_id,
        "type": "library-albums",
        "href": f"/v1/me/library/albums/{library_album_id}",
        "attributes": attrs,
    }
    if relationships:
        out["relationships"] = relationships
    return out
