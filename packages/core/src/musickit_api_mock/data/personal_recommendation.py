"""User recommendation resource (``/v1/me/recommendations/{id}``).

A recommendation lists a set of catalog resources under an editorial title.
The linked resources can mix types within a single recommendation
(playlists + albums + stations etc.), so each content entry carries its
own type. The ``contents`` relationship is default-included by Apple.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from musickit_api_mock.data.lookup import LookupContext, _lookup_source

PersonalRecommendationContentKind = Literal[
    "playlists", "albums", "stations", "music-videos"
]
PersonalRecommendationKind = Literal[
    "music-recommendations", "playlist-recommendations", "recently-played"
]


@dataclass
class PersonalRecommendationContent:
    """A single content reference within a recommendation row.

    A recommendation's contents can be heterogeneous (playlists, albums,
    stations, music videos mixed in one row), so each entry carries its
    own type alongside the catalog id.

    Attributes:
        type: Resource type of the linked catalog resource.
        id: Catalog id of the linked resource.
    """

    type: PersonalRecommendationContentKind
    id: str


@dataclass
class PersonalRecommendationDisplay:
    """Editorial-shelf display hint for a recommendation row.

    Apple emits these values alongside the row attributes; user code can
    observe them via the response passthrough.

    Attributes:
        kind: Apple-defined display style identifier.
        decorations: Display-treatment tags applied to the row.
    """

    kind: str
    decorations: list[str] | None = None


@dataclass
class PersonalRecommendation:
    """A single user-recommendation row.

    Attributes:
        title: Editorial display name shown above the row in the UI.
        is_group_recommendation: Whether the row is a group recommendation.
        kind: Editorial category of the row (generic music recommendation,
            playlist-specific recommendation, recently-played row, etc.).
        next_update_date: ISO-8601 timestamp of the next refresh.
        reason: Optional editorial reason copy.
        resource_types: Resource types featured in the row.
        contents: Catalog resource references composing the row. Each entry
            pairs a resource type with a catalog id so a single row can
            mix types.
        display: Editorial-shelf display hint.
        has_see_all: Whether the row has a "see all" expansion.
        version: Apple's row revision marker.
    """

    title: str
    is_group_recommendation: bool
    kind: PersonalRecommendationKind
    next_update_date: str | None = None
    reason: str | None = None
    resource_types: list[str] | None = None
    contents: list[PersonalRecommendationContent] | None = None
    display: PersonalRecommendationDisplay | None = None
    has_see_all: bool | None = None
    version: int | None = None


type PersonalRecommendationsSource = (
    dict[str, PersonalRecommendation]
    | Callable[[LookupContext], PersonalRecommendation | None]
    | None
)


class _PersonalRecommendationResolver:
    """Library-internal lookup over ``DataSources.personal_recommendations``."""

    def __init__(self, get_source: Callable[[], PersonalRecommendationsSource]) -> None:
        """Bind to the ``DataSources.personal_recommendations`` source via a callback."""
        self._get_source = get_source

    def get(self, context: LookupContext) -> PersonalRecommendation | None:
        """Return the recommendation for ``context.id`` or ``None`` if absent."""
        return _lookup_source(
            self._get_source(), "data.personal_recommendations", context
        )
