"""Record-label resource JSON shape builder."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.endpoints.schema.builders import (
    _artwork,
    _description,
    _strip_none,
)

if TYPE_CHECKING:
    from musickit_api_mock.data.record_label import RecordLabel
    from musickit_api_mock.json_value import _JSONValue


def _record_label_resource(
    sf: str, record_label_id: str, record_label: RecordLabel
) -> dict[str, _JSONValue]:
    return {
        "id": record_label_id,
        "type": "record-labels",
        "href": f"/v1/catalog/{sf}/record-labels/{record_label_id}",
        "attributes": _strip_none(
            {
                "artwork": _artwork(record_label.artwork)
                if record_label.artwork is not None
                else None,
                "description": _description(record_label.description)
                if record_label.description is not None
                else None,
                "name": record_label.name,
                "url": record_label.url,
            }
        ),
    }
