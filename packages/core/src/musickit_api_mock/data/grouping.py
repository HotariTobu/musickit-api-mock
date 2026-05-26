"""Catalog grouping resource.

Apple curators hold a grouping id reference on their own dataclass.
The grouping surfaces inline when an apple-curator emits
``relationships.grouping`` (default-included) and as the data of
``/v1/catalog/{sf}/apple-curators/{id}/grouping``.
"""

from collections.abc import Callable
from dataclasses import dataclass

from musickit_api_mock.data.lookup import LookupContext, _lookup_source
from musickit_api_mock.data.primitives.artwork import Artwork


@dataclass
class Grouping:
    """Apple Music catalog grouping (editorial category for apple-curators).

    Attributes:
        name: Display name of the grouping.
        url: Grouping landing-page URL on Apple Music.
        artwork: Hero artwork for the grouping.
    """

    name: str
    url: str
    artwork: Artwork | None = None


type GroupingsSource = (
    dict[str, Grouping] | Callable[[LookupContext], Grouping | None] | None
)


class _GroupingResolver:
    """Library-internal lookup over ``DataSources.groupings``."""

    def __init__(self, get_source: Callable[[], GroupingsSource]) -> None:
        """Bind to the ``DataSources.groupings`` source via a callback."""
        self._get_source = get_source

    def get(self, context: LookupContext) -> Grouping | None:
        """Return the grouping for ``context.id`` or ``None`` if absent."""
        return _lookup_source(self._get_source(), "data.groupings", context)
