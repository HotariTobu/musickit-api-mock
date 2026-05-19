"""Library artist resource."""

from collections.abc import Callable
from dataclasses import dataclass

from musickit_api_mock.data.lookup import LookupContext, _lookup_source


@dataclass
class LibraryArtist:
    """User-library artist."""

    name: str
    album_ids: list[str] | None = None
    catalog_id: str | None = None


type LibraryArtistsSource = (
    dict[str, LibraryArtist] | Callable[[LookupContext], LibraryArtist | None] | None
)


class _LibraryArtistResolver:
    """Library-internal lookup over ``DataSources.library_artists``."""

    def __init__(self, get_source: Callable[[], LibraryArtistsSource]) -> None:
        """Bind to the ``DataSources.library_artists`` source via a callback."""
        self._get_source = get_source

    def get(self, context: LookupContext) -> LibraryArtist | None:
        """Return the library artist for ``context.id`` or ``None`` if absent."""
        return _lookup_source(self._get_source(), "data.library_artists", context)
