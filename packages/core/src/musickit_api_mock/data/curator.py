"""Curator resource (catalog ``apple-curators`` / ``curators``).

Catalog playlists carry a ``relationships.curator`` ref Apple auto-emits in
the default response. The ref's ``type`` field is one of ``apple-curators``
(Apple's editorial team) or ``curators`` (third-party curators). Resolving
``?include=curator`` embeds full Curator attributes inline.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from musickit_api_mock.data.lookup import LookupContext, _lookup_source
from musickit_api_mock.data.primitives.artwork import Artwork


@dataclass
class Curator:
    """Apple Music catalog curator (``apple-curators`` or ``curators`` type).

    ``playlist_ids`` references the playlists the curator owns; emitted in
    ``relationships.playlists`` of the curator's singular endpoint and as
    the data of ``/v1/catalog/{sf}/{type}/{id}/playlists``. ``grouping_id``
    (apple-curators only) references the editorial grouping the curator
    belongs to; surfaces as ``relationships.grouping``.
    """

    name: str
    type: Literal["apple-curators", "curators"]
    url: str
    artwork: Artwork
    short_name: str | None = None
    kind: str | None = None
    playlist_ids: list[str] | None = None
    grouping_id: str | None = None


type CuratorsSource = (
    dict[str, Curator] | Callable[[LookupContext], Curator | None] | None
)


class _CuratorResolver:
    """Library-internal lookup over ``DataSources.curators``."""

    def __init__(self, get_source: Callable[[], CuratorsSource]) -> None:
        """Bind to the ``DataSources.curators`` source via a callback."""
        self._get_source = get_source

    def get(self, context: LookupContext) -> Curator | None:
        """Return the curator for ``context.id`` or ``None`` if absent."""
        return _lookup_source(self._get_source(), "data.curators", context)
