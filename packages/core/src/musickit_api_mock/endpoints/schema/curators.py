"""Curator resource and reference shape builders."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.endpoints.schema.builders import _artwork, _strip_none

if TYPE_CHECKING:
    from musickit_api_mock.data.curator import Curator
    from musickit_api_mock.json_value import _JSONValue


def _curator_resource(
    sf: str,
    curator_id: str,
    curator: Curator,
    *,
    relationships: dict[str, _JSONValue] | None = None,
) -> dict[str, _JSONValue]:
    """Branch the emitted ``type`` and ``href`` prefix on the curator kind.

    ``apple-curators`` is Apple-editorial, ``curators`` is third-party;
    the curator's kind selects both the emitted ``type`` and the URL segment.
    """
    out: dict[str, _JSONValue] = {
        "id": curator_id,
        "type": curator.type,
        "href": f"/v1/catalog/{sf}/{curator.type}/{curator_id}",
        "attributes": _strip_none(
            {
                "artwork": _artwork(curator.artwork),
                "kind": curator.kind,
                "name": curator.name,
                "shortName": curator.short_name,
                "url": curator.url,
            }
        ),
    }
    if relationships is not None:
        out["relationships"] = relationships
    return out
