"""Standalone relationship endpoints for catalog and library resources.

These back the ``next`` URL emitted in a parent resource's ``relationships``
block, and the public ``albumRelationship`` / ``playlistRelationship``
methods MusicKit JS exposes. They support ``?limit=N`` (capped per endpoint
with a 400 envelope on overflow), ``?offset=N`` (default 0), and
``?include=...`` (sub-relationships filter, where Apple supports it).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.data.lookup import LookupContext, _list_source_ids
from musickit_api_mock.endpoints.pagination import (
    _ARTIST_ALBUMS,
    _CATALOG_ALBUM_ARTISTS,
    _CATALOG_ALBUM_GENRES,
    _CATALOG_ALBUM_RECORD_LABELS,
    _CATALOG_ALBUM_TRACKS,
    _CATALOG_APPLE_CURATOR_PLAYLISTS,
    _CATALOG_ARTIST_GENRES,
    _CATALOG_ARTIST_MUSIC_VIDEOS,
    _CATALOG_ARTIST_PLAYLISTS,
    _CATALOG_CURATOR_PLAYLISTS,
    _CATALOG_MUSIC_VIDEO_ALBUMS,
    _CATALOG_MUSIC_VIDEO_ARTISTS,
    _CATALOG_MUSIC_VIDEO_GENRES,
    _CATALOG_MUSIC_VIDEO_SONGS,
    _CATALOG_PLAYLIST_TRACKS,
    _CATALOG_SONG_ALBUMS,
    _CATALOG_SONG_ARTISTS,
    _CATALOG_SONG_COMPOSERS,
    _CATALOG_SONG_GENRES,
    _CATALOG_SONG_MUSIC_VIDEOS,
    _INLINE_ARTIST_ALBUMS,
    _LIBRARY_ALBUM_ARTISTS,
    _LIBRARY_ALBUM_TRACKS,
    _LIBRARY_ARTIST_ALBUMS,
    _LIBRARY_MUSIC_VIDEO_ALBUMS,
    _LIBRARY_MUSIC_VIDEO_ARTISTS,
    _LIBRARY_PLAYLIST_TRACKS,
    _LIBRARY_SONG_ALBUMS,
    _LIBRARY_SONG_ARTISTS,
    _ME_RECOMMENDATION_CONTENTS,
    _paginated_relationship_block,
    _parse_standalone_pagination,
    _shallow_relationship_block,
    _slice_resolved,
    _standalone_paginated_response,
)
from musickit_api_mock.endpoints.query import _parse_csv_param
from musickit_api_mock.endpoints.request_locale import _check_and_resolve_locale
from musickit_api_mock.endpoints.schema import (
    _album_resource,
    _artist_resource,
    _catalog_ref,
    _curator_resource,
    _empty_ids_400_envelope,
    _genre_resource,
    _grouping_resource,
    _library_album_resource,
    _library_artist_resource,
    _library_music_video_resource,
    _library_playlist_resource,
    _library_ref,
    _library_song_resource,
    _music_video_resource,
    _playlist_resource,
    _record_label_resource,
    _resource_not_found_404_envelope,
    _song_resource,
    _station_resource,
)
from musickit_api_mock.transport.response_builders import _json_response

if TYPE_CHECKING:
    from musickit_api_mock.data.album import Album
    from musickit_api_mock.data.artist import Artist
    from musickit_api_mock.data.curator import Curator
    from musickit_api_mock.data.library_album import LibraryAlbum
    from musickit_api_mock.data.personal_recommendation import PersonalRecommendation
    from musickit_api_mock.data.song import Song
    from musickit_api_mock.json_value import _JSONValue
    from musickit_api_mock.mock import MusicKitApiMock
    from musickit_api_mock.surfaces.data import _DataResolver
    from musickit_api_mock.transport.http import Request, Response


def _build_artist_sub_rels(
    sf: str,
    artist_id: str,
    artist: Artist,
    *,
    locale: str | None,
    includes: set[str],
    resolver: _DataResolver,
) -> dict[str, _JSONValue]:
    """Build sub-rels for an artist resource.

    Apple emits default ``relationships.albums`` (shallow refs, 20 entries)
    for artists in any catalog endpoint that returns artist resources.
    ``?include=albums`` upgrades the same block to full album resources.
    """
    rels: dict[str, _JSONValue] = {}
    if "albums" in includes:
        block = _paginated_relationship_block(
            f"/v1/catalog/{sf}/artists/{artist_id}/albums",
            artist.album_ids,
            _INLINE_ARTIST_ALBUMS,
            resolver=lambda aid: resolver.album.get(LookupContext(aid, locale)),
            encode=lambda aid, al: _album_resource(sf, aid, al),
            fallback_ref=lambda aid: _catalog_ref(sf, "albums", aid),
            include_full=True,
        )
    else:
        block = _shallow_relationship_block(
            f"/v1/catalog/{sf}/artists/{artist_id}/albums",
            artist.album_ids,
            _INLINE_ARTIST_ALBUMS,
            ref=lambda aid: _catalog_ref(sf, "albums", aid),
        )
    if block is not None:
        rels["albums"] = block
    return rels


def _build_album_sub_rels(
    sf: str,
    album_id: str,
    album: Album,
    *,
    locale: str | None,
    includes: set[str],
    resolver: _DataResolver,
) -> dict[str, _JSONValue]:
    """Build sub-rels for an album: ``?include=tracks,artists``."""
    rels: dict[str, _JSONValue] = {}
    if "tracks" in includes:
        block = _paginated_relationship_block(
            f"/v1/catalog/{sf}/albums/{album_id}/tracks",
            album.track_ids,
            _CATALOG_ALBUM_TRACKS.page_size,
            resolver=lambda sid: resolver.song.get(LookupContext(sid, locale)),
            encode=lambda sid, sg: _song_resource(sf, sid, sg),
            fallback_ref=lambda sid: _catalog_ref(sf, "songs", sid),
            include_full=True,
        )
        if block is not None:
            rels["tracks"] = block
    if "artists" in includes:
        block = _paginated_relationship_block(
            f"/v1/catalog/{sf}/albums/{album_id}/artists",
            album.artist_ids,
            _CATALOG_ALBUM_ARTISTS.page_size,
            resolver=lambda aid: resolver.artist.get(LookupContext(aid, locale)),
            encode=lambda aid, ar: _artist_resource(sf, aid, ar),
            fallback_ref=lambda aid: _catalog_ref(sf, "artists", aid),
            include_full=True,
        )
        if block is not None:
            rels["artists"] = block
    return rels


def _build_song_sub_rels(
    sf: str,
    song_id: str,
    song: Song,
    *,
    locale: str | None,
    includes: set[str],
    resolver: _DataResolver,
) -> dict[str, _JSONValue]:
    """Build sub-rels for a song: ``?include=albums,artists,composers``."""
    rels: dict[str, _JSONValue] = {}
    if "albums" in includes:
        block = _paginated_relationship_block(
            f"/v1/catalog/{sf}/songs/{song_id}/albums",
            song.album_ids,
            _CATALOG_SONG_ALBUMS.page_size,
            resolver=lambda aid: resolver.album.get(LookupContext(aid, locale)),
            encode=lambda aid, al: _album_resource(sf, aid, al),
            fallback_ref=lambda aid: _catalog_ref(sf, "albums", aid),
            include_full=True,
        )
        if block is not None:
            rels["albums"] = block
    if "artists" in includes:
        block = _paginated_relationship_block(
            f"/v1/catalog/{sf}/songs/{song_id}/artists",
            song.artist_ids,
            _CATALOG_SONG_ARTISTS.page_size,
            resolver=lambda aid: resolver.artist.get(LookupContext(aid, locale)),
            encode=lambda aid, ar: _artist_resource(sf, aid, ar),
            fallback_ref=lambda aid: _catalog_ref(sf, "artists", aid),
            include_full=True,
        )
        if block is not None:
            rels["artists"] = block
    if "composers" in includes:
        block = _paginated_relationship_block(
            f"/v1/catalog/{sf}/songs/{song_id}/composers",
            song.composer_ids,
            _CATALOG_SONG_COMPOSERS.page_size,
            resolver=lambda aid: resolver.artist.get(LookupContext(aid, locale)),
            encode=lambda aid, ar: _artist_resource(sf, aid, ar),
            fallback_ref=lambda aid: _catalog_ref(sf, "artists", aid),
            include_full=True,
        )
        if block is not None:
            rels["composers"] = block
    return rels


def _build_library_album_sub_rels(
    library_album_id: str,
    library_album: LibraryAlbum,
    *,
    locale: str | None,
    includes: set[str],
    resolver: _DataResolver,
) -> dict[str, _JSONValue]:
    """Build sub-rels for a library album: ``?include=tracks,artists``."""
    rels: dict[str, _JSONValue] = {}
    if "tracks" in includes:
        block = _paginated_relationship_block(
            f"/v1/me/library/albums/{library_album_id}/tracks",
            library_album.track_ids,
            _LIBRARY_ALBUM_TRACKS.page_size,
            resolver=lambda sid: resolver.library_song.get(LookupContext(sid, locale)),
            encode=lambda sid, ls: _library_song_resource(sid, ls),
            fallback_ref=lambda sid: _library_ref("library-songs", sid),
            include_full=True,
        )
        if block is not None:
            rels["tracks"] = block
    if "artists" in includes:
        block = _paginated_relationship_block(
            f"/v1/me/library/albums/{library_album_id}/artists",
            library_album.artist_ids,
            _LIBRARY_ALBUM_ARTISTS.page_size,
            resolver=lambda aid: resolver.library_artist.get(
                LookupContext(aid, locale)
            ),
            encode=lambda aid, lar: _library_artist_resource(aid, lar),
            fallback_ref=lambda aid: _library_ref("library-artists", aid),
            include_full=True,
        )
        if block is not None:
            rels["artists"] = block
    return rels


def _handle_artist_albums(
    mock: MusicKitApiMock, req: Request, sf: str, artist_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    limit, offset, err = _parse_standalone_pagination(req, _ARTIST_ALBUMS)
    if err is not None:
        return err
    artist = mock._data_resolver.artist.get(LookupContext(artist_id, locale))
    if artist is None:
        return _json_response({"data": []})
    resolver = mock._data_resolver
    includes = _parse_csv_param(req.url, "include")
    items = _slice_resolved(
        artist.album_ids,
        offset,
        limit,
        lambda aid: resolver.album.get(LookupContext(aid, locale)),
    )
    data: list[dict[str, _JSONValue]] = []
    for aid, album in items:
        sub_rels = _build_album_sub_rels(
            sf, aid, album, locale=locale, includes=includes, resolver=resolver
        )
        data.append(_album_resource(sf, aid, album, relationships=sub_rels or None))
    total = 0 if artist.album_ids is None else len(artist.album_ids)
    return _standalone_paginated_response(
        f"/v1/catalog/{sf}/artists/{artist_id}/albums",
        data,
        total,
        offset=offset,
        limit=limit,
    )


def _handle_album_tracks(
    mock: MusicKitApiMock, req: Request, sf: str, album_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    limit, offset, err = _parse_standalone_pagination(req, _CATALOG_ALBUM_TRACKS)
    if err is not None:
        return err
    album = mock._data_resolver.album.get(LookupContext(album_id, locale))
    if album is None:
        return _json_response({"data": []})
    resolver = mock._data_resolver
    includes = _parse_csv_param(req.url, "include")
    items = _slice_resolved(
        album.track_ids,
        offset,
        limit,
        lambda sid: resolver.song.get(LookupContext(sid, locale)),
    )
    data: list[dict[str, _JSONValue]] = []
    for sid, song in items:
        sub_rels = _build_song_sub_rels(
            sf, sid, song, locale=locale, includes=includes, resolver=resolver
        )
        data.append(_song_resource(sf, sid, song, relationships=sub_rels or None))
    total = 0 if album.track_ids is None else len(album.track_ids)
    return _standalone_paginated_response(
        f"/v1/catalog/{sf}/albums/{album_id}/tracks",
        data,
        total,
        offset=offset,
        limit=limit,
    )


def _handle_album_artists(
    mock: MusicKitApiMock, req: Request, sf: str, album_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    limit, offset, err = _parse_standalone_pagination(req, _CATALOG_ALBUM_ARTISTS)
    if err is not None:
        return err
    album = mock._data_resolver.album.get(LookupContext(album_id, locale))
    if album is None:
        return _json_response({"data": []})
    resolver = mock._data_resolver
    includes = _parse_csv_param(req.url, "include")
    items = _slice_resolved(
        album.artist_ids,
        offset,
        limit,
        lambda aid: resolver.artist.get(LookupContext(aid, locale)),
    )
    data: list[dict[str, _JSONValue]] = []
    for aid, ar in items:
        sub_rels = _build_artist_sub_rels(
            sf, aid, ar, locale=locale, includes=includes, resolver=resolver
        )
        data.append(_artist_resource(sf, aid, ar, relationships=sub_rels or None))
    total = 0 if album.artist_ids is None else len(album.artist_ids)
    return _standalone_paginated_response(
        f"/v1/catalog/{sf}/albums/{album_id}/artists",
        data,
        total,
        offset=offset,
        limit=limit,
    )


def _handle_playlist_tracks(
    mock: MusicKitApiMock, req: Request, sf: str, playlist_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    limit, offset, err = _parse_standalone_pagination(req, _CATALOG_PLAYLIST_TRACKS)
    if err is not None:
        return err
    playlist = mock._data_resolver.playlist.get(LookupContext(playlist_id, locale))
    if playlist is None:
        return _json_response({"data": []})
    resolver = mock._data_resolver
    includes = _parse_csv_param(req.url, "include")
    items = _slice_resolved(
        playlist.track_ids,
        offset,
        limit,
        lambda sid: resolver.song.get(LookupContext(sid, locale)),
    )
    data: list[dict[str, _JSONValue]] = []
    for sid, song in items:
        sub_rels = _build_song_sub_rels(
            sf, sid, song, locale=locale, includes=includes, resolver=resolver
        )
        data.append(_song_resource(sf, sid, song, relationships=sub_rels or None))
    total = 0 if playlist.track_ids is None else len(playlist.track_ids)
    return _standalone_paginated_response(
        f"/v1/catalog/{sf}/playlists/{playlist_id}/tracks",
        data,
        total,
        offset=offset,
        limit=limit,
    )


def _handle_music_video_albums(
    mock: MusicKitApiMock, req: Request, sf: str, music_video_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    limit, offset, err = _parse_standalone_pagination(req, _CATALOG_MUSIC_VIDEO_ALBUMS)
    if err is not None:
        return err
    music_video = mock._data_resolver.music_video.get(
        LookupContext(music_video_id, locale)
    )
    if music_video is None:
        return _json_response({"data": []})
    resolver = mock._data_resolver
    includes = _parse_csv_param(req.url, "include")
    items = _slice_resolved(
        music_video.album_ids,
        offset,
        limit,
        lambda aid: resolver.album.get(LookupContext(aid, locale)),
    )
    data: list[dict[str, _JSONValue]] = []
    for aid, al in items:
        sub_rels = _build_album_sub_rels(
            sf, aid, al, locale=locale, includes=includes, resolver=resolver
        )
        data.append(_album_resource(sf, aid, al, relationships=sub_rels or None))
    total = 0 if music_video.album_ids is None else len(music_video.album_ids)
    return _standalone_paginated_response(
        f"/v1/catalog/{sf}/music-videos/{music_video_id}/albums",
        data,
        total,
        offset=offset,
        limit=limit,
    )


def _handle_music_video_artists(
    mock: MusicKitApiMock, req: Request, sf: str, music_video_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    limit, offset, err = _parse_standalone_pagination(req, _CATALOG_MUSIC_VIDEO_ARTISTS)
    if err is not None:
        return err
    music_video = mock._data_resolver.music_video.get(
        LookupContext(music_video_id, locale)
    )
    if music_video is None:
        return _json_response({"data": []})
    resolver = mock._data_resolver
    includes = _parse_csv_param(req.url, "include")
    items = _slice_resolved(
        music_video.artist_ids,
        offset,
        limit,
        lambda aid: resolver.artist.get(LookupContext(aid, locale)),
    )
    data: list[dict[str, _JSONValue]] = []
    for aid, ar in items:
        sub_rels = _build_artist_sub_rels(
            sf, aid, ar, locale=locale, includes=includes, resolver=resolver
        )
        data.append(_artist_resource(sf, aid, ar, relationships=sub_rels or None))
    total = 0 if music_video.artist_ids is None else len(music_video.artist_ids)
    return _standalone_paginated_response(
        f"/v1/catalog/{sf}/music-videos/{music_video_id}/artists",
        data,
        total,
        offset=offset,
        limit=limit,
    )


def _handle_song_albums(
    mock: MusicKitApiMock, req: Request, sf: str, song_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    limit, offset, err = _parse_standalone_pagination(req, _CATALOG_SONG_ALBUMS)
    if err is not None:
        return err
    song = mock._data_resolver.song.get(LookupContext(song_id, locale))
    if song is None:
        return _json_response({"data": []})
    resolver = mock._data_resolver
    includes = _parse_csv_param(req.url, "include")
    items = _slice_resolved(
        song.album_ids,
        offset,
        limit,
        lambda aid: resolver.album.get(LookupContext(aid, locale)),
    )
    data: list[dict[str, _JSONValue]] = []
    for aid, al in items:
        sub_rels = _build_album_sub_rels(
            sf, aid, al, locale=locale, includes=includes, resolver=resolver
        )
        data.append(_album_resource(sf, aid, al, relationships=sub_rels or None))
    total = 0 if song.album_ids is None else len(song.album_ids)
    return _standalone_paginated_response(
        f"/v1/catalog/{sf}/songs/{song_id}/albums",
        data,
        total,
        offset=offset,
        limit=limit,
    )


def _handle_song_artists(
    mock: MusicKitApiMock, req: Request, sf: str, song_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    limit, offset, err = _parse_standalone_pagination(req, _CATALOG_SONG_ARTISTS)
    if err is not None:
        return err
    song = mock._data_resolver.song.get(LookupContext(song_id, locale))
    if song is None:
        return _json_response({"data": []})
    resolver = mock._data_resolver
    includes = _parse_csv_param(req.url, "include")
    items = _slice_resolved(
        song.artist_ids,
        offset,
        limit,
        lambda aid: resolver.artist.get(LookupContext(aid, locale)),
    )
    data: list[dict[str, _JSONValue]] = []
    for aid, ar in items:
        sub_rels = _build_artist_sub_rels(
            sf, aid, ar, locale=locale, includes=includes, resolver=resolver
        )
        data.append(_artist_resource(sf, aid, ar, relationships=sub_rels or None))
    total = 0 if song.artist_ids is None else len(song.artist_ids)
    return _standalone_paginated_response(
        f"/v1/catalog/{sf}/songs/{song_id}/artists",
        data,
        total,
        offset=offset,
        limit=limit,
    )


def _handle_song_composers(
    mock: MusicKitApiMock, req: Request, sf: str, song_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    limit, offset, err = _parse_standalone_pagination(req, _CATALOG_SONG_COMPOSERS)
    if err is not None:
        return err
    song = mock._data_resolver.song.get(LookupContext(song_id, locale))
    if song is None:
        return _json_response({"data": []})
    resolver = mock._data_resolver
    includes = _parse_csv_param(req.url, "include")
    items = _slice_resolved(
        song.composer_ids,
        offset,
        limit,
        lambda aid: resolver.artist.get(LookupContext(aid, locale)),
    )
    data: list[dict[str, _JSONValue]] = []
    for aid, ar in items:
        sub_rels = _build_artist_sub_rels(
            sf, aid, ar, locale=locale, includes=includes, resolver=resolver
        )
        data.append(_artist_resource(sf, aid, ar, relationships=sub_rels or None))
    total = 0 if song.composer_ids is None else len(song.composer_ids)
    return _standalone_paginated_response(
        f"/v1/catalog/{sf}/songs/{song_id}/composers",
        data,
        total,
        offset=offset,
        limit=limit,
    )


def _handle_library_album_tracks(
    mock: MusicKitApiMock, req: Request, library_album_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=None, mock=mock)
    if err is not None:
        return err
    limit, offset, err = _parse_standalone_pagination(req, _LIBRARY_ALBUM_TRACKS)
    if err is not None:
        return err
    library_album = mock._data_resolver.library_album.get(
        LookupContext(library_album_id, locale)
    )
    if library_album is None:
        return _json_response({"data": []})
    resolver = mock._data_resolver
    items = _slice_resolved(
        library_album.track_ids,
        offset,
        limit,
        lambda sid: resolver.library_song.get(LookupContext(sid, locale)),
    )
    data = [_library_song_resource(sid, ls) for sid, ls in items]
    total = 0 if library_album.track_ids is None else len(library_album.track_ids)
    return _standalone_paginated_response(
        f"/v1/me/library/albums/{library_album_id}/tracks",
        data,
        total,
        offset=offset,
        limit=limit,
        include_meta_total=True,
    )


def _handle_library_album_artists(
    mock: MusicKitApiMock, req: Request, library_album_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=None, mock=mock)
    if err is not None:
        return err
    limit, offset, err = _parse_standalone_pagination(req, _LIBRARY_ALBUM_ARTISTS)
    if err is not None:
        return err
    library_album = mock._data_resolver.library_album.get(
        LookupContext(library_album_id, locale)
    )
    if library_album is None:
        return _json_response({"data": []})
    resolver = mock._data_resolver
    items = _slice_resolved(
        library_album.artist_ids,
        offset,
        limit,
        lambda aid: resolver.library_artist.get(LookupContext(aid, locale)),
    )
    data = [_library_artist_resource(aid, lar) for aid, lar in items]
    total = 0 if library_album.artist_ids is None else len(library_album.artist_ids)
    return _standalone_paginated_response(
        f"/v1/me/library/albums/{library_album_id}/artists",
        data,
        total,
        offset=offset,
        limit=limit,
    )


def _handle_library_playlist_tracks(
    mock: MusicKitApiMock, req: Request, library_playlist_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=None, mock=mock)
    if err is not None:
        return err
    limit, offset, err = _parse_standalone_pagination(req, _LIBRARY_PLAYLIST_TRACKS)
    if err is not None:
        return err
    library_playlist = mock._data_resolver.library_playlist.get(
        LookupContext(library_playlist_id, locale)
    )
    if library_playlist is None:
        return _json_response({"data": []})
    resolver = mock._data_resolver
    items = _slice_resolved(
        library_playlist.track_ids,
        offset,
        limit,
        lambda sid: resolver.library_song.get(LookupContext(sid, locale)),
    )
    data = [_library_song_resource(sid, ls) for sid, ls in items]
    total = 0 if library_playlist.track_ids is None else len(library_playlist.track_ids)
    return _standalone_paginated_response(
        f"/v1/me/library/playlists/{library_playlist_id}/tracks",
        data,
        total,
        offset=offset,
        limit=limit,
        include_meta_total=True,
    )


def _handle_library_music_video_albums(
    mock: MusicKitApiMock, req: Request, library_music_video_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=None, mock=mock)
    if err is not None:
        return err
    limit, offset, err = _parse_standalone_pagination(req, _LIBRARY_MUSIC_VIDEO_ALBUMS)
    if err is not None:
        return err
    library_music_video = mock._data_resolver.library_music_video.get(
        LookupContext(library_music_video_id, locale)
    )
    if library_music_video is None:
        return _json_response({"data": []})
    resolver = mock._data_resolver
    includes = _parse_csv_param(req.url, "include")
    items = _slice_resolved(
        library_music_video.album_ids,
        offset,
        limit,
        lambda aid: resolver.library_album.get(LookupContext(aid, locale)),
    )
    data: list[dict[str, _JSONValue]] = []
    for aid, la in items:
        sub_rels = _build_library_album_sub_rels(
            aid, la, locale=locale, includes=includes, resolver=resolver
        )
        data.append(_library_album_resource(aid, la, relationships=sub_rels or None))
    total = (
        0
        if library_music_video.album_ids is None
        else len(library_music_video.album_ids)
    )
    return _standalone_paginated_response(
        f"/v1/me/library/music-videos/{library_music_video_id}/albums",
        data,
        total,
        offset=offset,
        limit=limit,
    )


def _handle_library_music_video_artists(
    mock: MusicKitApiMock, req: Request, library_music_video_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=None, mock=mock)
    if err is not None:
        return err
    limit, offset, err = _parse_standalone_pagination(req, _LIBRARY_MUSIC_VIDEO_ARTISTS)
    if err is not None:
        return err
    library_music_video = mock._data_resolver.library_music_video.get(
        LookupContext(library_music_video_id, locale)
    )
    if library_music_video is None:
        return _json_response({"data": []})
    resolver = mock._data_resolver
    items = _slice_resolved(
        library_music_video.artist_ids,
        offset,
        limit,
        lambda aid: resolver.library_artist.get(LookupContext(aid, locale)),
    )
    data = [_library_artist_resource(aid, lar) for aid, lar in items]
    total = (
        0
        if library_music_video.artist_ids is None
        else len(library_music_video.artist_ids)
    )
    return _standalone_paginated_response(
        f"/v1/me/library/music-videos/{library_music_video_id}/artists",
        data,
        total,
        offset=offset,
        limit=limit,
    )


def _handle_song_library(
    mock: MusicKitApiMock, req: Request, sf: str, song_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    song = mock._data_resolver.song.get(LookupContext(song_id, locale))
    if song is None or song.library_song_id is None:
        return _json_response({"data": []})
    library_song = mock._data_resolver.library_song.get(
        LookupContext(song.library_song_id, locale)
    )
    if library_song is None:
        return _json_response({"data": []})
    return _json_response(
        {"data": [_library_song_resource(song.library_song_id, library_song)]}
    )


def _handle_album_library(
    mock: MusicKitApiMock, req: Request, sf: str, album_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    album = mock._data_resolver.album.get(LookupContext(album_id, locale))
    if album is None or album.library_album_id is None:
        return _json_response({"data": []})
    library_album = mock._data_resolver.library_album.get(
        LookupContext(album.library_album_id, locale)
    )
    if library_album is None:
        return _json_response({"data": []})
    return _json_response(
        {"data": [_library_album_resource(album.library_album_id, library_album)]}
    )


def _handle_music_video_library(
    mock: MusicKitApiMock, req: Request, sf: str, music_video_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    music_video = mock._data_resolver.music_video.get(
        LookupContext(music_video_id, locale)
    )
    if music_video is None or music_video.library_music_video_id is None:
        return _json_response({"data": []})
    library_music_video = mock._data_resolver.library_music_video.get(
        LookupContext(music_video.library_music_video_id, locale)
    )
    if library_music_video is None:
        return _json_response({"data": []})
    return _json_response(
        {
            "data": [
                _library_music_video_resource(
                    music_video.library_music_video_id, library_music_video
                )
            ]
        }
    )


def _handle_playlist_library(
    mock: MusicKitApiMock, req: Request, sf: str, playlist_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    playlist = mock._data_resolver.playlist.get(LookupContext(playlist_id, locale))
    if playlist is None or playlist.library_playlist_id is None:
        return _json_response({"data": []})
    library_playlist = mock._data_resolver.library_playlist.get(
        LookupContext(playlist.library_playlist_id, locale)
    )
    if library_playlist is None:
        return _json_response({"data": []})
    return _json_response(
        {
            "data": [
                _library_playlist_resource(
                    playlist.library_playlist_id, library_playlist
                )
            ]
        }
    )


def _handle_library_song_albums(
    mock: MusicKitApiMock, req: Request, library_song_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=None, mock=mock)
    if err is not None:
        return err
    limit, offset, err = _parse_standalone_pagination(req, _LIBRARY_SONG_ALBUMS)
    if err is not None:
        return err
    library_song = mock._data_resolver.library_song.get(
        LookupContext(library_song_id, locale)
    )
    if library_song is None:
        return _json_response({"data": []})
    resolver = mock._data_resolver
    items = _slice_resolved(
        library_song.album_ids,
        offset,
        limit,
        lambda aid: resolver.library_album.get(LookupContext(aid, locale)),
    )
    data = [_library_album_resource(aid, la) for aid, la in items]
    total = 0 if library_song.album_ids is None else len(library_song.album_ids)
    return _standalone_paginated_response(
        f"/v1/me/library/songs/{library_song_id}/albums",
        data,
        total,
        offset=offset,
        limit=limit,
    )


def _handle_library_song_artists(
    mock: MusicKitApiMock, req: Request, library_song_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=None, mock=mock)
    if err is not None:
        return err
    limit, offset, err = _parse_standalone_pagination(req, _LIBRARY_SONG_ARTISTS)
    if err is not None:
        return err
    library_song = mock._data_resolver.library_song.get(
        LookupContext(library_song_id, locale)
    )
    if library_song is None:
        return _json_response({"data": []})
    resolver = mock._data_resolver
    items = _slice_resolved(
        library_song.artist_ids,
        offset,
        limit,
        lambda aid: resolver.library_artist.get(LookupContext(aid, locale)),
    )
    data = [_library_artist_resource(aid, lar) for aid, lar in items]
    total = 0 if library_song.artist_ids is None else len(library_song.artist_ids)
    return _standalone_paginated_response(
        f"/v1/me/library/songs/{library_song_id}/artists",
        data,
        total,
        offset=offset,
        limit=limit,
    )


def _handle_library_artist_albums(
    mock: MusicKitApiMock, req: Request, library_artist_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=None, mock=mock)
    if err is not None:
        return err
    limit, offset, err = _parse_standalone_pagination(req, _LIBRARY_ARTIST_ALBUMS)
    if err is not None:
        return err
    library_artist = mock._data_resolver.library_artist.get(
        LookupContext(library_artist_id, locale)
    )
    if library_artist is None:
        return _json_response({"data": []})
    resolver = mock._data_resolver
    items = _slice_resolved(
        library_artist.album_ids,
        offset,
        limit,
        lambda aid: resolver.library_album.get(LookupContext(aid, locale)),
    )
    data = [_library_album_resource(aid, la) for aid, la in items]
    total = 0 if library_artist.album_ids is None else len(library_artist.album_ids)
    return _standalone_paginated_response(
        f"/v1/me/library/artists/{library_artist_id}/albums",
        data,
        total,
        offset=offset,
        limit=limit,
    )


def _handle_library_song_catalog(
    mock: MusicKitApiMock, req: Request, library_song_id: str
) -> Response:
    from musickit_api_mock.endpoints.library import _user_storefront_slug

    locale, err = _check_and_resolve_locale(req, storefront_slug=None, mock=mock)
    if err is not None:
        return err
    library_song = mock._data_resolver.library_song.get(
        LookupContext(library_song_id, locale)
    )
    if library_song is None or library_song.catalog_id is None:
        return _json_response({"data": []})
    catalog_song = mock._data_resolver.song.get(
        LookupContext(library_song.catalog_id, locale)
    )
    if catalog_song is None:
        return _json_response({"data": []})
    sf = _user_storefront_slug(mock)
    return _json_response(
        {"data": [_song_resource(sf, library_song.catalog_id, catalog_song)]}
    )


def _handle_library_album_catalog(
    mock: MusicKitApiMock, req: Request, library_album_id: str
) -> Response:
    from musickit_api_mock.endpoints.library import _user_storefront_slug

    locale, err = _check_and_resolve_locale(req, storefront_slug=None, mock=mock)
    if err is not None:
        return err
    library_album = mock._data_resolver.library_album.get(
        LookupContext(library_album_id, locale)
    )
    if library_album is None or library_album.catalog_id is None:
        return _json_response({"data": []})
    catalog_album = mock._data_resolver.album.get(
        LookupContext(library_album.catalog_id, locale)
    )
    if catalog_album is None:
        return _json_response({"data": []})
    sf = _user_storefront_slug(mock)
    return _json_response(
        {"data": [_album_resource(sf, library_album.catalog_id, catalog_album)]}
    )


def _handle_library_music_video_catalog(
    mock: MusicKitApiMock, req: Request, library_music_video_id: str
) -> Response:
    from musickit_api_mock.endpoints.library import _user_storefront_slug

    locale, err = _check_and_resolve_locale(req, storefront_slug=None, mock=mock)
    if err is not None:
        return err
    library_music_video = mock._data_resolver.library_music_video.get(
        LookupContext(library_music_video_id, locale)
    )
    if library_music_video is None or library_music_video.catalog_id is None:
        return _json_response({"data": []})
    catalog_music_video = mock._data_resolver.music_video.get(
        LookupContext(library_music_video.catalog_id, locale)
    )
    if catalog_music_video is None:
        return _json_response({"data": []})
    sf = _user_storefront_slug(mock)
    return _json_response(
        {
            "data": [
                _music_video_resource(
                    sf, library_music_video.catalog_id, catalog_music_video
                )
            ]
        }
    )


def _handle_library_playlist_catalog(
    mock: MusicKitApiMock, req: Request, library_playlist_id: str
) -> Response:
    from musickit_api_mock.endpoints.library import _user_storefront_slug

    locale, err = _check_and_resolve_locale(req, storefront_slug=None, mock=mock)
    if err is not None:
        return err
    library_playlist = mock._data_resolver.library_playlist.get(
        LookupContext(library_playlist_id, locale)
    )
    if library_playlist is None or library_playlist.catalog_id is None:
        return _json_response({"data": []})
    catalog_playlist = mock._data_resolver.playlist.get(
        LookupContext(library_playlist.catalog_id, locale)
    )
    if catalog_playlist is None:
        return _json_response({"data": []})
    sf = _user_storefront_slug(mock)
    return _json_response(
        {
            "data": [
                _playlist_resource(sf, library_playlist.catalog_id, catalog_playlist)
            ]
        }
    )


def _handle_library_artist_catalog(
    mock: MusicKitApiMock, req: Request, library_artist_id: str
) -> Response:
    from musickit_api_mock.endpoints.library import _user_storefront_slug

    locale, err = _check_and_resolve_locale(req, storefront_slug=None, mock=mock)
    if err is not None:
        return err
    library_artist = mock._data_resolver.library_artist.get(
        LookupContext(library_artist_id, locale)
    )
    if library_artist is None or library_artist.catalog_id is None:
        return _json_response({"data": []})
    catalog_artist = mock._data_resolver.artist.get(
        LookupContext(library_artist.catalog_id, locale)
    )
    if catalog_artist is None:
        return _json_response({"data": []})
    sf = _user_storefront_slug(mock)
    return _json_response(
        {"data": [_artist_resource(sf, library_artist.catalog_id, catalog_artist)]}
    )


def _handle_song_genres(
    mock: MusicKitApiMock, req: Request, sf: str, song_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    limit, offset, err = _parse_standalone_pagination(req, _CATALOG_SONG_GENRES)
    if err is not None:
        return err
    song = mock._data_resolver.song.get(LookupContext(song_id, locale))
    if song is None:
        return _json_response({"data": []})
    resolver = mock._data_resolver
    items = _slice_resolved(
        song.genre_ids,
        offset,
        limit,
        lambda gid: resolver.genre.get(LookupContext(gid, locale)),
    )
    data = [_genre_resource(sf, gid, g) for gid, g in items]
    total = 0 if song.genre_ids is None else len(song.genre_ids)
    return _standalone_paginated_response(
        f"/v1/catalog/{sf}/songs/{song_id}/genres",
        data,
        total,
        offset=offset,
        limit=limit,
    )


def _handle_song_station(
    mock: MusicKitApiMock, req: Request, sf: str, song_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    song = mock._data_resolver.song.get(LookupContext(song_id, locale))
    if song is None or song.station_id is None:
        return _json_response({"data": []})
    station = mock._data_resolver.station.get(LookupContext(song.station_id, locale))
    if station is None:
        return _json_response({"data": []})
    return _json_response({"data": [_station_resource(sf, song.station_id, station)]})


def _handle_song_music_videos(
    mock: MusicKitApiMock, req: Request, sf: str, song_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    limit, offset, err = _parse_standalone_pagination(req, _CATALOG_SONG_MUSIC_VIDEOS)
    if err is not None:
        return err
    song = mock._data_resolver.song.get(LookupContext(song_id, locale))
    if song is None:
        return _json_response({"data": []})
    resolver = mock._data_resolver
    items = _slice_resolved(
        song.music_video_ids,
        offset,
        limit,
        lambda mvid: resolver.music_video.get(LookupContext(mvid, locale)),
    )
    data = [_music_video_resource(sf, mvid, mv) for mvid, mv in items]
    total = 0 if song.music_video_ids is None else len(song.music_video_ids)
    return _standalone_paginated_response(
        f"/v1/catalog/{sf}/songs/{song_id}/music-videos",
        data,
        total,
        offset=offset,
        limit=limit,
    )


def _handle_album_genres(
    mock: MusicKitApiMock, req: Request, sf: str, album_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    limit, offset, err = _parse_standalone_pagination(req, _CATALOG_ALBUM_GENRES)
    if err is not None:
        return err
    album = mock._data_resolver.album.get(LookupContext(album_id, locale))
    if album is None:
        return _json_response({"data": []})
    resolver = mock._data_resolver
    items = _slice_resolved(
        album.genre_ids,
        offset,
        limit,
        lambda gid: resolver.genre.get(LookupContext(gid, locale)),
    )
    data = [_genre_resource(sf, gid, g) for gid, g in items]
    total = 0 if album.genre_ids is None else len(album.genre_ids)
    return _standalone_paginated_response(
        f"/v1/catalog/{sf}/albums/{album_id}/genres",
        data,
        total,
        offset=offset,
        limit=limit,
    )


def _handle_album_record_labels(
    mock: MusicKitApiMock, req: Request, sf: str, album_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    limit, offset, err = _parse_standalone_pagination(req, _CATALOG_ALBUM_RECORD_LABELS)
    if err is not None:
        return err
    album = mock._data_resolver.album.get(LookupContext(album_id, locale))
    if album is None:
        return _json_response({"data": []})
    resolver = mock._data_resolver
    items = _slice_resolved(
        album.record_label_ids,
        offset,
        limit,
        lambda rid: resolver.record_label.get(LookupContext(rid, locale)),
    )
    data = [_record_label_resource(sf, rid, rl) for rid, rl in items]
    total = 0 if album.record_label_ids is None else len(album.record_label_ids)
    return _standalone_paginated_response(
        f"/v1/catalog/{sf}/albums/{album_id}/record-labels",
        data,
        total,
        offset=offset,
        limit=limit,
    )


def _handle_artist_genres(
    mock: MusicKitApiMock, req: Request, sf: str, artist_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    limit, offset, err = _parse_standalone_pagination(req, _CATALOG_ARTIST_GENRES)
    if err is not None:
        return err
    artist = mock._data_resolver.artist.get(LookupContext(artist_id, locale))
    if artist is None:
        return _json_response({"data": []})
    resolver = mock._data_resolver
    items = _slice_resolved(
        artist.genre_ids,
        offset,
        limit,
        lambda gid: resolver.genre.get(LookupContext(gid, locale)),
    )
    data = [_genre_resource(sf, gid, g) for gid, g in items]
    total = 0 if artist.genre_ids is None else len(artist.genre_ids)
    return _standalone_paginated_response(
        f"/v1/catalog/{sf}/artists/{artist_id}/genres",
        data,
        total,
        offset=offset,
        limit=limit,
    )


def _handle_artist_music_videos(
    mock: MusicKitApiMock, req: Request, sf: str, artist_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    limit, offset, err = _parse_standalone_pagination(req, _CATALOG_ARTIST_MUSIC_VIDEOS)
    if err is not None:
        return err
    artist = mock._data_resolver.artist.get(LookupContext(artist_id, locale))
    if artist is None:
        return _json_response({"data": []})
    resolver = mock._data_resolver
    items = _slice_resolved(
        artist.music_video_ids,
        offset,
        limit,
        lambda mvid: resolver.music_video.get(LookupContext(mvid, locale)),
    )
    data = [_music_video_resource(sf, mvid, mv) for mvid, mv in items]
    total = 0 if artist.music_video_ids is None else len(artist.music_video_ids)
    return _standalone_paginated_response(
        f"/v1/catalog/{sf}/artists/{artist_id}/music-videos",
        data,
        total,
        offset=offset,
        limit=limit,
    )


def _handle_artist_playlists(
    mock: MusicKitApiMock, req: Request, sf: str, artist_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    limit, offset, err = _parse_standalone_pagination(req, _CATALOG_ARTIST_PLAYLISTS)
    if err is not None:
        return err
    artist = mock._data_resolver.artist.get(LookupContext(artist_id, locale))
    if artist is None:
        return _json_response({"data": []})
    resolver = mock._data_resolver
    items = _slice_resolved(
        artist.playlist_ids,
        offset,
        limit,
        lambda pid: resolver.playlist.get(LookupContext(pid, locale)),
    )
    data = [_playlist_resource(sf, pid, pl) for pid, pl in items]
    total = 0 if artist.playlist_ids is None else len(artist.playlist_ids)
    return _standalone_paginated_response(
        f"/v1/catalog/{sf}/artists/{artist_id}/playlists",
        data,
        total,
        offset=offset,
        limit=limit,
    )


def _handle_artist_station(
    mock: MusicKitApiMock, req: Request, sf: str, artist_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    artist = mock._data_resolver.artist.get(LookupContext(artist_id, locale))
    if artist is None or artist.station_id is None:
        return _json_response({"data": []})
    station = mock._data_resolver.station.get(LookupContext(artist.station_id, locale))
    if station is None:
        return _json_response({"data": []})
    return _json_response({"data": [_station_resource(sf, artist.station_id, station)]})


def _handle_music_video_genres(
    mock: MusicKitApiMock, req: Request, sf: str, music_video_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    limit, offset, err = _parse_standalone_pagination(req, _CATALOG_MUSIC_VIDEO_GENRES)
    if err is not None:
        return err
    music_video = mock._data_resolver.music_video.get(
        LookupContext(music_video_id, locale)
    )
    if music_video is None:
        return _json_response({"data": []})
    resolver = mock._data_resolver
    items = _slice_resolved(
        music_video.genre_ids,
        offset,
        limit,
        lambda gid: resolver.genre.get(LookupContext(gid, locale)),
    )
    data = [_genre_resource(sf, gid, g) for gid, g in items]
    total = 0 if music_video.genre_ids is None else len(music_video.genre_ids)
    return _standalone_paginated_response(
        f"/v1/catalog/{sf}/music-videos/{music_video_id}/genres",
        data,
        total,
        offset=offset,
        limit=limit,
    )


def _handle_music_video_songs(
    mock: MusicKitApiMock, req: Request, sf: str, music_video_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    limit, offset, err = _parse_standalone_pagination(req, _CATALOG_MUSIC_VIDEO_SONGS)
    if err is not None:
        return err
    music_video = mock._data_resolver.music_video.get(
        LookupContext(music_video_id, locale)
    )
    if music_video is None:
        return _json_response({"data": []})
    resolver = mock._data_resolver
    items = _slice_resolved(
        music_video.song_ids,
        offset,
        limit,
        lambda sid: resolver.song.get(LookupContext(sid, locale)),
    )
    data = [_song_resource(sf, sid, sg) for sid, sg in items]
    total = 0 if music_video.song_ids is None else len(music_video.song_ids)
    return _standalone_paginated_response(
        f"/v1/catalog/{sf}/music-videos/{music_video_id}/songs",
        data,
        total,
        offset=offset,
        limit=limit,
    )


def _handle_station_radio_show(
    mock: MusicKitApiMock, req: Request, sf: str, station_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    station = mock._data_resolver.station.get(LookupContext(station_id, locale))
    if station is None or station.radio_show_id is None:
        return _json_response({"data": []})
    curator = mock._data_resolver.curator.get(
        LookupContext(station.radio_show_id, locale)
    )
    if curator is None:
        return _json_response({"data": []})
    return _json_response(
        {"data": [_curator_resource(sf, station.radio_show_id, curator)]}
    )


def _handle_apple_curator_playlists(
    mock: MusicKitApiMock, req: Request, sf: str, apple_curator_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    limit, offset, err = _parse_standalone_pagination(
        req, _CATALOG_APPLE_CURATOR_PLAYLISTS
    )
    if err is not None:
        return err
    curator = mock._data_resolver.curator.get(LookupContext(apple_curator_id, locale))
    if curator is None:
        return _json_response({"data": []})
    resolver = mock._data_resolver
    items = _slice_resolved(
        curator.playlist_ids,
        offset,
        limit,
        lambda pid: resolver.playlist.get(LookupContext(pid, locale)),
    )
    data = [_playlist_resource(sf, pid, pl) for pid, pl in items]
    total = 0 if curator.playlist_ids is None else len(curator.playlist_ids)
    return _standalone_paginated_response(
        f"/v1/catalog/{sf}/apple-curators/{apple_curator_id}/playlists",
        data,
        total,
        offset=offset,
        limit=limit,
    )


def _handle_apple_curator_grouping(
    mock: MusicKitApiMock, req: Request, sf: str, apple_curator_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    curator = mock._data_resolver.curator.get(LookupContext(apple_curator_id, locale))
    if curator is None or curator.grouping_id is None:
        return _json_response({"data": []})
    grouping = mock._data_resolver.grouping.get(
        LookupContext(curator.grouping_id, locale)
    )
    if grouping is None:
        return _json_response({"data": []})
    return _json_response(
        {"data": [_grouping_resource(sf, curator.grouping_id, grouping)]}
    )


def _handle_curator_playlists(
    mock: MusicKitApiMock, req: Request, sf: str, curator_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    limit, offset, err = _parse_standalone_pagination(req, _CATALOG_CURATOR_PLAYLISTS)
    if err is not None:
        return err
    curator = mock._data_resolver.curator.get(LookupContext(curator_id, locale))
    if curator is None:
        return _json_response({"data": []})
    resolver = mock._data_resolver
    items = _slice_resolved(
        curator.playlist_ids,
        offset,
        limit,
        lambda pid: resolver.playlist.get(LookupContext(pid, locale)),
    )
    data = [_playlist_resource(sf, pid, pl) for pid, pl in items]
    total = 0 if curator.playlist_ids is None else len(curator.playlist_ids)
    return _standalone_paginated_response(
        f"/v1/catalog/{sf}/curators/{curator_id}/playlists",
        data,
        total,
        offset=offset,
        limit=limit,
    )


def _build_curator_rels(
    sf: str,
    curator_id: str,
    curator: Curator,
    *,
    locale: str | None,
    includes: set[str],
    resolver: _DataResolver,
) -> dict[str, _JSONValue]:
    """Build sub-rels for a curator resource.

    Apple emits both ``relationships.playlists`` (with ids-only by default,
    full resources on ``?include=playlists``) and ``relationships.grouping``
    (for ``apple-curators`` only — default-included with the grouping ref,
    full grouping on ``?include=grouping``).
    """
    rels: dict[str, _JSONValue] = {}
    pagination = (
        _CATALOG_APPLE_CURATOR_PLAYLISTS
        if curator.type == "apple-curators"
        else _CATALOG_CURATOR_PLAYLISTS
    )
    playlists_href = f"/v1/catalog/{sf}/{curator.type}/{curator_id}/playlists"
    playlists_block = _paginated_relationship_block(
        playlists_href,
        curator.playlist_ids,
        pagination.page_size,
        resolver=lambda pid: resolver.playlist.get(LookupContext(pid, locale)),
        encode=lambda pid, pl: _playlist_resource(sf, pid, pl),
        fallback_ref=lambda pid: _catalog_ref(sf, "playlists", pid),
        include_full="playlists" in includes,
    )
    if playlists_block is not None:
        rels["playlists"] = playlists_block

    if curator.type == "apple-curators" and curator.grouping_id is not None:
        grouping_href = f"/v1/catalog/{sf}/apple-curators/{curator_id}/grouping"
        grouping_data: dict[str, _JSONValue] | None = None
        if "grouping" in includes:
            grouping = resolver.grouping.get(LookupContext(curator.grouping_id, locale))
            if grouping is not None:
                grouping_data = _grouping_resource(sf, curator.grouping_id, grouping)
        if grouping_data is None:
            grouping_data = _catalog_ref(sf, "groupings", curator.grouping_id)
        rels["grouping"] = {"href": grouping_href, "data": [grouping_data]}
    return rels


def _handle_apple_curator_singular(
    mock: MusicKitApiMock, req: Request, sf: str, apple_curator_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    curator = mock._data_resolver.curator.get(LookupContext(apple_curator_id, locale))
    if curator is None or curator.type != "apple-curators":
        return _json_response(_resource_not_found_404_envelope(), status=404)
    includes = _parse_csv_param(req.url, "include")
    rels = _build_curator_rels(
        sf,
        apple_curator_id,
        curator,
        locale=locale,
        includes=includes,
        resolver=mock._data_resolver,
    )
    return _json_response(
        {
            "data": [
                _curator_resource(
                    sf, apple_curator_id, curator, relationships=rels or None
                )
            ]
        }
    )


def _handle_curator_singular(
    mock: MusicKitApiMock, req: Request, sf: str, curator_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    curator = mock._data_resolver.curator.get(LookupContext(curator_id, locale))
    if curator is None or curator.type != "curators":
        return _json_response(_resource_not_found_404_envelope(), status=404)
    includes = _parse_csv_param(req.url, "include")
    rels = _build_curator_rels(
        sf,
        curator_id,
        curator,
        locale=locale,
        includes=includes,
        resolver=mock._data_resolver,
    )
    return _json_response(
        {
            "data": [
                _curator_resource(sf, curator_id, curator, relationships=rels or None)
            ]
        }
    )


def _build_recommendation_rels(
    sf: str,
    recommendation_id: str,
    recommendation: PersonalRecommendation,
    *,
    locale: str | None,
    resolver: _DataResolver,
) -> dict[str, _JSONValue]:
    """Build the default-included ``relationships.contents`` block."""
    if recommendation.contents is None:
        return {}
    contents_href = f"/v1/me/recommendations/{recommendation_id}/contents"
    data: list[dict[str, _JSONValue]] = []
    page_size = _ME_RECOMMENDATION_CONTENTS.page_size
    for content in recommendation.contents[:page_size]:
        if content.type == "playlists":
            pl = resolver.playlist.get(LookupContext(content.id, locale))
            if pl is not None:
                data.append(_playlist_resource(sf, content.id, pl))
                continue
        elif content.type == "albums":
            al = resolver.album.get(LookupContext(content.id, locale))
            if al is not None:
                data.append(_album_resource(sf, content.id, al))
                continue
        elif content.type == "stations":
            st = resolver.station.get(LookupContext(content.id, locale))
            if st is not None:
                data.append(_station_resource(sf, content.id, st))
                continue
        elif content.type == "music-videos":
            mv = resolver.music_video.get(LookupContext(content.id, locale))
            if mv is not None:
                data.append(_music_video_resource(sf, content.id, mv))
                continue
        data.append(_catalog_ref(sf, content.type, content.id))
    out: dict[str, _JSONValue] = {"href": contents_href, "data": data}
    if len(recommendation.contents) > page_size:
        out["next"] = f"{contents_href}?offset={page_size}"
    return {"contents": out}


def _handle_recommendation_singular(
    mock: MusicKitApiMock, req: Request, recommendation_id: str
) -> Response:
    from musickit_api_mock.endpoints.library import _user_storefront_slug
    from musickit_api_mock.endpoints.schema import _personal_recommendation_resource

    locale, err = _check_and_resolve_locale(req, storefront_slug=None, mock=mock)
    if err is not None:
        return err
    recommendation = mock._data_resolver.personal_recommendation.get(
        LookupContext(recommendation_id, locale)
    )
    if recommendation is None:
        return _json_response({"data": []})
    sf = _user_storefront_slug(mock)
    rels = _build_recommendation_rels(
        sf,
        recommendation_id,
        recommendation,
        locale=locale,
        resolver=mock._data_resolver,
    )
    return _json_response(
        {
            "data": [
                _personal_recommendation_resource(
                    recommendation_id, recommendation, relationships=rels or None
                )
            ]
        }
    )


def _handle_recommendations_batch(mock: MusicKitApiMock, req: Request) -> Response:
    """Batch / list endpoint for the user's recommendations.

    ``?ids=X,Y`` filters to those ids; absent ``?ids=`` lists every entry
    in ``mock.data.personal_recommendations`` (dict source required).
    Each emitted recommendation carries the default-included ``contents``
    relationship.
    """
    from musickit_api_mock.endpoints.library import _user_storefront_slug
    from musickit_api_mock.endpoints.query import _dedupe, _parse_ids
    from musickit_api_mock.endpoints.schema import _personal_recommendation_resource

    locale, err = _check_and_resolve_locale(req, storefront_slug=None, mock=mock)
    if err is not None:
        return err
    has_param, ids = _parse_ids(req.url)
    if has_param and not ids:
        return _json_response(_empty_ids_400_envelope(), status=400)
    if has_param:
        rec_ids = _dedupe(ids)
    else:
        rec_ids = _list_source_ids(
            mock.data.personal_recommendations, "data.personal_recommendations"
        )
    sf = _user_storefront_slug(mock)
    resolver = mock._data_resolver
    resources: list[dict[str, _JSONValue]] = []
    for rid in rec_ids:
        rec = resolver.personal_recommendation.get(LookupContext(rid, locale))
        if rec is None:
            continue
        rels = _build_recommendation_rels(
            sf, rid, rec, locale=locale, resolver=resolver
        )
        resources.append(
            _personal_recommendation_resource(rid, rec, relationships=rels or None)
        )
    return _json_response({"data": resources})


def _handle_genres_batch(mock: MusicKitApiMock, req: Request, sf: str) -> Response:
    """Batch / list endpoint for catalog genres.

    ``?ids=X,Y`` filters to those ids; absent ``?ids=`` lists every entry
    in ``mock.data.genres`` (dict source required).
    """
    from musickit_api_mock.endpoints.query import _dedupe, _parse_ids

    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    has_param, ids = _parse_ids(req.url)
    if has_param and not ids:
        return _json_response(_empty_ids_400_envelope(), status=400)
    if has_param:
        genre_ids = _dedupe(ids)
    else:
        genre_ids = _list_source_ids(mock.data.genres, "data.genres")
    resolver = mock._data_resolver
    resources: list[dict[str, _JSONValue]] = []
    for gid in genre_ids:
        g = resolver.genre.get(LookupContext(gid, locale))
        if g is None:
            continue
        resources.append(_genre_resource(sf, gid, g))
    return _json_response({"data": resources})


def _handle_genre_singular(
    mock: MusicKitApiMock, req: Request, sf: str, genre_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    g = mock._data_resolver.genre.get(LookupContext(genre_id, locale))
    if g is None:
        return _json_response({"data": []})
    return _json_response({"data": [_genre_resource(sf, genre_id, g)]})


def _handle_record_labels_batch(
    mock: MusicKitApiMock, req: Request, sf: str
) -> Response:
    """Batch / list endpoint for catalog record labels.

    ``?ids=X,Y`` filters to those ids; absent ``?ids=`` lists every entry
    in ``mock.data.record_labels`` (dict source required).
    """
    from musickit_api_mock.endpoints.query import _dedupe, _parse_ids

    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    has_param, ids = _parse_ids(req.url)
    if has_param and not ids:
        return _json_response(_empty_ids_400_envelope(), status=400)
    if has_param:
        rl_ids = _dedupe(ids)
    else:
        rl_ids = _list_source_ids(mock.data.record_labels, "data.record_labels")
    resolver = mock._data_resolver
    resources: list[dict[str, _JSONValue]] = []
    for rid in rl_ids:
        rl = resolver.record_label.get(LookupContext(rid, locale))
        if rl is None:
            continue
        resources.append(_record_label_resource(sf, rid, rl))
    return _json_response({"data": resources})


def _handle_record_label_singular(
    mock: MusicKitApiMock, req: Request, sf: str, record_label_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf, mock=mock)
    if err is not None:
        return err
    rl = mock._data_resolver.record_label.get(LookupContext(record_label_id, locale))
    if rl is None:
        return _json_response({"data": []})
    return _json_response({"data": [_record_label_resource(sf, record_label_id, rl)]})
