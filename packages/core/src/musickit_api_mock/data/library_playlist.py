"""Library playlist resource."""

from collections.abc import Callable
from dataclasses import dataclass

from musickit_api_mock.data.lookup import LookupContext, _lookup_source
from musickit_api_mock.data.primitives.artwork import Artwork


@dataclass
class LibraryPlaylist:
    """User-library playlist. ``track_ids`` refs library songs by id."""

    name: str
    can_delete: bool
    can_edit: bool
    is_public: bool
    has_catalog: bool
    has_collaboration: bool
    date_added: str | None = None
    last_modified_date: str | None = None
    track_ids: list[str] | None = None
    artwork: Artwork | None = None
    catalog_id: str | None = None


type LibraryPlaylistsSource = (
    dict[str, LibraryPlaylist]
    | Callable[[LookupContext], LibraryPlaylist | None]
    | None
)


class _LibraryPlaylistResolver:
    """Library-internal lookup over ``DataSources.library_playlists``."""

    def __init__(self, get_source: Callable[[], LibraryPlaylistsSource]) -> None:
        """Bind to the ``DataSources.library_playlists`` source via a callback."""
        self._get_source = get_source

    def get(self, context: LookupContext) -> LibraryPlaylist | None:
        """Return the library playlist for ``context.id`` or ``None`` if absent."""
        return _lookup_source(self._get_source(), "data.library_playlists", context)
