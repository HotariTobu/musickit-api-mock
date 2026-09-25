"""Library playlist folder resource (``/v1/me/library/playlist-folders/{id}``).

A folder lists its direct children in library order. Children mix folders
and playlists, so each child entry carries its own type. The folder tree's
root (``p.playlistsroot``) has no name or date of its own, so its children
live in a separate source instead of a folder entry.
"""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Literal

from musickit_api_mock.data.lookup import (
    LookupContext,
    _list_source_ids,
    _lookup_source,
)

_ROOT_ID = "p.playlistsroot"

LibraryPlaylistFolderChildKind = Literal[
    "library-playlist-folders", "library-playlists"
]


@dataclass
class LibraryPlaylistFolderChild:
    """A single child reference within a playlist folder.

    Attributes:
        type: Resource type of the child.
        id: Library id of the child folder or playlist.
    """

    type: LibraryPlaylistFolderChildKind
    id: str


@dataclass
class LibraryPlaylistFolder:
    """User-library playlist folder.

    Attributes:
        name: Display name of the folder.
        date_added: ISO-8601 timestamp the folder was added to the library.
        last_modified_date: ISO-8601 timestamp of the last edit. Only the
            library playlist paths emit it, since they also answer for a
            folder id.
        children: Direct children in library order. ``None`` and an empty
            list both describe an empty folder.
    """

    name: str
    date_added: str | None = None
    last_modified_date: str | None = None
    children: list[LibraryPlaylistFolderChild] | None = None


type LibraryPlaylistFoldersSource = (
    Mapping[str, LibraryPlaylistFolder]
    | Callable[[LookupContext], LibraryPlaylistFolder | None]
    | None
)

type LibraryPlaylistRootChildrenSource = list[LibraryPlaylistFolderChild] | None


class _LibraryPlaylistFolderResolver:
    """Library-internal lookup over the playlist folder sources."""

    def __init__(
        self,
        get_source: Callable[[], LibraryPlaylistFoldersSource],
        get_root_children: Callable[[], LibraryPlaylistRootChildrenSource],
    ) -> None:
        """Bind to the folder and root-children sources via callbacks."""
        self._get_source = get_source
        self._get_root_children = get_root_children

    def get(self, context: LookupContext) -> LibraryPlaylistFolder | None:
        """Return the folder for ``context.id`` or ``None`` if absent."""
        return _lookup_source(
            self._get_source(), "data.library_playlist_folders", context
        )

    def find(self, context: LookupContext) -> LibraryPlaylistFolder | None:
        """Return the folder for ``context.id``, reading an unset source as no folders.

        Used where a folder is an optional alternative to another resource,
        so an unset folder source never turns a lookup miss into an error.
        """
        if self._get_source() is None:
            return None
        return self.get(context)

    def list_ids(self) -> list[str]:
        """Return every folder id; requires a mapping source."""
        return _list_source_ids(self._get_source(), "data.library_playlist_folders")

    def root_children(self) -> list[LibraryPlaylistFolderChild]:
        """Return the root's children or raise ``ValueError`` when unset."""
        children = self._get_root_children()
        if children is None:
            raise ValueError("data.library_playlist_root_children is not set")
        return children

    def parent_id(self, child_id: str, locale: str | None) -> str | None:
        """Return the id of the folder listing ``child_id``, or ``None``.

        The root id is returned for top-level children. Searching the tree
        needs every folder, so the folder source must be a mapping.
        """
        if any(c.id == child_id for c in self.root_children()):
            return _ROOT_ID
        for folder_id in self.list_ids():
            folder = self.get(LookupContext(folder_id, locale))
            if folder is not None and any(
                c.id == child_id for c in folder.children or []
            ):
                return folder_id
        return None
