"""Catalog genre resource.

Songs / albums / artists / music videos hold genre id references on their
own dataclass. Genres surface inline when the parent emits
``relationships.genres`` (on ``?include=genres``) and as the data of the
standalone ``/v1/catalog/{sf}/{resource}/{id}/genres`` endpoints.
"""

from collections.abc import Callable
from dataclasses import dataclass

from musickit_api_mock.data.lookup import LookupContext, _lookup_source


@dataclass
class Genre:
    """Apple Music catalog genre."""

    name: str
    url: str
    parent_id: str | None = None
    parent_name: str | None = None


type GenresSource = dict[str, Genre] | Callable[[LookupContext], Genre | None] | None


class _GenreResolver:
    """Library-internal lookup over ``DataSources.genres``."""

    def __init__(self, get_source: Callable[[], GenresSource]) -> None:
        """Bind to the ``DataSources.genres`` source via a callback."""
        self._get_source = get_source

    def get(self, context: LookupContext) -> Genre | None:
        """Return the genre for ``context.id`` or ``None`` if absent."""
        return _lookup_source(self._get_source(), "data.genres", context)
