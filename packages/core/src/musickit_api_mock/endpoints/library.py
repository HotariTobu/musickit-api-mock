"""Handlers for the user's library batch and singular endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.data.lookup import LookupContext
from musickit_api_mock.endpoints.pagination import (
    _LIBRARY_ALBUM_ARTISTS,
    _LIBRARY_ALBUM_TRACKS,
    _LIBRARY_ARTIST_ALBUMS,
    _LIBRARY_MUSIC_VIDEO_ALBUMS,
    _LIBRARY_MUSIC_VIDEO_ARTISTS,
    _LIBRARY_PLAYLIST_TRACKS,
    _LIBRARY_SONG_ALBUMS,
    _LIBRARY_SONG_ARTISTS,
    _paginated_relationship_block,
    _parse_inline_limits,
    _singleton_relationship_block,
)
from musickit_api_mock.endpoints.query import (
    _dedupe,
    _parse_csv_param,
    _parse_ids,
)
from musickit_api_mock.endpoints.request_locale import _check_and_resolve_locale
from musickit_api_mock.endpoints.responses.storefront import StorefrontResponseSuccess
from musickit_api_mock.endpoints.schema import (
    _album_resource,
    _artist_resource,
    _batch_envelope,
    _empty_ids_400_envelope,
    _library_album_resource,
    _library_artist_resource,
    _library_music_video_resource,
    _library_playlist_resource,
    _library_ref,
    _library_song_resource,
    _library_songs_dead_path_400_envelope,
    _missing_ids_param_400_envelope,
    _music_video_resource,
    _playlist_resource,
    _song_resource,
)
from musickit_api_mock.transport.response_builders import _json_response

if TYPE_CHECKING:
    from musickit_api_mock.data.library_album import LibraryAlbum
    from musickit_api_mock.data.library_artist import LibraryArtist
    from musickit_api_mock.data.library_music_video import LibraryMusicVideo
    from musickit_api_mock.data.library_playlist import LibraryPlaylist
    from musickit_api_mock.data.library_song import LibrarySong
    from musickit_api_mock.json_value import _JSONValue
    from musickit_api_mock.mock import MusicKitApiMock
    from musickit_api_mock.transport.http import Request, Response


def _build_library_song_catalog_rel(
    mock: MusicKitApiMock,
    sf: str,
    library_id: str,
    library_song: LibrarySong,
    *,
    locale: str | None,
) -> dict[str, _JSONValue] | None:
    """Build ``relationships.catalog`` for a library song (``?include=catalog``).

    Resolves the linked catalog song via ``catalog_id`` and emits the full
    catalog song shape inline. Returns ``None`` when the library song has
    no ``catalog_id`` set.
    """
    if library_song.catalog_id is None:
        return None
    href = f"/v1/me/library/songs/{library_id}/catalog"
    catalog_song = mock._data_resolver.song.get(
        LookupContext(library_song.catalog_id, locale)
    )
    if catalog_song is None:
        return _singleton_relationship_block(href, [])
    return _singleton_relationship_block(
        href, [_song_resource(sf, library_song.catalog_id, catalog_song)]
    )


def _build_library_album_catalog_rel(
    mock: MusicKitApiMock,
    sf: str,
    library_id: str,
    library_album: LibraryAlbum,
    *,
    locale: str | None,
) -> dict[str, _JSONValue] | None:
    if library_album.catalog_id is None:
        return None
    href = f"/v1/me/library/albums/{library_id}/catalog"
    catalog_album = mock._data_resolver.album.get(
        LookupContext(library_album.catalog_id, locale)
    )
    if catalog_album is None:
        return _singleton_relationship_block(href, [])
    return _singleton_relationship_block(
        href, [_album_resource(sf, library_album.catalog_id, catalog_album)]
    )


def _user_storefront_slug(mock: MusicKitApiMock) -> str:
    """Return the user's storefront slug for ``?include=catalog`` href URLs."""
    resp = mock._endpoint_resolver.storefront()
    if isinstance(resp, StorefrontResponseSuccess):
        return resp.storefront.id
    raise ValueError("user storefront is not in a success state")


