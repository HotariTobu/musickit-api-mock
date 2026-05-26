"""Catalog playlist resource."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

from musickit_api_mock.data.lookup import LookupContext, _lookup_source
from musickit_api_mock.data.primitives.artwork import Artwork
from musickit_api_mock.data.primitives.description import Description
from musickit_api_mock.data.primitives.editorial_notes import EditorialNotes


@dataclass
class Playlist:
    """Apple Music catalog playlist.

    Catalog playlists curated by Apple Music's editorial team carry the
    ``apple-curators`` curator type — that distinction lives on the curator
    resource, not here.

    Attributes:
        name: Display name of the playlist.
        playlist_type: Playlist category — one of ``user-shared``,
            ``editorial``, ``external``, or ``personal-mix``.
        curator_name: Display name of the curator.
        has_collaboration: Whether collaborative editing is enabled.
        is_chart: Whether the playlist is a chart playlist.
        audio_traits: Audio capability tags (lossless, dolby-atmos, etc.).
        supports_sing: Whether the playlist supports Apple Music Sing.
        url: Playlist landing-page URL on Apple Music.
        artwork: Cover artwork.
        last_modified: ISO-8601 timestamp of the last edit.
        track_ids: Catalog song ids in the playlist's track order.
        description: Long/short description text.
        editorial_notes: Editorial copy shown alongside the playlist.
        curator_id: Editorial or user curator id. When set, the mock emits
            a ``relationships.curator`` shallow ref matching Apple's default.
        library_playlist_id: Library playlist id when the playlist has a
            counterpart in the user's library.
    """

    name: str
    playlist_type: Literal["user-shared", "editorial", "external", "personal-mix"]
    curator_name: str
    has_collaboration: bool
    is_chart: bool
    audio_traits: list[str]
    supports_sing: bool
    url: str
    artwork: Artwork | None = None
    last_modified: str | None = None
    track_ids: list[str] | None = None
    description: Description | None = None
    editorial_notes: EditorialNotes | None = None
    curator_id: str | None = None
    library_playlist_id: str | None = None


type PlaylistsSource = (
    dict[str, Playlist] | Callable[[LookupContext], Playlist | None] | None
)


class _PlaylistResolver:
    """Library-internal lookup over ``DataSources.playlists``."""

    def __init__(self, get_source: Callable[[], PlaylistsSource]) -> None:
        """Bind to the ``DataSources.playlists`` source via a callback."""
        self._get_source = get_source

    def get(self, context: LookupContext) -> Playlist | None:
        """Return the playlist for ``context.id`` or ``None`` if absent."""
        return _lookup_source(self._get_source(), "data.playlists", context)
