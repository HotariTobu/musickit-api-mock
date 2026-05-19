"""Catalog record-label resource.

Catalog albums hold record-label id references on their own dataclass.
The label surfaces inline when the album emits
``relationships.record-labels`` (on ``?include=record-labels``) and as the
data of ``/v1/catalog/{sf}/albums/{id}/record-labels``.
"""

from collections.abc import Callable
from dataclasses import dataclass

from musickit_api_mock.data.lookup import LookupContext, _lookup_source
from musickit_api_mock.data.primitives.artwork import Artwork
from musickit_api_mock.data.primitives.description import Description


@dataclass
class RecordLabel:
    """Apple Music catalog record label."""

    name: str
    url: str
    artwork: Artwork | None = None
    description: Description | None = None


type RecordLabelsSource = (
    dict[str, RecordLabel] | Callable[[LookupContext], RecordLabel | None] | None
)


class _RecordLabelResolver:
    """Library-internal lookup over ``DataSources.record_labels``."""

    def __init__(self, get_source: Callable[[], RecordLabelsSource]) -> None:
        """Bind to the ``DataSources.record_labels`` source via a callback."""
        self._get_source = get_source

    def get(self, context: LookupContext) -> RecordLabel | None:
        """Return the record label for ``context.id`` or ``None`` if absent."""
        return _lookup_source(self._get_source(), "data.record_labels", context)
