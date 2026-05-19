"""Library song resource JSON shape builder."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.endpoints.schema.builders import (
    _artwork,
    _strip_none,
)
from musickit_api_mock.endpoints.schema.play_params import _play_params_library_song

if TYPE_CHECKING:
    from musickit_api_mock.data.library_song import LibrarySong
    from musickit_api_mock.json_value import _JSONValue


def _library_song_resource(
    library_song_id: str,
    library_song: LibrarySong,
    *,
    relationships: dict[str, _JSONValue] | None = None,
) -> dict[str, _JSONValue]:
    attrs: dict[str, _JSONValue] = _strip_none(
        {
            "name": library_song.name,
            "artistName": library_song.artist_name,
            "albumName": library_song.album_name,
            "artwork": _artwork(library_song.artwork),
            "discNumber": library_song.disc_number,
            "durationInMillis": library_song.duration_ms,
            "genreNames": library_song.genre_names,
            "hasLyrics": library_song.has_lyrics,
            "playParams": _play_params_library_song(library_song_id, library_song),
            "releaseDate": library_song.release_date,
            "trackNumber": library_song.track_number,
        }
    )
    out: dict[str, _JSONValue] = {
        "id": library_song_id,
        "type": "library-songs",
        "href": f"/v1/me/library/songs/{library_song_id}",
        "attributes": attrs,
    }
    if relationships:
        out["relationships"] = relationships
    return out
