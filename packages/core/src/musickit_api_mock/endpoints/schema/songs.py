"""Song resource JSON shape builder and preview URL helper."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.endpoints.schema.builders import (
    _artwork,
    _play_asset,
    _strip_none,
)
from musickit_api_mock.endpoints.schema.play_params import _play_params_song

if TYPE_CHECKING:
    from musickit_api_mock.data.song import Song
    from musickit_api_mock.json_value import _JSONValue


def _preview_url_for(song_id: str) -> str:
    return f"https://audio-ssl.itunes.apple.com/preview/{song_id}.m4a"


def _song_resource(
    sf: str,
    song_id: str,
    song: Song,
    *,
    relationships: dict[str, _JSONValue] | None = None,
    include_play_assets: bool = False,
) -> dict[str, _JSONValue]:
    attrs: dict[str, _JSONValue] = _strip_none(
        {
            "name": song.title,
            "artistName": song.artist,
            "albumName": song.album,
            "artwork": _artwork(song.artwork),
            "audioLocale": song.audio_locale,
            "audioTraits": song.audio_traits,
            "durationInMillis": song.duration_ms,
            "genreNames": song.genres,
            "releaseDate": song.release_date,
            "trackNumber": song.track_number,
            "discNumber": song.disc_number,
            "composerName": song.composer,
            "hasLyrics": song.has_lyrics,
            "hasTimeSyncedLyrics": song.has_time_synced_lyrics,
            "isAppleDigitalMaster": song.is_apple_digital_master,
            "isMasteredForItunes": song.is_mastered_for_itunes,
            "isVocalAttenuationAllowed": song.is_vocal_attenuation_allowed,
            "isrc": song.isrc,
            "playParams": _play_params_song(song_id),
            "previews": [{"url": _preview_url_for(song_id)}],
            "url": song.url,
            "contentRating": song.content_rating,
        }
    )
    if include_play_assets and song.play_assets is not None:
        attrs["playAssets"] = [_play_asset(p) for p in song.play_assets]
    out: dict[str, _JSONValue] = {
        "id": song_id,
        "type": "songs",
        "href": f"/v1/catalog/{sf}/songs/{song_id}",
        "attributes": attrs,
    }
    if relationships:
        out["relationships"] = relationships
    return out