def _build_library_song_rels(
    mock: MusicKitApiMock,
    library_id: str,
    library_song: LibrarySong,
    *,
    locale: str | None,
    includes: set[str],
    sizes: dict[str, int],
) -> dict[str, _JSONValue]:
    resolver = mock._data_resolver
    rels: dict[str, _JSONValue] = {}
    if "albums" in includes:
        albums_block = _paginated_relationship_block(
            f"/v1/me/library/songs/{library_id}/albums",
            library_song.album_ids,
            sizes["albums"],
            resolver=lambda aid: resolver.library_album.get(LookupContext(aid, locale)),
            encode=lambda aid, la: _library_album_resource(aid, la),
            fallback_ref=lambda aid: _library_ref("library-albums", aid),
            include_full=True,
        )
        if albums_block is not None:
            rels["albums"] = albums_block
    if "artists" in includes:
        artists_block = _paginated_relationship_block(
            f"/v1/me/library/songs/{library_id}/artists",
            library_song.artist_ids,
            sizes["artists"],
            resolver=lambda aid: resolver.library_artist.get(
                LookupContext(aid, locale)
            ),
            encode=lambda aid, lar: _library_artist_resource(aid, lar),
            fallback_ref=lambda aid: _library_ref("library-artists", aid),
            include_full=True,
        )
        if artists_block is not None:
            rels["artists"] = artists_block
    if "catalog" in includes:
        sf = _user_storefront_slug(mock)
        catalog = _build_library_song_catalog_rel(
            mock, sf, library_id, library_song, locale=locale
        )
        if catalog is not None:
            rels["catalog"] = catalog
    return rels


def _build_library_artist_rels(
    mock: MusicKitApiMock,
    library_id: str,
    library_artist: LibraryArtist,
    *,
    locale: str | None,
    includes: set[str],
    sizes: dict[str, int],
) -> dict[str, _JSONValue]:
    resolver = mock._data_resolver
    rels: dict[str, _JSONValue] = {}
    if "albums" in includes:
        albums_block = _paginated_relationship_block(
            f"/v1/me/library/artists/{library_id}/albums",
            library_artist.album_ids,
            sizes["albums"],
            resolver=lambda aid: resolver.library_album.get(LookupContext(aid, locale)),
            encode=lambda aid, la: _library_album_resource(aid, la),
            fallback_ref=lambda aid: _library_ref("library-albums", aid),
            include_full=True,
        )
        if albums_block is not None:
            rels["albums"] = albums_block
    if "catalog" in includes and library_artist.catalog_id is not None:
        sf = _user_storefront_slug(mock)
        href = f"/v1/me/library/artists/{library_id}/catalog"
        catalog_artist = resolver.artist.get(
            LookupContext(library_artist.catalog_id, locale)
        )
        if catalog_artist is None:
            rels["catalog"] = _singleton_relationship_block(href, [])
        else:
            rels["catalog"] = _singleton_relationship_block(
                href, [_artist_resource(sf, library_artist.catalog_id, catalog_artist)]
            )
    return rels


def _build_library_album_rels(
    mock: MusicKitApiMock,
    library_id: str,
    library_album: LibraryAlbum,
    *,
    locale: str | None,
    includes: set[str],
    sizes: dict[str, int],
) -> dict[str, _JSONValue]:
    resolver = mock._data_resolver
    rels: dict[str, _JSONValue] = {}

    tracks_block = _paginated_relationship_block(
        f"/v1/me/library/albums/{library_id}/tracks",
        library_album.track_ids,
        sizes["tracks"],
        resolver=lambda sid: resolver.library_song.get(LookupContext(sid, locale)),
        encode=lambda sid, ls: _library_song_resource(sid, ls),
        fallback_ref=lambda sid: _library_ref("library-songs", sid),
        include_full=True,
        include_meta_total=True,
    )
    if tracks_block is not None:
        rels["tracks"] = tracks_block

    if "artists" in includes:
        artists_block = _paginated_relationship_block(
            f"/v1/me/library/albums/{library_id}/artists",
            library_album.artist_ids,
            sizes["artists"],
            resolver=lambda aid: resolver.library_artist.get(
                LookupContext(aid, locale)
            ),
            encode=lambda aid, lar: _library_artist_resource(aid, lar),
            fallback_ref=lambda aid: _library_ref("library-artists", aid),
            include_full=True,
        )
        if artists_block is not None:
            rels["artists"] = artists_block

    if "catalog" in includes:
        sf = _user_storefront_slug(mock)
        catalog = _build_library_album_catalog_rel(
            mock, sf, library_id, library_album, locale=locale
        )
        if catalog is not None:
            rels["catalog"] = catalog

    return rels


