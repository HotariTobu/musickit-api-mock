"""Handlers for ``web-playback`` and ``play-assets`` endpoints."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING
from urllib.parse import parse_qs

from musickit_api_mock.data.lookup import LookupContext
from musickit_api_mock.endpoints.playback_failure_codes import (
    _WEB_PLAYBACK_FAILURE_CODES,
)
from musickit_api_mock.endpoints.query import _parse_query
from musickit_api_mock.endpoints.responses.play_assets_broadcast import (
    PlayAssetsBroadcastContext,
    PlayAssetsBroadcastResponse,
    PlayAssetsBroadcastResponseAccessDenied,
    PlayAssetsBroadcastResponseContentUnavailable,
    PlayAssetsBroadcastResponseEmptyAssets,
    PlayAssetsBroadcastResponseServerError,
    PlayAssetsBroadcastResponseSubscriptionError,
    PlayAssetsBroadcastResponseSuccess,
)
from musickit_api_mock.endpoints.responses.play_assets_catalog_song import (
    PlayAssetsCatalogSongContext,
    PlayAssetsCatalogSongResponse,
    PlayAssetsCatalogSongResponseContentUnavailable,
    PlayAssetsCatalogSongResponseSuccess,
)
from musickit_api_mock.endpoints.responses.play_assets_live_audio import (
    PlayAssetsLiveAudioContext,
    PlayAssetsLiveAudioResponse,
    PlayAssetsLiveAudioResponseAccessDenied,
    PlayAssetsLiveAudioResponseContentUnavailable,
    PlayAssetsLiveAudioResponseEmptyAssets,
    PlayAssetsLiveAudioResponseServerError,
    PlayAssetsLiveAudioResponseSubscriptionError,
    PlayAssetsLiveAudioResponseSuccess,
)
from musickit_api_mock.endpoints.responses.play_assets_live_video import (
    PlayAssetsLiveVideoContext,
    PlayAssetsLiveVideoResponse,
    PlayAssetsLiveVideoResponseAccessDenied,
    PlayAssetsLiveVideoResponseContentUnavailable,
    PlayAssetsLiveVideoResponseEmptyAssets,
    PlayAssetsLiveVideoResponseServerError,
    PlayAssetsLiveVideoResponseSubscriptionError,
    PlayAssetsLiveVideoResponseSuccess,
)
from musickit_api_mock.endpoints.responses.web_playback import (
    WebPlaybackContext,
    WebPlaybackResponse,
    WebPlaybackResponseSuccess,
    WebPlaybackResponseUnsupportedError,
)
from musickit_api_mock.endpoints.schema import (
    _generic_error_envelope,
    _play_assets_403_envelope,
    _play_assets_broadcast_body,
    _play_assets_drm_body,
    _play_assets_empty_body,
    _web_playback_failure_body,
    _web_playback_success_body,
    _web_playback_unsupported_body,
)
from musickit_api_mock.transport.response_builders import (
    _empty_response,
    _json_response,
)

if TYPE_CHECKING:
    from musickit_api_mock.json_value import _JSONValue
    from musickit_api_mock.mock import MusicKitApiMock
    from musickit_api_mock.transport.http import Request, Response


_PLAY_ASSETS_SERVER_ERROR_STATUS = 500
_PLAY_ASSETS_FORBIDDEN_STATUS = 403
_PLAY_ASSETS_CONTENT_UNAVAILABLE_STATUS = 404
_PLAY_ASSETS_SUBSCRIPTION_ERROR_CODE = "40303"
_PLAY_ASSETS_ACCESS_DENIED_CODE = "40300"


def _decode_form_or_json(body: bytes | None) -> dict[str, _JSONValue]:
    if not body:
        return {}
    text = body.decode("utf-8", errors="replace").strip()
    if not text:
        return {}
    if text.startswith(("{", "[")):
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass
    out: dict[str, _JSONValue] = {}
    for k, v in parse_qs(text, keep_blank_values=True).items():
        out[k] = v[0] if len(v) == 1 else v
    return out


def _web_playback_failure_body_code(resp: WebPlaybackResponse) -> int:
    code = _WEB_PLAYBACK_FAILURE_CODES.get(type(resp))
    if code is None:
        raise TypeError(f"Unexpected web_playback response: {type(resp).__name__}")
    return code


def _handle_web_playback(mock: MusicKitApiMock, req: Request) -> Response:
    body = _decode_form_or_json(req.body)
    salable_adam_id = str(body.get("salableAdamId", ""))
    resp = mock._endpoint_resolver.web_playback(
        WebPlaybackContext(salable_adam_id=salable_adam_id)
    )
    if isinstance(resp, WebPlaybackResponseSuccess):
        return _json_response(_web_playback_success_body(resp))
    if isinstance(resp, WebPlaybackResponseUnsupportedError):
        return _json_response(_web_playback_unsupported_body())
    code = _web_playback_failure_body_code(resp)
    return _json_response(_web_playback_failure_body(code))


def _serialize_play_assets_catalog_song(
    resp: PlayAssetsCatalogSongResponse,
) -> Response:
    if isinstance(resp, PlayAssetsCatalogSongResponseSuccess):
        return _json_response(_play_assets_drm_body(resp.assets))
    if isinstance(resp, PlayAssetsCatalogSongResponseContentUnavailable):
        return _json_response(_play_assets_empty_body())
    raise TypeError(
        f"Unexpected play_assets_catalog_song response: {type(resp).__name__}"
    )


def _serialize_live_audio_response(resp: PlayAssetsLiveAudioResponse) -> Response:
    if isinstance(resp, PlayAssetsLiveAudioResponseSuccess):
        return _json_response(_play_assets_drm_body(resp.assets))
    if isinstance(resp, PlayAssetsLiveAudioResponseEmptyAssets):
        return _json_response(_play_assets_empty_body())
    if isinstance(resp, PlayAssetsLiveAudioResponseServerError):
        return _empty_response(status=_PLAY_ASSETS_SERVER_ERROR_STATUS)
    if isinstance(resp, PlayAssetsLiveAudioResponseSubscriptionError):
        return _json_response(
            _play_assets_403_envelope(
                _PLAY_ASSETS_SUBSCRIPTION_ERROR_CODE,
                "Forbidden",
                "Subscription required",
            ),
            status=_PLAY_ASSETS_FORBIDDEN_STATUS,
        )
    if isinstance(resp, PlayAssetsLiveAudioResponseAccessDenied):
        return _json_response(
            _play_assets_403_envelope(
                _PLAY_ASSETS_ACCESS_DENIED_CODE, "Forbidden", "Access denied"
            ),
            status=_PLAY_ASSETS_FORBIDDEN_STATUS,
        )
    if isinstance(resp, PlayAssetsLiveAudioResponseContentUnavailable):
        return _json_response(
            _generic_error_envelope(_PLAY_ASSETS_CONTENT_UNAVAILABLE_STATUS),
            status=_PLAY_ASSETS_CONTENT_UNAVAILABLE_STATUS,
        )
    raise TypeError(
        f"Unexpected play_assets_live_audio response: {type(resp).__name__}"
    )


def _serialize_live_video_response(resp: PlayAssetsLiveVideoResponse) -> Response:
    if isinstance(resp, PlayAssetsLiveVideoResponseSuccess):
        return _json_response(_play_assets_drm_body(resp.assets))
    if isinstance(resp, PlayAssetsLiveVideoResponseEmptyAssets):
        return _json_response(_play_assets_empty_body())
    if isinstance(resp, PlayAssetsLiveVideoResponseServerError):
        return _empty_response(status=_PLAY_ASSETS_SERVER_ERROR_STATUS)
    if isinstance(resp, PlayAssetsLiveVideoResponseSubscriptionError):
        return _json_response(
            _play_assets_403_envelope(
                _PLAY_ASSETS_SUBSCRIPTION_ERROR_CODE,
                "Forbidden",
                "Subscription required",
            ),
            status=_PLAY_ASSETS_FORBIDDEN_STATUS,
        )
    if isinstance(resp, PlayAssetsLiveVideoResponseAccessDenied):
        return _json_response(
            _play_assets_403_envelope(
                _PLAY_ASSETS_ACCESS_DENIED_CODE, "Forbidden", "Access denied"
            ),
            status=_PLAY_ASSETS_FORBIDDEN_STATUS,
        )
    if isinstance(resp, PlayAssetsLiveVideoResponseContentUnavailable):
        return _json_response(
            _generic_error_envelope(_PLAY_ASSETS_CONTENT_UNAVAILABLE_STATUS),
            status=_PLAY_ASSETS_CONTENT_UNAVAILABLE_STATUS,
        )
    raise TypeError(
        f"Unexpected play_assets_live_video response: {type(resp).__name__}"
    )


def _serialize_broadcast_response(resp: PlayAssetsBroadcastResponse) -> Response:
    if isinstance(resp, PlayAssetsBroadcastResponseSuccess):
        return _json_response(_play_assets_broadcast_body(resp.assets, resp.track_info))
    if isinstance(resp, PlayAssetsBroadcastResponseEmptyAssets):
        return _json_response(_play_assets_empty_body())
    if isinstance(resp, PlayAssetsBroadcastResponseServerError):
        return _empty_response(status=_PLAY_ASSETS_SERVER_ERROR_STATUS)
    if isinstance(resp, PlayAssetsBroadcastResponseSubscriptionError):
        return _json_response(
            _play_assets_403_envelope(
                _PLAY_ASSETS_SUBSCRIPTION_ERROR_CODE,
                "Forbidden",
                "Subscription required",
            ),
            status=_PLAY_ASSETS_FORBIDDEN_STATUS,
        )
    if isinstance(resp, PlayAssetsBroadcastResponseAccessDenied):
        return _json_response(
            _play_assets_403_envelope(
                _PLAY_ASSETS_ACCESS_DENIED_CODE, "Forbidden", "Access denied"
            ),
            status=_PLAY_ASSETS_FORBIDDEN_STATUS,
        )
    if isinstance(resp, PlayAssetsBroadcastResponseContentUnavailable):
        return _json_response(
            _generic_error_envelope(_PLAY_ASSETS_CONTENT_UNAVAILABLE_STATUS),
            status=_PLAY_ASSETS_CONTENT_UNAVAILABLE_STATUS,
        )
    raise TypeError(f"Unexpected play_assets_broadcast response: {type(resp).__name__}")


def _handle_play_assets(mock: MusicKitApiMock, req: Request) -> Response:
    q = _parse_query(req.url)
    asset_id = q.get("id", [""])[-1]
    kind = q.get("kind", [""])[-1]
    if not asset_id or kind not in ("song", "radioStation"):
        return _empty_response(status=400)
    if kind == "song":
        resp = mock._endpoint_resolver.play_assets_catalog_song(
            PlayAssetsCatalogSongContext(adam_id=asset_id)
        )
        return _serialize_play_assets_catalog_song(resp)

    if kind == "radioStation":
        station = mock._data_resolver.station.get(LookupContext(asset_id, None))
        if station is None:
            raise ValueError(
                f"play_assets requested station id {asset_id!r}"
                f" but mock.data.stations has no entry for it"
            )
        if station.media_kind == "video":
            resp = mock._endpoint_resolver.play_assets_live_video(
                PlayAssetsLiveVideoContext(station_id=asset_id)
            )
            return _serialize_live_video_response(resp)
        if station.has_drm:
            resp = mock._endpoint_resolver.play_assets_live_audio(
                PlayAssetsLiveAudioContext(station_id=asset_id)
            )
            return _serialize_live_audio_response(resp)
        resp = mock._endpoint_resolver.play_assets_broadcast(
            PlayAssetsBroadcastContext(station_id=asset_id)
        )
        return _serialize_broadcast_response(resp)

    raise AssertionError(f"unreachable: kind={kind!r}")
