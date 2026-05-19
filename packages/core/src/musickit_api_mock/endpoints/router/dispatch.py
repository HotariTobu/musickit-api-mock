"""Dispatch matched endpoint names to handler functions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.endpoints import (
    activity,
    auth,
    browser,
    catalog,
    drm,
    hls,
    library,
    me,
    playback,
    preview,
    relationships,
    station,
)

if TYPE_CHECKING:
    from musickit_api_mock.mock import MusicKitApiMock
    from musickit_api_mock.transport.http import Request, Response


def _dispatch(
    mock: MusicKitApiMock,
    req: Request,
    endpoint: str,
    kwargs: dict[str, str],
) -> Response | None:
    match endpoint:
        case "me.storefront":
            return me._handle_storefront(mock, req)
        case "me.account":
            return me._handle_account(mock, req)
        case "catalog.songs":
            return catalog._handle_songs(mock, req, kwargs["sf"])
        case "catalog.albums":
            return catalog._handle_albums(mock, req, kwargs["sf"])
        case "catalog.playlists":
            return catalog._handle_playlists(mock, req, kwargs["sf"])
        case "catalog.artists":
            return catalog._handle_artists(mock, req, kwargs["sf"])
        case "catalog.music_videos":
            return catalog._handle_music_videos(mock, req, kwargs["sf"])
        case "catalog.stations":
            return catalog._handle_stations(mock, req, kwargs["sf"])
        case "catalog.station":
            return catalog._handle_station_singular(
                mock, req, kwargs["sf"], kwargs["station_id"]
            )
        case "catalog.song":
            return catalog._handle_song_singular(
                mock, req, kwargs["sf"], kwargs["song_id"]
            )
        case "catalog.song_albums":
            return relationships._handle_song_albums(
                mock, req, kwargs["sf"], kwargs["song_id"]
            )
        case "catalog.song_artists":
            return relationships._handle_song_artists(
                mock, req, kwargs["sf"], kwargs["song_id"]
            )
        case "catalog.song_composers":
            return relationships._handle_song_composers(
                mock, req, kwargs["sf"], kwargs["song_id"]
            )
        case "catalog.song_library":
            return relationships._handle_song_library(
                mock, req, kwargs["sf"], kwargs["song_id"]
            )
        case "catalog.album_library":
            return relationships._handle_album_library(
                mock, req, kwargs["sf"], kwargs["album_id"]
            )
        case "catalog.music_video_library":
            return relationships._handle_music_video_library(
                mock, req, kwargs["sf"], kwargs["music_video_id"]
            )
        case "catalog.playlist_library":
            return relationships._handle_playlist_library(
                mock, req, kwargs["sf"], kwargs["playlist_id"]
            )
        case "catalog.unsupported":
            return catalog._handle_unsupported_kind()
        case "catalog.artist_albums":
            return relationships._handle_artist_albums(
                mock, req, kwargs["sf"], kwargs["artist_id"]
            )
        case "catalog.album_tracks":
            return relationships._handle_album_tracks(
                mock, req, kwargs["sf"], kwargs["album_id"]
            )
        case "catalog.album_artists":
            return relationships._handle_album_artists(
                mock, req, kwargs["sf"], kwargs["album_id"]
            )
        case "catalog.playlist_tracks":
            return relationships._handle_playlist_tracks(
                mock, req, kwargs["sf"], kwargs["playlist_id"]
            )
        case "catalog.music_video_albums":
            return relationships._handle_music_video_albums(
                mock, req, kwargs["sf"], kwargs["music_video_id"]
            )
        case "catalog.music_video_artists":
            return relationships._handle_music_video_artists(
                mock, req, kwargs["sf"], kwargs["music_video_id"]
            )
        case "library.songs_batch":
            return library._handle_library_songs(mock, req)
        case "library.songs_dead":
            return library._handle_library_songs_dead_path()
        case "library.song":
            return library._handle_library_song(mock, req, kwargs["item_id"])
        case "library.album":
            return library._handle_library_album(mock, req, kwargs["item_id"])
        case "library.playlist":
            return library._handle_library_playlist(mock, req, kwargs["item_id"])
        case "library.artist":
            return library._handle_library_artist(mock, req, kwargs["item_id"])
        case "library.music_video":
            return library._handle_library_music_video(mock, req, kwargs["item_id"])
        case "library.album_tracks":
            return relationships._handle_library_album_tracks(
                mock, req, kwargs["album_id"]
            )
        case "library.album_artists":
            return relationships._handle_library_album_artists(
                mock, req, kwargs["album_id"]
            )
        case "library.playlist_tracks":
            return relationships._handle_library_playlist_tracks(
                mock, req, kwargs["playlist_id"]
            )
        case "library.music_video_albums":
            return relationships._handle_library_music_video_albums(
                mock, req, kwargs["music_video_id"]
            )
        case "library.music_video_artists":
            return relationships._handle_library_music_video_artists(
                mock, req, kwargs["music_video_id"]
            )
        case "library.song_albums":
            return relationships._handle_library_song_albums(
                mock, req, kwargs["library_song_id"]
            )
        case "library.song_artists":
            return relationships._handle_library_song_artists(
                mock, req, kwargs["library_song_id"]
            )
        case "library.song_catalog":
            return relationships._handle_library_song_catalog(
                mock, req, kwargs["library_song_id"]
            )
        case "library.album_catalog":
            return relationships._handle_library_album_catalog(
                mock, req, kwargs["library_album_id"]
            )
        case "library.music_video_catalog":
            return relationships._handle_library_music_video_catalog(
                mock, req, kwargs["library_music_video_id"]
            )
        case "library.playlist_catalog":
            return relationships._handle_library_playlist_catalog(
                mock, req, kwargs["library_playlist_id"]
            )
        case "library.artist_albums":
            return relationships._handle_library_artist_albums(
                mock, req, kwargs["library_artist_id"]
            )
        case "library.artist_catalog":
            return relationships._handle_library_artist_catalog(
                mock, req, kwargs["library_artist_id"]
            )
        case "catalog.song_genres":
            return relationships._handle_song_genres(
                mock, req, kwargs["sf"], kwargs["song_id"]
            )
        case "catalog.song_station":
            return relationships._handle_song_station(
                mock, req, kwargs["sf"], kwargs["song_id"]
            )
        case "catalog.song_music_videos":
            return relationships._handle_song_music_videos(
                mock, req, kwargs["sf"], kwargs["song_id"]
            )
        case "catalog.album_genres":
            return relationships._handle_album_genres(
                mock, req, kwargs["sf"], kwargs["album_id"]
            )
        case "catalog.album_record_labels":
            return relationships._handle_album_record_labels(
                mock, req, kwargs["sf"], kwargs["album_id"]
            )
        case "catalog.artist_genres":
            return relationships._handle_artist_genres(
                mock, req, kwargs["sf"], kwargs["artist_id"]
            )
        case "catalog.artist_music_videos":
            return relationships._handle_artist_music_videos(
                mock, req, kwargs["sf"], kwargs["artist_id"]
            )
        case "catalog.artist_playlists":
            return relationships._handle_artist_playlists(
                mock, req, kwargs["sf"], kwargs["artist_id"]
            )
        case "catalog.artist_station":
            return relationships._handle_artist_station(
                mock, req, kwargs["sf"], kwargs["artist_id"]
            )
        case "catalog.music_video_genres":
            return relationships._handle_music_video_genres(
                mock, req, kwargs["sf"], kwargs["music_video_id"]
            )
        case "catalog.music_video_songs":
            return relationships._handle_music_video_songs(
                mock, req, kwargs["sf"], kwargs["music_video_id"]
            )
        case "catalog.station_radio_show":
            return relationships._handle_station_radio_show(
                mock, req, kwargs["sf"], kwargs["station_id"]
            )
        case "catalog.apple_curator":
            return relationships._handle_apple_curator_singular(
                mock, req, kwargs["sf"], kwargs["apple_curator_id"]
            )
        case "catalog.apple_curator_playlists":
            return relationships._handle_apple_curator_playlists(
                mock, req, kwargs["sf"], kwargs["apple_curator_id"]
            )
        case "catalog.apple_curator_grouping":
            return relationships._handle_apple_curator_grouping(
                mock, req, kwargs["sf"], kwargs["apple_curator_id"]
            )
        case "catalog.curator":
            return relationships._handle_curator_singular(
                mock, req, kwargs["sf"], kwargs["curator_id"]
            )
        case "catalog.curator_playlists":
            return relationships._handle_curator_playlists(
                mock, req, kwargs["sf"], kwargs["curator_id"]
            )
        case "me.recommendation":
            return relationships._handle_recommendation_singular(
                mock, req, kwargs["recommendation_id"]
            )
        case "me.recommendations":
            return relationships._handle_recommendations_batch(mock, req)
        case "catalog.genres":
            return relationships._handle_genres_batch(mock, req, kwargs["sf"])
        case "catalog.genre":
            return relationships._handle_genre_singular(
                mock, req, kwargs["sf"], kwargs["genre_id"]
            )
        case "catalog.record_labels":
            return relationships._handle_record_labels_batch(mock, req, kwargs["sf"])
        case "catalog.record_label":
            return relationships._handle_record_label_singular(
                mock, req, kwargs["sf"], kwargs["record_label_id"]
            )
        case "playback.play_assets":
            return playback._handle_play_assets(mock, req)
        case "playback.web_playback":
            return playback._handle_web_playback(mock, req)
        case "station.next_tracks":
            return station._handle_next_tracks(mock, req, kwargs["station_id"])
        case "station.continuous":
            return station._handle_continuous(mock, req)
        case "auth.webplayer_logout":
            return auth._handle_webplayer_logout(mock)
        case "auth.renew_music_token":
            return auth._handle_renew_music_token(mock)
        case "drm.widevine_cert":
            return drm._handle_widevine_cert(mock)
        case "drm.fairplay_cert":
            return drm._handle_fairplay_cert(mock)
        case "drm.license_acquire":
            return drm._handle_acquire_web_playback_license(mock, req)
        case "drm.streaming_key_delivery":
            return drm._handle_streaming_key_delivery(mock, req)
        case "activity.play_activity":
            return activity._handle_play_activity(mock)
        case "hls.manifest":
            return hls._handle_hls_manifest(mock, kwargs["song_id"])
        case "hls.segment":
            return hls._handle_hls_segment(mock, kwargs["song_id"])
        case "preview.preview":
            return preview._handle_preview(mock, kwargs["song_id"])
        case "browser.authorize_response":
            return browser._handle_authorize_response(mock)
        case _:
            return None
