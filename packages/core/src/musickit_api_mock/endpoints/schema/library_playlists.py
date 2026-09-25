"""Library playlist resource JSON shape builders."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.endpoints.schema.builders import (
    _artwork,
    _description,
    _strip_none,
)
from musickit_api_mock.endpoints.schema.play_params import _play_params_library_playlist

if TYPE_CHECKING:
    from musickit_api_mock.data.library_playlist import LibraryPlaylist
    from musickit_api_mock.data.library_playlist_folder import LibraryPlaylistFolder
    from musickit_api_mock.json_value import _JSONValue


def _wrap(
    library_playlist_id: str,
    attrs: dict[str, _JSONValue],
    relationships: dict[str, _JSONValue] | None,
) -> dict[str, _JSONValue]:
    out: dict[str, _JSONValue] = {
        "id": library_playlist_id,
        "type": "library-playlists",
        "href": f"/v1/me/library/playlists/{library_playlist_id}",
        "attributes": attrs,
    }
    if relationships:
        out["relationships"] = relationships
    return out


def _library_playlist_resource(
    library_playlist_id: str,
    library_playlist: LibraryPlaylist,
    *,
    relationships: dict[str, _JSONValue] | None = None,
) -> dict[str, _JSONValue]:
    attrs: dict[str, _JSONValue] = _strip_none(
        {
            "name": library_playlist.name,
            "canEdit": library_playlist.can_edit,
            "isPublic": library_playlist.is_public,
            "dateAdded": library_playlist.date_added,
            "lastModifiedDate": library_playlist.last_modified_date,
            "hasCatalog": library_playlist.has_catalog,
            "playParams": _play_params_library_playlist(
                library_playlist_id, library_playlist.catalog_id
            ),
            "artwork": (
                _artwork(library_playlist.artwork)
                if library_playlist.artwork is not None
                else None
            ),
            "description": (
                _description(library_playlist.description)
                if library_playlist.description is not None
                else None
            ),
        }
    )
    return _wrap(library_playlist_id, attrs, relationships)


def _library_playlist_folder_as_playlist_resource(
    folder_id: str,
    folder: LibraryPlaylistFolder,
    *,
    relationships: dict[str, _JSONValue] | None = None,
) -> dict[str, _JSONValue]:
    """A folder answered on the library playlist paths, shaped as a playlist."""
    attrs: dict[str, _JSONValue] = _strip_none(
        {
            "name": folder.name,
            "canEdit": False,
            "isPublic": False,
            "dateAdded": folder.date_added,
            "lastModifiedDate": folder.last_modified_date,
            "hasCatalog": False,
            "playParams": _play_params_library_playlist(folder_id, None),
        }
    )
    return _wrap(folder_id, attrs, relationships)


def _library_playlist_placeholder_resource(
    library_playlist_id: str,
    *,
    relationships: dict[str, _JSONValue] | None = None,
) -> dict[str, _JSONValue]:
    """Apple's stand-in for an unknown ``p.`` id in an ``?ids=`` fetch."""
    attrs: dict[str, _JSONValue] = {
        "canEdit": False,
        "isPublic": False,
        "lastModifiedDate": "1970-01-01T00:00:00Z",
        "hasCatalog": False,
        "playParams": _play_params_library_playlist(library_playlist_id, None),
    }
    return _wrap(library_playlist_id, attrs, relationships)
