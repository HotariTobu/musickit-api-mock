"""Library music video resource JSON shape builder."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.endpoints.schema.builders import (
    _artwork,
    _strip_none,
)
from musickit_api_mock.endpoints.schema.play_params import (
    _play_params_library_music_video,
)

if TYPE_CHECKING:
    from musickit_api_mock.data.library_music_video import LibraryMusicVideo
    from musickit_api_mock.json_value import _JSONValue


def _library_music_video_resource(
    library_music_video_id: str,
    library_music_video: LibraryMusicVideo,
    *,
    relationships: dict[str, _JSONValue] | None = None,
) -> dict[str, _JSONValue]:
    attrs: dict[str, _JSONValue] = _strip_none(
        {
            "name": library_music_video.name,
            "artistName": library_music_video.artist_name,
            "albumName": library_music_video.album_name,
            "artwork": _artwork(library_music_video.artwork),
            "contentRating": library_music_video.content_rating,
            "durationInMillis": library_music_video.duration_ms,
            "genreNames": library_music_video.genre_names,
            "playParams": _play_params_library_music_video(library_music_video_id),
            "releaseDate": library_music_video.release_date,
            "trackNumber": library_music_video.track_number,
        }
    )
    out: dict[str, _JSONValue] = {
        "id": library_music_video_id,
        "type": "library-music-videos",
        "href": f"/v1/me/library/music-videos/{library_music_video_id}",
        "attributes": attrs,
    }
    if relationships:
        out["relationships"] = relationships
    return out
