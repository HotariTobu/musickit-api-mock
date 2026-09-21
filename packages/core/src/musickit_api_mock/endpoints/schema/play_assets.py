"""Play-assets DRM, broadcast, and empty-asset body builders."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Sequence

    from musickit_api_mock.endpoints.responses.play_assets_broadcast import (
        PlayAssetsBroadcastAsset,
    )
    from musickit_api_mock.endpoints.schema.shapes import (
        AppleResponse,
        AppleResults,
    )
    from musickit_api_mock.json_value import _JSONValue


class _DrmAsset(Protocol):
    url: str
    fair_play_key_certificate_url: str
    key_server_url: str
    widevine_key_certificate_url: str


def _play_assets_drm_body(assets: Sequence[_DrmAsset]) -> AppleResponse:
    """Body for catalog-song / live-audio / live-video play_assets responses."""
    return {
        "results": {
            "assets": [
                {
                    "url": a.url,
                    "fairPlayKeyCertificateUrl": a.fair_play_key_certificate_url,
                    "keyServerUrl": a.key_server_url,
                    "widevineKeyCertificateUrl": a.widevine_key_certificate_url,
                }
                for a in assets
            ]
        }
    }


def _play_assets_broadcast_body(
    assets: list[PlayAssetsBroadcastAsset],
    track_info: dict[str, _JSONValue] | None,
) -> AppleResponse:
    """Body for broadcast play_assets response (no DRM key fields)."""
    results: AppleResults = {"assets": [{"url": a.url} for a in assets]}
    if track_info is not None:
        results["track-info"] = track_info
    return {"results": results}


def _play_assets_empty_body() -> AppleResponse:
    """``results.assets = []`` for ContentUnavailable / EmptyAssets cases."""
    return {"results": {"assets": []}}
