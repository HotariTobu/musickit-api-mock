"""Library playlist folder resource JSON shape builders."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.endpoints.schema.builders import _strip_none

if TYPE_CHECKING:
    from musickit_api_mock.data.library_playlist_folder import LibraryPlaylistFolder
    from musickit_api_mock.endpoints.schema.shapes import (
        AppleRelationshipBlock,
        AppleResource,
    )


def _library_playlist_folder_href(folder_id: str) -> str:
    return f"/v1/me/library/playlist-folders/{folder_id}"


def _library_playlist_folder_ref(folder_id: str) -> AppleResource:
    """Shallow ``{id, type, href}`` ref; also the root's shape, which has no attributes."""
    return {
        "id": folder_id,
        "type": "library-playlist-folders",
        "href": _library_playlist_folder_href(folder_id),
    }


def _library_playlist_folder_resource(
    folder_id: str,
    folder: LibraryPlaylistFolder,
    *,
    relationships: dict[str, AppleRelationshipBlock] | None = None,
) -> AppleResource:
    out = _library_playlist_folder_ref(folder_id)
    out["attributes"] = _strip_none(
        {"name": folder.name, "dateAdded": folder.date_added}
    )
    if relationships:
        out["relationships"] = relationships
    return out


def _library_playlist_folder_root_resource(
    relationships: dict[str, AppleRelationshipBlock],
) -> AppleResource:
    out = _library_playlist_folder_ref("p.playlistsroot")
    out["relationships"] = relationships
    return out


def _counted_relationship_block(
    href: str,
    data: list[AppleResource],
    total: int,
    *,
    next_offset: int | None = None,
) -> AppleRelationshipBlock:
    """Relationship block carrying ``meta.total`` and an optional ``next``."""
    if next_offset is not None:
        return {
            "href": href,
            "next": f"{href}?offset={next_offset}",
            "data": data,
            "meta": {"total": total},
        }
    return {"href": href, "data": data, "meta": {"total": total}}
