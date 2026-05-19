"""Personal-recommendation resource JSON shape builder."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.endpoints.schema.builders import _strip_none

if TYPE_CHECKING:
    from musickit_api_mock.data.personal_recommendation import (
        PersonalRecommendation,
        PersonalRecommendationDisplay,
    )
    from musickit_api_mock.json_value import _JSONValue


def _personal_recommendation_display(
    display: PersonalRecommendationDisplay,
) -> dict[str, _JSONValue]:
    return {
        "kind": display.kind,
        "decorations": list(display.decorations) if display.decorations else [],
    }


def _personal_recommendation_resource(
    recommendation_id: str,
    recommendation: PersonalRecommendation,
    *,
    relationships: dict[str, _JSONValue] | None = None,
) -> dict[str, _JSONValue]:
    out: dict[str, _JSONValue] = {
        "id": recommendation_id,
        "type": "personal-recommendation",
        "href": f"/v1/me/recommendations/{recommendation_id}",
        "attributes": _strip_none(
            {
                "display": (
                    _personal_recommendation_display(recommendation.display)
                    if recommendation.display is not None
                    else None
                ),
                "hasSeeAll": recommendation.has_see_all,
                "isGroupRecommendation": recommendation.is_group_recommendation,
                "kind": recommendation.kind,
                "nextUpdateDate": recommendation.next_update_date,
                "reason": recommendation.reason,
                "resourceTypes": recommendation.resource_types,
                "title": {"stringForDisplay": recommendation.title},
                "version": recommendation.version,
            }
        ),
    }
    if relationships is not None:
        out["relationships"] = relationships
    return out
