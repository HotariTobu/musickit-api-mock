"""Library playlist resource JSON shape builder."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.endpoints.schema.builders import (
    _artwork,
    _strip_none,
)
from musickit_api_mock.endpoints.schema.play_params import _play_params_library_playlist

if TYPE_CHECKING:
    from musickit_api_mock.data.library_playlist import LibraryPlaylist
    from musickit_api_mock.json_value import _JSONValue


def _library_playlist_resource(
    library_playlist_id: str,
    library_playlist: LibraryPlaylist,
    *,
    relationships: dict[str, _JSONValue] | None = None,
) -> dict[str, _JSONValue]:
    attrs: dict[str, _JSONValue] = _strip_none(
        {
            "name": library_playlist.name,
            "canDelete": library_playlist.can_delete,
            "canEdit": library_playlist.can_edit,
            "isPublic": library_playlist.is_public,
            "dateAdded": library_playlist.date_added,
            "lastModifiedDate": library_playlist.last_modified_date,
            "hasCatalog": library_playlist.has_catalog,
            "hasCollaboration": library_playlist.has_collaboration,
            "playParams": _play_params_library_playlist(library_playlist_id),
            "artwork": (
                _artwork(library_playlist.artwork)
                if library_playlist.artwork is not None
                else None
            ),
        }
    )
    out: dict[str, _JSONValue] = {
        "id": library_playlist_id,
        "type": "library-playlists",
        "href": f"/v1/me/library/playlists/{library_playlist_id}",
        "attributes": attrs,
    }
    if relationships:
        out["relationships"] = relationships
    return out
