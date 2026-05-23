"""Handlers for HLS manifest and segment endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.data.lookup import LookupContext
from musickit_api_mock.endpoints.hls_manifest import _compose_manifest
from musickit_api_mock.transport.response_builders import (
    _bytes_response,
    _empty_response,
)

if TYPE_CHECKING:
    from musickit_api_mock.key_system import KeySystem
    from musickit_api_mock.mock import MusicKitApiMock
    from musickit_api_mock.surfaces.browser import EmeFlavorSetter
    from musickit_api_mock.transport.http import Response


def _resolve_eme_flavor(setter: EmeFlavorSetter) -> KeySystem | None:
    if setter is None:
        return None
    if callable(setter):
        return setter()
    return setter


def _handle_hls_manifest(mock: MusicKitApiMock, song_id: str) -> Response:
    song = mock._data_resolver.song.get(LookupContext(song_id, None))
    if song is None:
        return _empty_response(status=404)
    key_system = _resolve_eme_flavor(mock.browser.eme_flavor)
    manifest = _compose_manifest(song.hls_layout, key_system, song_id)
    return _bytes_response(manifest, content_type="application/vnd.apple.mpegurl")


def _handle_hls_segment(mock: MusicKitApiMock, song_id: str) -> Response:
    song = mock._data_resolver.song.get(LookupContext(song_id, None))
    if song is None:
        return _empty_response(status=404)
    return _bytes_response(song.hls_segment, content_type="video/mp4")
