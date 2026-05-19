"""Playlist resource JSON shape builder."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.endpoints.schema.builders import (
    _artwork,
    _description,
    _editorial_notes,
    _strip_none,
)
from musickit_api_mock.endpoints.schema.play_params import _play_params_playlist

if TYPE_CHECKING:
    from musickit_api_mock.data.playlist import Playlist
    from musickit_api_mock.json_value import _JSONValue


def _playlist_resource(
    sf: str,
    playlist_id: str,
    playlist: Playlist,
    *,
    relationships: dict[str, _JSONValue] | None = None,
) -> dict[str, _JSONValue]:
    attrs: dict[str, _JSONValue] = _strip_none(
        {
            "name": playlist.name,
            "artwork": (
                _artwork(playlist.artwork) if playlist.artwork is not None else None
            ),
            "audioTraits": playlist.audio_traits,
            "curatorName": playlist.curator_name,
            "description": (
                _description(playlist.description)
                if playlist.description is not None
                else None
            ),
            "editorialNotes": (
                _editorial_notes(playlist.editorial_notes)
                if playlist.editorial_notes is not None
                else None
            ),
            "hasCollaboration": playlist.has_collaboration,
            "isChart": playlist.is_chart,
            "lastModifiedDate": playlist.last_modified,
            "playParams": _play_params_playlist(playlist_id),
            "playlistType": playlist.playlist_type,
            "supportsSing": playlist.supports_sing,
            "url": playlist.url,
        }
    )
    out: dict[str, _JSONValue] = {
        "id": playlist_id,
        "type": "playlists",
        "href": f"/v1/catalog/{sf}/playlists/{playlist_id}",
        "attributes": attrs,
    }
    if relationships:
        out["relationships"] = relationships
    return out
