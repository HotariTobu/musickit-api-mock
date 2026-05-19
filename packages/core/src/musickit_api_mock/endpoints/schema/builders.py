"""Shared schema builders: artwork, preview, description, editorial notes, play-asset, hashing."""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from musickit_api_mock.data.primitives.artwork import Artwork
    from musickit_api_mock.data.primitives.description import Description
    from musickit_api_mock.data.primitives.editorial_notes import EditorialNotes
    from musickit_api_mock.data.primitives.preview import Preview
    from musickit_api_mock.data.primitives.station_context_play_asset import (
        StationContextPlayAsset,
    )
    from musickit_api_mock.json_value import _JSONValue


def _strip_none(d: dict[str, _JSONValue]) -> dict[str, _JSONValue]:
    return {k: v for k, v in d.items() if v is not None}


def _artwork(a: Artwork) -> dict[str, _JSONValue]:
    out: dict[str, _JSONValue] = {
        "url": a.url,
        "width": a.width,
        "height": a.height,
    }
    if a.bg_color is not None:
        out["bgColor"] = a.bg_color
    if a.text_color_1 is not None:
        out["textColor1"] = a.text_color_1
    if a.text_color_2 is not None:
        out["textColor2"] = a.text_color_2
    if a.text_color_3 is not None:
        out["textColor3"] = a.text_color_3
    if a.text_color_4 is not None:
        out["textColor4"] = a.text_color_4
    if a.has_p3 is not None:
        out["hasP3"] = a.has_p3
    return out


def _preview(p: Preview) -> dict[str, _JSONValue]:
    out: dict[str, _JSONValue] = {"url": p.url}
    if p.hls_url is not None:
        out["hlsUrl"] = p.hls_url
    if p.artwork is not None:
        out["artwork"] = _artwork(p.artwork)
    return out


def _description(d: Description) -> dict[str, _JSONValue]:
    out: dict[str, _JSONValue] = {"standard": d.standard}
    if d.short is not None:
        out["short"] = d.short
    return out


def _editorial_notes(n: EditorialNotes) -> dict[str, _JSONValue]:
    return _strip_none(
        {
            "name": n.name,
            "short": n.short,
            "standard": n.standard,
            "tagline": n.tagline,
        }
    )


def _play_asset(p: StationContextPlayAsset) -> dict[str, _JSONValue]:
    return {"bitRate": p.bit_rate, "url": p.url}


def _stable_hash(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode()).hexdigest()[:16]
