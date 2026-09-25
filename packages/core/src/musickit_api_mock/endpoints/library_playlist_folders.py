"""Handlers for the user's library playlist folder endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.data.library_playlist_folder import (
    _ROOT_ID,
    LibraryPlaylistFolder,
)
from musickit_api_mock.data.lookup import LookupContext
from musickit_api_mock.endpoints.pagination import (
    _LIBRARY_PLAYLIST_FOLDER_CHILDREN,
    _LIBRARY_PLAYLIST_FOLDER_PARENT,
    _LIBRARY_PLAYLIST_FOLDERS,
    _parse_inline_limits,
    _parse_validated_standalone_pagination,
    _standalone_paginated_response,
)
from musickit_api_mock.endpoints.query import _dedupe, _parse_csv_param, _parse_ids
from musickit_api_mock.endpoints.request_locale import _check_and_resolve_locale
from musickit_api_mock.endpoints.schema import (
    _batch_envelope,
    _counted_relationship_block,
    _empty_ids_400_envelope,
    _library_playlist_folder_href,
    _library_playlist_folder_ref,
    _library_playlist_folder_resource,
    _library_playlist_folder_root_resource,
    _library_playlist_resource,
    _no_related_resources_404_envelope,
    _resource_not_found_404_envelope,
)
from musickit_api_mock.transport.response_builders import _json_response

if TYPE_CHECKING:
    from musickit_api_mock.data.library_playlist_folder import (
        LibraryPlaylistFolderChild,
    )
    from musickit_api_mock.json_value import _JSONValue
    from musickit_api_mock.mock import MusicKitApiMock
    from musickit_api_mock.transport.http import Request, Response


def _resolve_folder_or_playlist(
    mock: MusicKitApiMock, item_id: str, locale: str | None
) -> LibraryPlaylistFolder | None:
    """Resolve an id on the folder resource paths.

    Apple also answers these paths for a library playlist id, returning a
    childless folder that carries the playlist's name and date.
    """
    resolver = mock._data_resolver
    folder = resolver.library_playlist_folder.get(LookupContext(item_id, locale))
    if folder is not None:
        return folder
    library_playlist = resolver.library_playlist.get(LookupContext(item_id, locale))
    if library_playlist is None:
        return None
    return LibraryPlaylistFolder(
        name=library_playlist.name, date_added=library_playlist.date_added
    )


def _children_of(
    mock: MusicKitApiMock, folder_id: str, locale: str | None
) -> list[LibraryPlaylistFolderChild] | None:
    resolver = mock._data_resolver.library_playlist_folder
    if folder_id == _ROOT_ID:
        return resolver.root_children()
    folder = resolver.get(LookupContext(folder_id, locale))
    if folder is None:
        return None
    return folder.children or []


def _parent_resource(
    mock: MusicKitApiMock, parent_id: str, locale: str | None, *, recursive: bool
) -> dict[str, _JSONValue]:
    rels: dict[str, _JSONValue] | None = None
    if recursive:
        rels = {
            "parent": _parent_block(
                mock,
                parent_id,
                f"{_library_playlist_folder_href(parent_id)}/parent",
                locale,
                recursive=True,
            )
        }
    if parent_id == _ROOT_ID:
        if rels is None:
            return _library_playlist_folder_ref(_ROOT_ID)
        return _library_playlist_folder_root_resource(rels)
    folder = mock._data_resolver.library_playlist_folder.get(
        LookupContext(parent_id, locale)
    )
    if folder is None:
        return _library_playlist_folder_ref(parent_id)
    return _library_playlist_folder_resource(parent_id, folder, relationships=rels)


def _parent_block(
    mock: MusicKitApiMock,
    child_id: str,
    href: str,
    locale: str | None,
    *,
    recursive: bool,
) -> dict[str, _JSONValue]:
    """Build ``relationships.parent`` for a folder or playlist.

    With ``recursive``, each emitted parent carries its own parent block up
    to the root, as Apple does on the children endpoint.
    """
    parent_id = mock._data_resolver.library_playlist_folder.parent_id(child_id, locale)
    if parent_id is None:
        return _counted_relationship_block(href, [], 0)
    return _counted_relationship_block(
        href, [_parent_resource(mock, parent_id, locale, recursive=recursive)], 1
    )


def _encode_child(
    mock: MusicKitApiMock,
    child: LibraryPlaylistFolderChild,
    locale: str | None,
    *,
    includes: set[str],
) -> dict[str, _JSONValue] | None:
    resolver = mock._data_resolver
    rels: dict[str, _JSONValue] = {}
    if child.type == "library-playlists":
        library_playlist = resolver.library_playlist.get(
            LookupContext(child.id, locale)
        )
        if library_playlist is None:
            return None
        href = f"/v1/me/library/playlists/{child.id}"
        # Apple emits the tracks block here with no data and a next offset of 0.
        if "tracks" in includes and library_playlist.track_ids is not None:
            rels["tracks"] = _counted_relationship_block(
                f"{href}/tracks", [], len(library_playlist.track_ids), next_offset=0
            )
        if "parent" in includes:
            rels["parent"] = _parent_block(
                mock, child.id, f"{href}/parent", locale, recursive=True
            )
        return _library_playlist_resource(
            child.id, library_playlist, relationships=rels or None
        )
    folder = resolver.library_playlist_folder.get(LookupContext(child.id, locale))
    if folder is None:
        return None
    if "parent" in includes:
        rels["parent"] = _parent_block(
            mock,
            child.id,
            f"{_library_playlist_folder_href(child.id)}/parent",
            locale,
            recursive=True,
        )
    return _library_playlist_folder_resource(
        child.id, folder, relationships=rels or None
    )


def _encode_children(
    mock: MusicKitApiMock,
    children: list[LibraryPlaylistFolderChild],
    locale: str | None,
    *,
    includes: set[str],
) -> list[dict[str, _JSONValue]]:
    out: list[dict[str, _JSONValue]] = []
    for child in children:
        encoded = _encode_child(mock, child, locale, includes=includes)
        if encoded is not None:
            out.append(encoded)
    return out


def _handle_library_playlist_folders(mock: MusicKitApiMock, req: Request) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=None, mock=mock)
    if err is not None:
        return err
    has_param, ids = _parse_ids(req.url)
    if has_param:
        if not ids:
            return _json_response(_empty_ids_400_envelope(), status=400)
        resources: list[dict[str, _JSONValue]] = []
        for folder_id in _dedupe(ids):
            folder = _resolve_folder_or_playlist(mock, folder_id, locale)
            if folder is not None:
                resources.append(_library_playlist_folder_resource(folder_id, folder))
        return _json_response(_batch_envelope(resources))
    limit, offset, err = _parse_validated_standalone_pagination(
        req, _LIBRARY_PLAYLIST_FOLDERS
    )
    if err is not None:
        return err
    resolver = mock._data_resolver.library_playlist_folder
    folder_ids = resolver.list_ids()
    data: list[dict[str, _JSONValue]] = []
    for folder_id in folder_ids[offset : offset + limit]:
        folder = resolver.get(LookupContext(folder_id, locale))
        if folder is not None:
            data.append(_library_playlist_folder_resource(folder_id, folder))
    return _standalone_paginated_response(
        "/v1/me/library/playlist-folders",
        data,
        len(folder_ids),
        offset=offset,
        limit=limit,
        include_meta_total=True,
    )


def _handle_library_playlist_folder(
    mock: MusicKitApiMock, req: Request, folder_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=None, mock=mock)
    if err is not None:
        return err
    includes = _parse_csv_param(req.url, "include")
    sizes, err = _parse_inline_limits(
        req, {"children": _LIBRARY_PLAYLIST_FOLDER_CHILDREN}
    )
    if err is not None:
        return err
    href = _library_playlist_folder_href(folder_id)
    folder: LibraryPlaylistFolder | None = None
    if folder_id != _ROOT_ID:
        folder = _resolve_folder_or_playlist(mock, folder_id, locale)
        if folder is None:
            return _json_response(_resource_not_found_404_envelope(), status=404)
    rels: dict[str, _JSONValue] = {}
    if "children" in includes:
        children = _children_of(mock, folder_id, locale) or []
        size = sizes["children"]
        rels["children"] = _counted_relationship_block(
            f"{href}/children",
            _encode_children(mock, children[:size], locale, includes=set()),
            len(children),
            next_offset=size if len(children) > size else None,
        )
    if "parent" in includes:
        rels["parent"] = _parent_block(
            mock, folder_id, f"{href}/parent", locale, recursive=False
        )
    if folder is None:
        # Apple answers the root only when a relationship is requested.
        if not rels:
            return _json_response(_resource_not_found_404_envelope(), status=404)
        return _json_response(
            _batch_envelope([_library_playlist_folder_root_resource(rels)])
        )
    return _json_response(
        _batch_envelope(
            [
                _library_playlist_folder_resource(
                    folder_id, folder, relationships=rels or None
                )
            ]
        )
    )


def _handle_library_playlist_folder_children(
    mock: MusicKitApiMock, req: Request, folder_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=None, mock=mock)
    if err is not None:
        return err
    limit, offset, err = _parse_validated_standalone_pagination(
        req, _LIBRARY_PLAYLIST_FOLDER_CHILDREN
    )
    if err is not None:
        return err
    children = _children_of(mock, folder_id, locale)
    if children is None or offset < 0 or offset >= len(children):
        return _json_response(
            _no_related_resources_404_envelope("children"), status=404
        )
    includes = _parse_csv_param(req.url, "include")
    return _standalone_paginated_response(
        f"{_library_playlist_folder_href(folder_id)}/children",
        _encode_children(
            mock, children[offset : offset + limit], locale, includes=includes
        ),
        len(children),
        offset=offset,
        limit=limit,
        include_meta_total=True,
    )


def _standalone_parent_response(
    mock: MusicKitApiMock, req: Request, child_id: str, href: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=None, mock=mock)
    if err is not None:
        return err
    limit, offset, err = _parse_validated_standalone_pagination(
        req, _LIBRARY_PLAYLIST_FOLDER_PARENT
    )
    if err is not None:
        return err
    parent_id = mock._data_resolver.library_playlist_folder.parent_id(child_id, locale)
    if parent_id is None:
        return _json_response(_no_related_resources_404_envelope("parent"), status=404)
    return _standalone_paginated_response(
        href,
        [_parent_resource(mock, parent_id, locale, recursive=False)],
        1,
        offset=offset,
        limit=limit,
        include_meta_total=True,
    )


def _handle_library_playlist_folder_parent(
    mock: MusicKitApiMock, req: Request, folder_id: str
) -> Response:
    return _standalone_parent_response(
        mock, req, folder_id, f"{_library_playlist_folder_href(folder_id)}/parent"
    )


def _handle_library_playlist_parent(
    mock: MusicKitApiMock, req: Request, library_playlist_id: str
) -> Response:
    return _standalone_parent_response(
        mock,
        req,
        library_playlist_id,
        f"/v1/me/library/playlists/{library_playlist_id}/parent",
    )
