"""Response body builders: assemble Apple Music API JSON shapes from data sources."""

from musickit_api_mock.endpoints.schema.account import (
    _account_envelope,
    _storefront_envelope,
    _storefront_resource,
)
from musickit_api_mock.endpoints.schema.albums import _album_resource
from musickit_api_mock.endpoints.schema.artists import _artist_resource
from musickit_api_mock.endpoints.schema.auth import (
    _renew_music_token_success_body,
    _webplayer_logout_success_body,
)
from musickit_api_mock.endpoints.schema.curators import _curator_resource
from musickit_api_mock.endpoints.schema.envelope import (
    _batch_envelope,
    _continuous_stations_errors_envelope,
    _continuous_stations_no_station_envelope,
    _empty_ids_400_envelope,
    _generic_error_envelope,
    _invalid_language_tag_envelope,
    _library_songs_dead_path_400_envelope,
    _limit_exceeded_envelope,
    _missing_ids_param_400_envelope,
    _parameter_invalid_envelope,
    _play_assets_403_envelope,
    _resource_not_found_404_envelope,
    _session_expired_403_envelope,
    _session_expired_renew_401_body,
)
from musickit_api_mock.endpoints.schema.genres import _genre_resource
from musickit_api_mock.endpoints.schema.groupings import _grouping_resource
from musickit_api_mock.endpoints.schema.library_albums import _library_album_resource
from musickit_api_mock.endpoints.schema.library_artists import _library_artist_resource
from musickit_api_mock.endpoints.schema.library_music_videos import (
    _library_music_video_resource,
)
from musickit_api_mock.endpoints.schema.library_playlists import (
    _library_playlist_resource,
)
from musickit_api_mock.endpoints.schema.library_songs import _library_song_resource
from musickit_api_mock.endpoints.schema.license import (
    _license_failure_body,
    _license_success_body,
)
from musickit_api_mock.endpoints.schema.music_videos import _music_video_resource
from musickit_api_mock.endpoints.schema.personal_recommendations import (
    _personal_recommendation_resource,
)
from musickit_api_mock.endpoints.schema.play_assets import (
    _play_assets_broadcast_body,
    _play_assets_drm_body,
    _play_assets_empty_body,
)
from musickit_api_mock.endpoints.schema.playlists import _playlist_resource
from musickit_api_mock.endpoints.schema.record_labels import _record_label_resource
from musickit_api_mock.endpoints.schema.refs import _catalog_ref, _library_ref
from musickit_api_mock.endpoints.schema.songs import _song_resource
from musickit_api_mock.endpoints.schema.stations import (
    _continuous_station_envelope,
    _station_resource,
)
from musickit_api_mock.endpoints.schema.web_playback import (
    _web_playback_failure_body,
    _web_playback_success_body,
    _web_playback_unsupported_body,
)

__all__ = [
    "_account_envelope",
    "_album_resource",
    "_artist_resource",
    "_batch_envelope",
    "_catalog_ref",
    "_continuous_station_envelope",
    "_continuous_stations_errors_envelope",
    "_continuous_stations_no_station_envelope",
    "_curator_resource",
    "_empty_ids_400_envelope",
    "_generic_error_envelope",
    "_genre_resource",
    "_grouping_resource",
    "_invalid_language_tag_envelope",
    "_library_album_resource",
    "_library_artist_resource",
    "_library_music_video_resource",
    "_library_playlist_resource",
    "_library_ref",
    "_library_song_resource",
    "_library_songs_dead_path_400_envelope",
    "_license_failure_body",
    "_license_success_body",
    "_limit_exceeded_envelope",
    "_missing_ids_param_400_envelope",
    "_music_video_resource",
    "_parameter_invalid_envelope",
    "_personal_recommendation_resource",
    "_play_assets_403_envelope",
    "_play_assets_broadcast_body",
    "_play_assets_drm_body",
    "_play_assets_empty_body",
    "_playlist_resource",
    "_record_label_resource",
    "_renew_music_token_success_body",
    "_resource_not_found_404_envelope",
    "_session_expired_403_envelope",
    "_session_expired_renew_401_body",
    "_song_resource",
    "_station_resource",
    "_storefront_envelope",
    "_storefront_resource",
    "_web_playback_failure_body",
    "_web_playback_success_body",
    "_web_playback_unsupported_body",
    "_webplayer_logout_success_body",
]
