"""Shallow ``{id, type, href}`` ref builders for relationship ``data[]`` entries."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from musickit_api_mock.json_value import _JSONValue


def _catalog_ref(sf: str, item_type: str, item_id: str) -> dict[str, _JSONValue]:
    """Shallow ref for a catalog resource at ``/v1/catalog/<sf>/<type>/<id>``."""
    return {
        "id": item_id,
        "type": item_type,
        "href": f"/v1/catalog/{sf}/{item_type}/{item_id}",
    }


def _library_ref(item_type: str, item_id: str) -> dict[str, _JSONValue]:
    """Shallow ref for a library resource at ``/v1/me/library/<type>/<id>``."""
    return {
        "id": item_id,
        "type": item_type,
        "href": f"/v1/me/library/{item_type}/{item_id}",
    }
