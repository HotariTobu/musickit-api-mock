"""``playParams`` builders per resource type."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.endpoints.schema.builders import _stable_hash

if TYPE_CHECKING:
    from musickit_api_mock.data.library_song import LibrarySong
    from musickit_api_mock.data.station import Station
    from musickit_api_mock.json_value import _JSONValue


def _play_params_song(song_id: str) -> dict[str, _JSONValue]:
    return {"id": song_id, "kind": "song"}


def _play_params_album(album_id: str) -> dict[str, _JSONValue]:
    return {"id": album_id, "kind": "album"}


def _play_params_playlist(playlist_id: str) -> dict[str, _JSONValue]:
    return {"id": playlist_id, "kind": "playlist"}


def _play_params_music_video(music_video_id: str) -> dict[str, _JSONValue]:
    return {"id": music_video_id, "kind": "musicVideo"}


def _play_params_station(station_id: str, station: Station) -> dict[str, _JSONValue]:
    out: dict[str, _JSONValue] = {
        "id": station_id,
        "kind": "radioStation",
        "hasDrm": station.has_drm,
        "mediaType": station.media_kind,
        "stationHash": _stable_hash(station_id, station.kind),
    }
    if station.is_tracks_station:
        out["format"] = "tracks"
    return out


def _play_params_library_song(
    library_song_id: str, library_song: LibrarySong
) -> dict[str, _JSONValue]:
    out: dict[str, _JSONValue] = {
        "id": library_song_id,
        "kind": "song",
        "isLibrary": True,
        "reporting": False,
        "reportingId": _stable_hash(library_song_id),
    }
    if library_song.catalog_id is not None:
        out["catalogId"] = library_song.catalog_id
    return out


def _play_params_library_album(album_id: str) -> dict[str, _JSONValue]:
    return {
        "id": album_id,
        "kind": "album",
        "isLibrary": True,
        "reporting": False,
        "reportingId": _stable_hash(album_id),
    }


def _play_params_library_playlist(playlist_id: str) -> dict[str, _JSONValue]:
    return {
        "id": playlist_id,
        "kind": "playlist",
        "isLibrary": True,
        "reporting": False,
        "reportingId": _stable_hash(playlist_id),
    }


def _play_params_library_music_video(
    library_music_video_id: str,
) -> dict[str, _JSONValue]:
    return {
        "id": library_music_video_id,
        "kind": "musicVideo",
        "isLibrary": True,
        "reporting": False,
        "reportingId": _stable_hash(library_music_video_id),
    }
