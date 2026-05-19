"""Grouping resource JSON shape builder."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.endpoints.schema.builders import _artwork, _strip_none

if TYPE_CHECKING:
    from musickit_api_mock.data.grouping import Grouping
    from musickit_api_mock.json_value import _JSONValue


def _grouping_resource(
    sf: str, grouping_id: str, grouping: Grouping
) -> dict[str, _JSONValue]:
    return {
        "id": grouping_id,
        "type": "groupings",
        "href": f"/v1/catalog/{sf}/groupings/{grouping_id}",
        "attributes": _strip_none(
            {
                "artwork": _artwork(grouping.artwork)
                if grouping.artwork is not None
                else None,
                "name": grouping.name,
                "url": grouping.url,
            }
        ),
    }
