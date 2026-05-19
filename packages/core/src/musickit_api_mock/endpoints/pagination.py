"""Pagination helpers shared by handlers.

Slice ownership lives on the handler side (not in schema builders): a request
context (``?offset=`` / ``?limit=`` for standalone endpoints, ``?limit[<rel>]=``
for inline relationships) determines how the resolved id list is sliced
before the schema builder shapes the response. Handlers also build the
``relationships`` block (with ``href`` / ``data`` / ``next``) and pass it
into the builder, so builders never reference the pagination caps.

Per-endpoint caps live in ``_PaginationConfig`` here so a single source
describes both inline and standalone pagination for one relationship.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from musickit_api_mock.endpoints.query import _parse_bracketed_param, _parse_query
from musickit_api_mock.endpoints.schema import (
    _limit_exceeded_envelope,
    _parameter_invalid_envelope,
)
from musickit_api_mock.transport.response_builders import _json_response

if TYPE_CHECKING:
    from collections.abc import Callable

    from musickit_api_mock.json_value import _JSONValue
    from musickit_api_mock.transport.http import Request, Response


@dataclass(frozen=True)
class _PaginationConfig:
    """Page size + limit cap for a paginated relationship.

    ``page_size`` is the default ``?limit=`` (and the default inline slice
    when the parent emits the relationship). ``max_limit`` is the cap that
    Apple's 400 envelope rejects beyond.
    """

    page_size: int
    max_limit: int


_ARTIST_ALBUMS = _PaginationConfig(page_size=25, max_limit=100)
_CATALOG_ALBUM_TRACKS = _PaginationConfig(page_size=300, max_limit=300)
_CATALOG_ALBUM_ARTISTS = _PaginationConfig(page_size=10, max_limit=10)
_CATALOG_PLAYLIST_TRACKS = _PaginationConfig(page_size=100, max_limit=300)
_CATALOG_MUSIC_VIDEO_ALBUMS = _PaginationConfig(page_size=10, max_limit=10)
_CATALOG_MUSIC_VIDEO_ARTISTS = _PaginationConfig(page_size=10, max_limit=10)
_CATALOG_SONG_ALBUMS = _PaginationConfig(page_size=10, max_limit=10)
_CATALOG_SONG_ARTISTS = _PaginationConfig(page_size=10, max_limit=10)
_CATALOG_SONG_COMPOSERS = _PaginationConfig(page_size=10, max_limit=10)

_LIBRARY_ALBUM_TRACKS = _PaginationConfig(page_size=300, max_limit=300)
_LIBRARY_ALBUM_ARTISTS = _PaginationConfig(page_size=10, max_limit=10)
_LIBRARY_PLAYLIST_TRACKS = _PaginationConfig(page_size=100, max_limit=100)
_LIBRARY_MUSIC_VIDEO_ALBUMS = _PaginationConfig(page_size=10, max_limit=10)
_LIBRARY_MUSIC_VIDEO_ARTISTS = _PaginationConfig(page_size=10, max_limit=10)
_LIBRARY_SONG_ALBUMS = _PaginationConfig(page_size=10, max_limit=10)
_LIBRARY_SONG_ARTISTS = _PaginationConfig(page_size=10, max_limit=10)
_LIBRARY_ARTIST_ALBUMS = _PaginationConfig(page_size=25, max_limit=100)

_CATALOG_SONG_GENRES = _PaginationConfig(page_size=10, max_limit=10)
_CATALOG_SONG_MUSIC_VIDEOS = _PaginationConfig(page_size=10, max_limit=10)
_CATALOG_ALBUM_GENRES = _PaginationConfig(page_size=10, max_limit=10)
_CATALOG_ALBUM_RECORD_LABELS = _PaginationConfig(page_size=10, max_limit=10)
_CATALOG_ARTIST_GENRES = _PaginationConfig(page_size=10, max_limit=10)
_CATALOG_ARTIST_MUSIC_VIDEOS = _PaginationConfig(page_size=25, max_limit=100)
_CATALOG_ARTIST_PLAYLISTS = _PaginationConfig(page_size=10, max_limit=10)
_CATALOG_MUSIC_VIDEO_GENRES = _PaginationConfig(page_size=10, max_limit=10)
_CATALOG_MUSIC_VIDEO_SONGS = _PaginationConfig(page_size=10, max_limit=10)
_CATALOG_CURATOR_PLAYLISTS = _PaginationConfig(page_size=10, max_limit=10)
_CATALOG_APPLE_CURATOR_PLAYLISTS = _PaginationConfig(page_size=10, max_limit=10)
_ME_RECOMMENDATION_CONTENTS = _PaginationConfig(page_size=10, max_limit=10)

# Inline page size for artist's ``relationships.albums`` block emitted by
# default from catalog endpoints that return artist resources (album.artists,
# song.artists, song.composers, music-video.artists). Differs from the
# standalone artist/<id>/albums default (25) — Apple emits 20 inline.
_INLINE_ARTIST_ALBUMS = 20


def _shallow_relationship_block(
    href: str,
    ids: list[str] | None,
    page_size: int,
    *,
    ref: Callable[[str], dict[str, _JSONValue]],
) -> dict[str, _JSONValue] | None:
    """Build a relationship block emitting shallow ``{id, type, href}`` refs only.

    Differs from the paginated relationship-block builder by skipping the
    resolve / full-encode path; used when the relationship is emitted
    without ``?include=`` and only needs shallow refs (e.g. the catalog
    artist-endpoint default ``relationships.albums``).
    """
    if ids is None:
        return None
    sliced = ids[:page_size]
    out: dict[str, _JSONValue] = {
        "href": href,
        "data": [ref(item_id) for item_id in sliced],
    }
    if len(ids) > page_size:
        out["next"] = f"{href}?offset={page_size}"
    return out


def _parse_standalone_pagination(
    req: Request, cfg: _PaginationConfig
) -> tuple[int, int, Response | None]:
    """Parse ``?limit=N&offset=N`` for a standalone relationship endpoint.

    Returns ``(limit, offset, err)``: ``err`` is a 400 ``Response`` when
    ``?limit=N`` exceeds ``cfg.max_limit``, else ``None``.
    """
    q = _parse_query(req.url)
    raw_limit = q.get("limit", [None])[-1]
    raw_offset = q.get("offset", [None])[-1]
    limit = cfg.page_size if raw_limit is None else int(raw_limit)
    offset = 0 if raw_offset is None else int(raw_offset)
    if limit > cfg.max_limit:
        return (
            0,
            0,
            _json_response(_limit_exceeded_envelope(cfg.max_limit, limit), status=400),
        )
    return limit, offset, None


def _parse_inline_limits(
    req: Request, rels: dict[str, _PaginationConfig]
) -> tuple[dict[str, int], Response | None]:
    """Parse ``?limit[<rel>]=N`` for inline relationships.

    Returns ``(sizes, err)``: ``sizes`` covers every entry in ``rels`` with
    ``cfg.page_size`` as the default; ``err`` is a 400 ``Response`` on the
    first invalid entry, else ``None``. Apple's error shape distinguishes:

    - non-integer / underflow (<1) → ``source.parameter = "limit[<rel>]"``
    - overflow (>max) → ``source.parameter = "limit"`` (handled via the
      limit-exceeded envelope builder)
    """
    raw_limits = _parse_bracketed_param(req.url, "limit")
    out: dict[str, int] = {}
    for rel, cfg in rels.items():
        raw = raw_limits.get(rel)
        if raw is None:
            out[rel] = cfg.page_size
            continue
        try:
            value = int(raw)
        except ValueError:
            return {}, _json_response(
                _parameter_invalid_envelope(
                    f"limit[{rel}]", "Value must be an integer"
                ),
                status=400,
            )
        if value < 1:
            return {}, _json_response(
                _parameter_invalid_envelope(
                    f"limit[{rel}]",
                    "Value must be an integer greater than or equal to 1",
                ),
                status=400,
            )
        if value > cfg.max_limit:
            return {}, _json_response(
                _limit_exceeded_envelope(cfg.max_limit, value), status=400
            )
        out[rel] = value
    return out, None


def _singleton_relationship_block(
    href: str,
    data: list[dict[str, _JSONValue]],
) -> dict[str, _JSONValue]:
    """Build a non-paginated relationship block with a single ``data`` slot.

    Used for relationships that don't paginate (e.g. ``playlist.curator``,
    ``library-song.catalog``). ``data`` is a list — empty when the linked
    resource is missing, otherwise a single-element list.
    """
    return {"href": href, "data": data}


def _paginated_relationship_block[T](
    href: str,
    ids: list[str] | None,
    page_size: int,
    *,
    resolver: Callable[[str], T | None],
    encode: Callable[[str, T], dict[str, _JSONValue]],
    fallback_ref: Callable[[str], dict[str, _JSONValue]],
    include_full: bool = False,
    include_meta_total: bool = False,
) -> dict[str, _JSONValue] | None:
    """Build an inline relationship block.

    Emits ``href`` / ``data`` / optional ``next`` / ``meta.total``. Slice
    happens here (size = ``page_size``); for each id either the ``encode``
    deep emit (when ``include_full`` and resolver returns the item) or
    ``fallback_ref`` (shallow ref dict) is used. Returns ``None`` when
    ``ids`` is ``None`` (relationship is absent for that resource).
    """
    if ids is None:
        return None
    sliced = ids[:page_size]
    data: list[dict[str, _JSONValue]] = []
    for item_id in sliced:
        if include_full:
            item = resolver(item_id)
            if item is not None:
                data.append(encode(item_id, item))
                continue
        data.append(fallback_ref(item_id))
    out: dict[str, _JSONValue] = {"href": href, "data": data}
    if include_meta_total:
        out["meta"] = {"total": len(ids)}
    if len(ids) > page_size:
        out["next"] = f"{href}?offset={page_size}"
    return out


def _standalone_paginated_response(
    href: str,
    items_data: list[dict[str, _JSONValue]],
    total: int,
    *,
    offset: int,
    limit: int,
    include_meta_total: bool = False,
) -> Response:
    """Wrap a standalone relationship-endpoint response.

    Emits ``data`` plus optional ``next`` / ``meta.total``.
    """
    body: dict[str, _JSONValue] = {"data": items_data}
    if include_meta_total:
        body["meta"] = {"total": total}
    if offset + limit < total:
        body["next"] = f"{href}?offset={offset + limit}"
    return _json_response(body)


def _slice_resolved[T](
    ids: list[str] | None,
    offset: int,
    limit: int,
    resolver: Callable[[str], T | None],
) -> list[tuple[str, T]]:
    """Slice ``ids[offset:offset+limit]`` then resolve each, dropping misses."""
    if ids is None:
        return []
    out: list[tuple[str, T]] = []
    for item_id in ids[offset : offset + limit]:
        item = resolver(item_id)
        if item is not None:
            out.append((item_id, item))
    return out
