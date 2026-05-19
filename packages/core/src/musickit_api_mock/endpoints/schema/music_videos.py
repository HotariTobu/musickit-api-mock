"""Music video resource JSON shape builder."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.endpoints.schema.builders import (
    _artwork,
    _preview,
    _strip_none,
)
from musickit_api_mock.endpoints.schema.play_params import _play_params_music_video

if TYPE_CHECKING:
    from musickit_api_mock.data.music_video import MusicVideo
    from musickit_api_mock.json_value import _JSONValue


def _music_video_resource(
    sf: str,
    music_video_id: str,
    music_video: MusicVideo,
    *,
    relationships: dict[str, _JSONValue] | None = None,
) -> dict[str, _JSONValue]:
    attrs: dict[str, _JSONValue] = _strip_none(
        {
            "name": music_video.name,
            "artistName": music_video.artist_name,
            "artwork": _artwork(music_video.artwork),
            "albumName": music_video.album_name,
            "audioTraits": None,
            "videoTraits": music_video.video_traits,
            "contentRating": music_video.content_rating,
            "discNumber": music_video.disc_number,
            "durationInMillis": music_video.duration_ms,
            "genreNames": music_video.genre_names,
            "has4K": music_video.has_4k,
            "hasHDR": music_video.has_hdr,
            "isrc": music_video.isrc,
            "playParams": _play_params_music_video(music_video_id),
            "previews": [_preview(p) for p in music_video.previews],
            "releaseDate": music_video.release_date,
            "trackNumber": music_video.track_number,
            "url": music_video.url,
        }
    )
    out: dict[str, _JSONValue] = {
        "id": music_video_id,
        "type": "music-videos",
        "href": f"/v1/catalog/{sf}/music-videos/{music_video_id}",
        "attributes": attrs,
    }
    if relationships:
        out["relationships"] = relationships
    return out
