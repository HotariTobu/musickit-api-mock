"""Handlers for the user's library playlist list, ``?ids=``, and single fetches.

These paths also answer for a playlist folder id, shaping the folder as an
empty playlist.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.data.library_playlist import LibraryPlaylist
from musickit_api_mock.data.library_playlist_folder import _ROOT_ID
from musickit_api_mock.data.lookup import LookupContext
from musickit_api_mock.endpoints.library import _user_storefront_slug
from musickit_api_mock.endpoints.library_playlist_folders import _parent_block
from musickit_api_mock.endpoints.pagination import (
    _LIBRARY_PLAYLIST_TRACKS,
    _LIBRARY_PLAYLISTS,
    _paginated_relationship_block,
    _parse_inline_limits,
    _parse_validated_standalone_pagination,
    _singleton_relationship_block,
    _standalone_paginated_response,
    _validate_offset,
)
from musickit_api_mock.endpoints.query import (
    _dedupe,
    _parse_csv_param,
    _parse_ids,
    _parse_query,
)
from musickit_api_mock.endpoints.request_locale import _check_and_resolve_locale
from musickit_api_mock.endpoints.schema import (
    _batch_envelope,
    _counted_relationship_block,
    _empty_ids_400_envelope,
    _library_playlist_folder_as_playlist_resource,
    _library_playlist_folder_ref,
    _library_playlist_placeholder_resource,
    _library_playlist_resource,
    _library_ref,
    _library_song_resource,
    _limit_not_supplied_400_envelope,
    _playlist_resource,
    _resource_not_found_404_envelope,
    _single_resource_include_400_envelope,
)
from musickit_api_mock.transport.response_builders import _json_response

if TYPE_CHECKING:
    from musickit_api_mock.data.library_playlist_folder import LibraryPlaylistFolder
    from musickit_api_mock.json_value import _JSONValue
    from musickit_api_mock.mock import MusicKitApiMock
    from musickit_api_mock.transport.http import Request, Response

_HREF = "/v1/me/library/playlists"

# ``None`` stands for the placeholder Apple returns for an unknown id.
type _Item = LibraryPlaylist | LibraryPlaylistFolder | None


def _resolve(mock: MusicKitApiMock, item_id: str, locale: str | None) -> _Item:
    resolver = mock._data_resolver
    context = LookupContext(item_id, locale)
    library_playlist = resolver.library_playlist.get(context)
    if library_playlist is not None:
        return library_playlist
    return resolver.library_playlist_folder.find(context)


def _encode(
    mock: MusicKitApiMock,
    item_id: str,
    item: _Item,
    *,
    locale: str | None,
    includes: set[str],
    sizes: dict[str, int],
) -> dict[str, _JSONValue]:
    resolver = mock._data_resolver
    href = f"{_HREF}/{item_id}"
    rels: dict[str, _JSONValue] = {}
    if "tracks" in includes:
        track_ids = item.track_ids if isinstance(item, LibraryPlaylist) else None
        tracks_block = _paginated_relationship_block(
            f"{href}/tracks",
            track_ids or [],
            sizes["tracks"],
            resolver=lambda sid: resolver.library_song.get(LookupContext(sid, locale)),
            encode=lambda sid, ls: _library_song_resource(sid, ls),
            fallback_ref=lambda sid: _library_ref("library-songs", sid),
            include_full=True,
            include_meta_total=True,
        )
        if tracks_block is not None:
            rels["tracks"] = tracks_block
    if "catalog" in includes:
        catalog_data: list[dict[str, _JSONValue]] = []
        if isinstance(item, LibraryPlaylist) and item.catalog_id is not None:
            catalog_playlist = resolver.playlist.get(
                LookupContext(item.catalog_id, locale)
            )
            if catalog_playlist is not None:
                catalog_data.append(
                    _playlist_resource(
                        _user_storefront_slug(mock), item.catalog_id, catalog_playlist
                    )
                )
        rels["catalog"] = _singleton_relationship_block(f"{href}/catalog", catalog_data)
    if "parent" in includes:
        if item is None:
            rels["parent"] = _counted_relationship_block(
                f"{href}/parent", [_library_playlist_folder_ref(_ROOT_ID)], 1
            )
        else:
            rels["parent"] = _parent_block(
                mock, item_id, f"{href}/parent", locale, recursive=False
            )
    relationships = rels or None
    if isinstance(item, LibraryPlaylist):
        return _library_playlist_resource(item_id, item, relationships=relationships)
    if item is None:
        return _library_playlist_placeholder_resource(
            item_id, relationships=relationships
        )
    return _library_playlist_folder_as_playlist_resource(
        item_id, item, relationships=relationships
    )


def _resolve_ids(
    mock: MusicKitApiMock, ids: list[str], locale: str | None
) -> list[tuple[str, _Item]]:
    """Resolve an ``?ids=`` fetch in request order.

    Once any id resolves, Apple answers every unknown ``p.`` id with a
    placeholder instead of dropping it.
    """
    resolved = [(item_id, _resolve(mock, item_id, locale)) for item_id in _dedupe(ids)]
    if all(item is None for _, item in resolved):
        return []
    return [
        (item_id, item)
        for item_id, item in resolved
        if item is not None or item_id.startswith("p.")
    ]


def _handle_library_playlists(mock: MusicKitApiMock, req: Request) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=None, mock=mock)
    if err is not None:
        return err
    includes = _parse_csv_param(req.url, "include")
    sizes, err = _parse_inline_limits(req, {"tracks": _LIBRARY_PLAYLIST_TRACKS})
    if err is not None:
        return err
    query = _parse_query(req.url)
    has_ids, ids = _parse_ids(req.url)
    total = 0
    limit = 0
    offset = 0
    if has_ids:
        if not ids:
            return _json_response(_empty_ids_400_envelope(), status=400)
        if "limit" in query:
            return _json_response(_limit_not_supplied_400_envelope(), status=400)
        page = _resolve_ids(mock, ids, locale)
    else:
        err = _validate_offset(req)
        if err is not None:
            return err
        limit, offset, err = _parse_validated_standalone_pagination(
            req, _LIBRARY_PLAYLISTS
        )
        if err is not None:
            return err
        resolver = mock._data_resolver.library_playlist
        playlist_ids = resolver.list_ids()
        total = len(playlist_ids)
        page = []
        for playlist_id in playlist_ids[offset : offset + limit]:
            library_playlist = resolver.get(LookupContext(playlist_id, locale))
            if library_playlist is not None:
                page.append((playlist_id, library_playlist))
    if "tracks" in includes and len(page) > 1:
        return _json_response(
            _single_resource_include_400_envelope("tracks"), status=400
        )
    data = [
        _encode(mock, item_id, item, locale=locale, includes=includes, sizes=sizes)
        for item_id, item in page
    ]
    if has_ids:
        return _json_response(_batch_envelope(data))
    return _standalone_paginated_response(
        _HREF,
        data,
        total,
        offset=offset,
        limit=limit,
        include_meta_total=True,
        language_tag=query.get("l", [None])[-1],
    )


def _handle_library_playlist(
    mock: MusicKitApiMock, req: Request, item_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=None, mock=mock)
    if err is not None:
        return err
    includes = _parse_csv_param(req.url, "include")
    sizes, err = _parse_inline_limits(req, {"tracks": _LIBRARY_PLAYLIST_TRACKS})
    if err is not None:
        return err
    item = _resolve(mock, item_id, locale)
    if item is None:
        return _json_response(_resource_not_found_404_envelope(), status=404)
    return _json_response(
        _batch_envelope(
            [
                _encode(
                    mock,
                    item_id,
                    item,
                    locale=locale,
                    includes=includes,
                    sizes=sizes,
                )
            ]
        )
    )