def _build_library_playlist_rels(
    mock: MusicKitApiMock,
    library_id: str,
    library_playlist: LibraryPlaylist,
    *,
    locale: str | None,
    includes: set[str],
    sizes: dict[str, int],
) -> dict[str, _JSONValue]:
    resolver = mock._data_resolver
    rels: dict[str, _JSONValue] = {}
    tracks_block = _paginated_relationship_block(
        f"/v1/me/library/playlists/{library_id}/tracks",
        library_playlist.track_ids,
        sizes["tracks"],
        resolver=lambda sid: resolver.library_song.get(LookupContext(sid, locale)),
        encode=lambda sid, ls: _library_song_resource(sid, ls),
        fallback_ref=lambda sid: _library_ref("library-songs", sid),
        include_full=True,
        include_meta_total=True,
    )
    if tracks_block is not None:
        rels["tracks"] = tracks_block
    if "catalog" in includes and library_playlist.catalog_id is not None:
        sf = _user_storefront_slug(mock)
        href = f"/v1/me/library/playlists/{library_id}/catalog"
        catalog_playlist = resolver.playlist.get(
            LookupContext(library_playlist.catalog_id, locale)
        )
        if catalog_playlist is None:
            rels["catalog"] = _singleton_relationship_block(href, [])
        else:
            rels["catalog"] = _singleton_relationship_block(
                href,
                [_playlist_resource(sf, library_playlist.catalog_id, catalog_playlist)],
            )
    return rels


def _build_library_music_video_rels(
    mock: MusicKitApiMock,
    library_id: str,
    library_music_video: LibraryMusicVideo,
    *,
    locale: str | None,
    includes: set[str],
    sizes: dict[str, int],
) -> dict[str, _JSONValue]:
    resolver = mock._data_resolver
    rels: dict[str, _JSONValue] = {}

    if "albums" in includes:
        albums_block = _paginated_relationship_block(
            f"/v1/me/library/music-videos/{library_id}/albums",
            library_music_video.album_ids,
            sizes["albums"],
            resolver=lambda aid: resolver.library_album.get(LookupContext(aid, locale)),
            encode=lambda aid, la: _library_album_resource(aid, la),
            fallback_ref=lambda aid: _library_ref("library-albums", aid),
            include_full=True,
        )
        if albums_block is not None:
            rels["albums"] = albums_block

    if "artists" in includes:
        artists_block = _paginated_relationship_block(
            f"/v1/me/library/music-videos/{library_id}/artists",
            library_music_video.artist_ids,
            sizes["artists"],
            resolver=lambda aid: resolver.library_artist.get(
                LookupContext(aid, locale)
            ),
            encode=lambda aid, lar: _library_artist_resource(aid, lar),
            fallback_ref=lambda aid: _library_ref("library-artists", aid),
            include_full=True,
        )
        if artists_block is not None:
            rels["artists"] = artists_block

    if "catalog" in includes and library_music_video.catalog_id is not None:
        sf = _user_storefront_slug(mock)
        href = f"/v1/me/library/music-videos/{library_id}/catalog"
        catalog_music_video = resolver.music_video.get(
            LookupContext(library_music_video.catalog_id, locale)
        )
        if catalog_music_video is None:
            rels["catalog"] = _singleton_relationship_block(href, [])
        else:
            rels["catalog"] = _singleton_relationship_block(
                href,
                [
                    _music_video_resource(
                        sf, library_music_video.catalog_id, catalog_music_video
                    )
                ],
            )

    return rels


def _handle_library_songs(mock: MusicKitApiMock, req: Request) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=None, mock=mock)
    if err is not None:
        return err
    has_param, ids = _parse_ids(req.url)
    if not has_param:
        return _json_response(_missing_ids_param_400_envelope(), status=400)
    if not ids:
        return _json_response(_empty_ids_400_envelope(), status=400)
    includes = _parse_csv_param(req.url, "include")
    sizes, err = _parse_inline_limits(
        req,
        {"albums": _LIBRARY_SONG_ALBUMS, "artists": _LIBRARY_SONG_ARTISTS},
    )
    if err is not None:
        return err
    resolver = mock._data_resolver
    resources: list[dict[str, _JSONValue]] = []
    for sid in _dedupe(ids):
        library_song = resolver.library_song.get(LookupContext(sid, locale))
        if library_song is None:
            continue
        rels = _build_library_song_rels(
            mock, sid, library_song, locale=locale, includes=includes, sizes=sizes
        )
        resources.append(
            _library_song_resource(sid, library_song, relationships=rels or None)
        )
    return _json_response(_batch_envelope(resources))


