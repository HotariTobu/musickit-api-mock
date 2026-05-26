"""Library playlist resource."""

from collections.abc import Callable
from dataclasses import dataclass

from musickit_api_mock.data.lookup import LookupContext, _lookup_source
from musickit_api_mock.data.primitives.artwork import Artwork


@dataclass
class LibraryPlaylist:
    """User-library playlist.

    Attributes:
        name: Display name of the playlist.
        can_delete: Whether the user can delete the playlist.
        can_edit: Whether the user can edit the playlist's tracks.
        is_public: Whether the playlist is shared publicly.
        has_catalog: Whether a corresponding catalog playlist exists.
        has_collaboration: Whether collaborative editing is enabled.
        date_added: ISO-8601 timestamp the playlist was added to the library.
        last_modified_date: ISO-8601 timestamp of the last edit.
        track_ids: Library song ids in the playlist's track order.
        artwork: Cover artwork.
        catalog_id: Catalog playlist id linking back to the catalog
            counterpart, used to resolve ``?include=catalog``.
    """

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