def _handle_library_songs_dead_path() -> Response:
    return _json_response(_library_songs_dead_path_400_envelope(), status=400)


def _handle_library_song(mock: MusicKitApiMock, req: Request, item_id: str) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=None, mock=mock)
    if err is not None:
        return err
    includes = _parse_csv_param(req.url, "include")
    sizes, err = _parse_inline_limits(
        req,
        {"albums": _LIBRARY_SONG_ALBUMS, "artists": _LIBRARY_SONG_ARTISTS},
    )
    if err is not None:
        return err
    library_song = mock._data_resolver.library_song.get(LookupContext(item_id, locale))
    if library_song is None:
        return _json_response({"data": []})
    rels = _build_library_song_rels(
        mock, item_id, library_song, locale=locale, includes=includes, sizes=sizes
    )
    return _json_response(
        _batch_envelope(
            [_library_song_resource(item_id, library_song, relationships=rels or None)]
        )
    )


def _handle_library_album(
    mock: MusicKitApiMock, req: Request, item_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=None, mock=mock)
    if err is not None:
        return err
    library_album = mock._data_resolver.library_album.get(
        LookupContext(item_id, locale)
    )
    if library_album is None:
        return _json_response({"data": []})
    includes = _parse_csv_param(req.url, "include")
    sizes, err = _parse_inline_limits(
        req,
        {"tracks": _LIBRARY_ALBUM_TRACKS, "artists": _LIBRARY_ALBUM_ARTISTS},
    )
    if err is not None:
        return err
    rels = _build_library_album_rels(
        mock, item_id, library_album, locale=locale, includes=includes, sizes=sizes
    )
    return _json_response(
        _batch_envelope(
            [
                _library_album_resource(
                    item_id, library_album, relationships=rels or None
                )
            ]
        )
    )


def _handle_library_playlist(
    mock: MusicKitApiMock, req: Request, item_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=None, mock=mock)
    if err is not None:
        return err
    library_playlist = mock._data_resolver.library_playlist.get(
        LookupContext(item_id, locale)
    )
    if library_playlist is None:
        return _json_response({"data": []})
    includes = _parse_csv_param(req.url, "include")
    sizes, err = _parse_inline_limits(req, {"tracks": _LIBRARY_PLAYLIST_TRACKS})
    if err is not None:
        return err
    rels = _build_library_playlist_rels(
        mock,
        item_id,
        library_playlist,
        locale=locale,
        includes=includes,
        sizes=sizes,
    )
    return _json_response(
        _batch_envelope(
            [
                _library_playlist_resource(
                    item_id, library_playlist, relationships=rels or None
                )
            ]
        )
    )


def _handle_library_artist(
    mock: MusicKitApiMock, req: Request, item_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=None, mock=mock)
    if err is not None:
        return err
    library_artist = mock._data_resolver.library_artist.get(
        LookupContext(item_id, locale)
    )
    if library_artist is None:
        return _json_response({"data": []})
    includes = _parse_csv_param(req.url, "include")
    sizes, err = _parse_inline_limits(req, {"albums": _LIBRARY_ARTIST_ALBUMS})
    if err is not None:
        return err
    rels = _build_library_artist_rels(
        mock,
        item_id,
        library_artist,
        locale=locale,
        includes=includes,
        sizes=sizes,
    )
    return _json_response(
        _batch_envelope(
            [
                _library_artist_resource(
                    item_id, library_artist, relationships=rels or None
                )
            ]
        )
    )


def _handle_library_music_video(
    mock: MusicKitApiMock, req: Request, item_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=None, mock=mock)
    if err is not None:
        return err
    library_music_video = mock._data_resolver.library_music_video.get(
        LookupContext(item_id, locale)
    )
    if library_music_video is None:
        return _json_response({"data": []})
    includes = _parse_csv_param(req.url, "include")
    sizes, err = _parse_inline_limits(
        req,
        {
            "albums": _LIBRARY_MUSIC_VIDEO_ALBUMS,
            "artists": _LIBRARY_MUSIC_VIDEO_ARTISTS,
        },
    )
    if err is not None:
        return err
    rels = _build_library_music_video_rels(
        mock,
        item_id,
        library_music_video,
        locale=locale,
        includes=includes,
        sizes=sizes,
    )
    return _json_response(
        _batch_envelope(
            [
                _library_music_video_resource(
                    item_id, library_music_video, relationships=rels or None
                )
            ]
        )
    )
