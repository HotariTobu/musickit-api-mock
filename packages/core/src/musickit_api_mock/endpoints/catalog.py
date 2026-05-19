"""Handlers for catalog batch (``/v1/catalog/{sf}/{kind}``) and song singular endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.data.lookup import LookupContext
from musickit_api_mock.endpoints.pagination import (
    _ARTIST_ALBUMS,
    _CATALOG_ALBUM_ARTISTS,
    _CATALOG_ALBUM_GENRES,
    _CATALOG_ALBUM_RECORD_LABELS,
    _CATALOG_ALBUM_TRACKS,
    _CATALOG_ARTIST_GENRES,
    _CATALOG_ARTIST_MUSIC_VIDEOS,
    _CATALOG_ARTIST_PLAYLISTS,
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
from musickit_api_mock.endpoints.schema import (
    _album_resource,
    _artist_resource,
    _batch_envelope,
    _catalog_ref,
    _curator_resource,
    _empty_ids_400_envelope,
    _genre_resource,
    _library_album_resource,
    _library_music_video_resource,
    _library_playlist_resource,
    _library_song_resource,
    _missing_ids_param_400_envelope,
    _music_video_resource,
    _playlist_resource,
    _record_label_resource,
    _song_resource,
    _station_resource,
)
from musickit_api_mock.transport.response_builders import _json_response

if TYPE_CHECKING:
    from musickit_api_mock.data.album import Album
    from musickit_api_mock.data.artist import Artist
    from musickit_api_mock.data.music_video import MusicVideo
    from musickit_api_mock.data.playlist import Playlist
    from musickit_api_mock.data.song import Song
    from musickit_api_mock.data.station import Station
    from musickit_api_mock.json_value import _JSONValue
    from musickit_api_mock.mock import MusicKitApiMock
    from musickit_api_mock.transport.http import Request, Response


def _build_song_rels(
    mock: MusicKitApiMock,
    sf: str,
    song_id: str,
    song: Song,
    *,
    locale: str | None,
    includes: set[str],
    sizes: dict[str, int],
) -> dict[str, _JSONValue]:
    resolver = mock._data_resolver
    rels: dict[str, _JSONValue] = {}

    albums_block = _paginated_relationship_block(
        f"/v1/catalog/{sf}/songs/{song_id}/albums",
        song.album_ids,
        sizes["albums"],
        resolver=lambda aid: resolver.album.get(LookupContext(aid, locale)),
        encode=lambda aid, al: _album_resource(sf, aid, al),
        fallback_ref=lambda aid: _catalog_ref(sf, "albums", aid),
        include_full="albums" in includes,
    )
    if albums_block is not None:
        rels["albums"] = albums_block

    artists_block = _paginated_relationship_block(
        f"/v1/catalog/{sf}/songs/{song_id}/artists",
        song.artist_ids,
        sizes["artists"],
        resolver=lambda aid: resolver.artist.get(LookupContext(aid, locale)),
        encode=lambda aid, ar: _artist_resource(sf, aid, ar),
        fallback_ref=lambda aid: _catalog_ref(sf, "artists", aid),
        include_full="artists" in includes,
    )
    if artists_block is not None:
        rels["artists"] = artists_block

    if "composers" in includes:
        composers_block = _paginated_relationship_block(
            f"/v1/catalog/{sf}/songs/{song_id}/composers",
            song.composer_ids,
            sizes["composers"],
            resolver=lambda aid: resolver.artist.get(LookupContext(aid, locale)),
            encode=lambda aid, ar: _artist_resource(sf, aid, ar),
            fallback_ref=lambda aid: _catalog_ref(sf, "artists", aid),
            include_full=True,
        )
        if composers_block is not None:
            rels["composers"] = composers_block

    if "library" in includes and song.library_song_id is not None:
        library_song = resolver.library_song.get(
            LookupContext(song.library_song_id, locale)
        )
        if library_song is not None:
            rels["library"] = _singleton_relationship_block(
                f"/v1/catalog/{sf}/songs/{song_id}/library",
                [_library_song_resource(song.library_song_id, library_song)],
            )

    if "genres" in includes:
        genres_block = _paginated_relationship_block(
            f"/v1/catalog/{sf}/songs/{song_id}/genres",
            song.genre_ids,
            sizes.get("genres", _CATALOG_SONG_GENRES.page_size),
            resolver=lambda gid: resolver.genre.get(LookupContext(gid, locale)),
            encode=lambda gid, g: _genre_resource(sf, gid, g),
            fallback_ref=lambda gid: _catalog_ref(sf, "genres", gid),
            include_full=True,
        )
        if genres_block is not None:
            rels["genres"] = genres_block

    if "music-videos" in includes:
        mvs_block = _paginated_relationship_block(
            f"/v1/catalog/{sf}/songs/{song_id}/music-videos",
            song.music_video_ids,
            sizes.get("music-videos", _CATALOG_SONG_MUSIC_VIDEOS.page_size),
            resolver=lambda mvid: resolver.music_video.get(LookupContext(mvid, locale)),
            encode=lambda mvid, mv: _music_video_resource(sf, mvid, mv),
            fallback_ref=lambda mvid: _catalog_ref(sf, "music-videos", mvid),
            include_full=True,
        )
        if mvs_block is not None:
            rels["music-videos"] = mvs_block

    if "station" in includes and song.station_id is not None:
        station = resolver.station.get(LookupContext(song.station_id, locale))
        if station is not None:
            rels["station"] = _singleton_relationship_block(
                f"/v1/catalog/{sf}/songs/{song_id}/station",
                [_station_resource(sf, song.station_id, station)],
            )

    return rels


def _build_album_rels(
    mock: MusicKitApiMock,
    sf: str,
    album_id: str,
    album: Album,
    *,
    locale: str | None,
    includes: set[str],
    sizes: dict[str, int],
) -> dict[str, _JSONValue]:
    resolver = mock._data_resolver
    rels: dict[str, _JSONValue] = {}

    tracks_block = _paginated_relationship_block(
        f"/v1/catalog/{sf}/albums/{album_id}/tracks",
        album.track_ids,
        sizes["tracks"],
        resolver=lambda sid: resolver.song.get(LookupContext(sid, locale)),
        encode=lambda sid, song: _song_resource(sf, sid, song),
        fallback_ref=lambda sid: _catalog_ref(sf, "songs", sid),
        include_full=True,
    )
    if tracks_block is not None:
        rels["tracks"] = tracks_block

    artists_block = _paginated_relationship_block(
        f"/v1/catalog/{sf}/albums/{album_id}/artists",
        album.artist_ids,
        sizes["artists"],
        resolver=lambda aid: resolver.artist.get(LookupContext(aid, locale)),
        encode=lambda aid, ar: _artist_resource(sf, aid, ar),
        fallback_ref=lambda aid: _catalog_ref(sf, "artists", aid),
        include_full="artists" in includes,
    )
    if artists_block is not None:
        rels["artists"] = artists_block

    if "library" in includes and album.library_album_id is not None:
        library_album = resolver.library_album.get(
            LookupContext(album.library_album_id, locale)
        )
        if library_album is not None:
            rels["library"] = _singleton_relationship_block(
                f"/v1/catalog/{sf}/albums/{album_id}/library",
                [_library_album_resource(album.library_album_id, library_album)],
            )

    if "genres" in includes:
        genres_block = _paginated_relationship_block(
            f"/v1/catalog/{sf}/albums/{album_id}/genres",
            album.genre_ids,
            sizes.get("genres", _CATALOG_ALBUM_GENRES.page_size),
            resolver=lambda gid: resolver.genre.get(LookupContext(gid, locale)),
            encode=lambda gid, g: _genre_resource(sf, gid, g),
            fallback_ref=lambda gid: _catalog_ref(sf, "genres", gid),
            include_full=True,
        )
        if genres_block is not None:
            rels["genres"] = genres_block

    if "record-labels" in includes:
        labels_block = _paginated_relationship_block(
            f"/v1/catalog/{sf}/albums/{album_id}/record-labels",
            album.record_label_ids,
            sizes.get("record-labels", _CATALOG_ALBUM_RECORD_LABELS.page_size),
            resolver=lambda rid: resolver.record_label.get(LookupContext(rid, locale)),
            encode=lambda rid, rl: _record_label_resource(sf, rid, rl),
            fallback_ref=lambda rid: _catalog_ref(sf, "record-labels", rid),
            include_full=True,
        )
        if labels_block is not None:
            rels["record-labels"] = labels_block

    return rels


def _build_playlist_rels(
    mock: MusicKitApiMock,
    sf: str,
    playlist_id: str,
    playlist: Playlist,
    *,
    locale: str | None,
    includes: set[str],
    sizes: dict[str, int],
) -> dict[str, _JSONValue]:
    resolver = mock._data_resolver
    rels: dict[str, _JSONValue] = {}

    tracks_block = _paginated_relationship_block(
        f"/v1/catalog/{sf}/playlists/{playlist_id}/tracks",
        playlist.track_ids,
        sizes["tracks"],
        resolver=lambda sid: resolver.song.get(LookupContext(sid, locale)),
        encode=lambda sid, song: _song_resource(sf, sid, song),
        fallback_ref=lambda sid: _catalog_ref(sf, "songs", sid),
        include_full=True,
    )
    if tracks_block is not None:
        rels["tracks"] = tracks_block

    if playlist.curator_id is not None:
        curator = resolver.curator.get(LookupContext(playlist.curator_id, locale))
        if curator is None:
            raise ValueError(
                f"playlist {playlist_id!r} references curator_id {playlist.curator_id!r}"
                f" but mock.data.curators has no entry for it"
            )
        curator_data: list[dict[str, _JSONValue]]
        if "curator" in includes:
            curator_data = [_curator_resource(sf, playlist.curator_id, curator)]
        else:
            curator_data = [_catalog_ref(sf, curator.type, playlist.curator_id)]
        rels["curator"] = _singleton_relationship_block(
            f"/v1/catalog/{sf}/playlists/{playlist_id}/curator",
            curator_data,
        )

    if "library" in includes and playlist.library_playlist_id is not None:
        library_playlist = resolver.library_playlist.get(
            LookupContext(playlist.library_playlist_id, locale)
        )
        if library_playlist is not None:
            rels["library"] = _singleton_relationship_block(
                f"/v1/catalog/{sf}/playlists/{playlist_id}/library",
                [
                    _library_playlist_resource(
                        playlist.library_playlist_id, library_playlist
                    )
                ],
            )

    return rels


def _build_artist_rels(
    mock: MusicKitApiMock,
    sf: str,
    artist_id: str,
    artist: Artist,
    *,
    locale: str | None,
    includes: set[str],
    sizes: dict[str, int],
) -> dict[str, _JSONValue]:
    resolver = mock._data_resolver
    rels: dict[str, _JSONValue] = {}

    albums_block = _paginated_relationship_block(
        f"/v1/catalog/{sf}/artists/{artist_id}/albums",
        artist.album_ids,
        sizes["albums"],
        resolver=lambda aid: resolver.album.get(LookupContext(aid, locale)),
        encode=lambda aid, al: _album_resource(sf, aid, al),
        fallback_ref=lambda aid: _catalog_ref(sf, "albums", aid),
        include_full="albums" in includes,
    )
    if albums_block is not None:
        rels["albums"] = albums_block

    if "genres" in includes:
        genres_block = _paginated_relationship_block(
            f"/v1/catalog/{sf}/artists/{artist_id}/genres",
            artist.genre_ids,
            sizes.get("genres", _CATALOG_ARTIST_GENRES.page_size),
            resolver=lambda gid: resolver.genre.get(LookupContext(gid, locale)),
            encode=lambda gid, g: _genre_resource(sf, gid, g),
            fallback_ref=lambda gid: _catalog_ref(sf, "genres", gid),
            include_full=True,
        )
        if genres_block is not None:
            rels["genres"] = genres_block

    if "music-videos" in includes:
        mvs_block = _paginated_relationship_block(
            f"/v1/catalog/{sf}/artists/{artist_id}/music-videos",
            artist.music_video_ids,
            sizes.get("music-videos", _CATALOG_ARTIST_MUSIC_VIDEOS.page_size),
            resolver=lambda mvid: resolver.music_video.get(LookupContext(mvid, locale)),
            encode=lambda mvid, mv: _music_video_resource(sf, mvid, mv),
            fallback_ref=lambda mvid: _catalog_ref(sf, "music-videos", mvid),
            include_full=True,
        )
        if mvs_block is not None:
            rels["music-videos"] = mvs_block

    if "playlists" in includes:
        playlists_block = _paginated_relationship_block(
            f"/v1/catalog/{sf}/artists/{artist_id}/playlists",
            artist.playlist_ids,
            sizes.get("playlists", _CATALOG_ARTIST_PLAYLISTS.page_size),
            resolver=lambda pid: resolver.playlist.get(LookupContext(pid, locale)),
            encode=lambda pid, pl: _playlist_resource(sf, pid, pl),
            fallback_ref=lambda pid: _catalog_ref(sf, "playlists", pid),
            include_full=True,
        )
        if playlists_block is not None:
            rels["playlists"] = playlists_block

    if "station" in includes and artist.station_id is not None:
        station = resolver.station.get(LookupContext(artist.station_id, locale))
        if station is not None:
            rels["station"] = _singleton_relationship_block(
                f"/v1/catalog/{sf}/artists/{artist_id}/station",
                [_station_resource(sf, artist.station_id, station)],
            )

    return rels


def _build_music_video_rels(
    mock: MusicKitApiMock,
    sf: str,
    music_video_id: str,
    music_video: MusicVideo,
    *,
    locale: str | None,
    includes: set[str],
    sizes: dict[str, int],
) -> dict[str, _JSONValue]:
    resolver = mock._data_resolver
    rels: dict[str, _JSONValue] = {}

    albums_block = _paginated_relationship_block(
        f"/v1/catalog/{sf}/music-videos/{music_video_id}/albums",
        music_video.album_ids,
        sizes["albums"],
        resolver=lambda aid: resolver.album.get(LookupContext(aid, locale)),
        encode=lambda aid, al: _album_resource(sf, aid, al),
        fallback_ref=lambda aid: _catalog_ref(sf, "albums", aid),
        include_full="albums" in includes,
    )
    if albums_block is not None:
        rels["albums"] = albums_block

    artists_block = _paginated_relationship_block(
        f"/v1/catalog/{sf}/music-videos/{music_video_id}/artists",
        music_video.artist_ids,
        sizes["artists"],
        resolver=lambda aid: resolver.artist.get(LookupContext(aid, locale)),
        encode=lambda aid, ar: _artist_resource(sf, aid, ar),
        fallback_ref=lambda aid: _catalog_ref(sf, "artists", aid),
        include_full="artists" in includes,
    )
    if artists_block is not None:
        rels["artists"] = artists_block

    if "library" in includes and music_video.library_music_video_id is not None:
        library_music_video = resolver.library_music_video.get(
            LookupContext(music_video.library_music_video_id, locale)
        )
        if library_music_video is not None:
            rels["library"] = _singleton_relationship_block(
                f"/v1/catalog/{sf}/music-videos/{music_video_id}/library",
                [
                    _library_music_video_resource(
                        music_video.library_music_video_id, library_music_video
                    )
                ],
            )

    if "genres" in includes:
        genres_block = _paginated_relationship_block(
            f"/v1/catalog/{sf}/music-videos/{music_video_id}/genres",
            music_video.genre_ids,
            sizes.get("genres", _CATALOG_MUSIC_VIDEO_GENRES.page_size),
            resolver=lambda gid: resolver.genre.get(LookupContext(gid, locale)),
            encode=lambda gid, g: _genre_resource(sf, gid, g),
            fallback_ref=lambda gid: _catalog_ref(sf, "genres", gid),
            include_full=True,
        )
        if genres_block is not None:
            rels["genres"] = genres_block

    if "songs" in includes:
        songs_block = _paginated_relationship_block(
            f"/v1/catalog/{sf}/music-videos/{music_video_id}/songs",
            music_video.song_ids,
            sizes.get("songs", _CATALOG_MUSIC_VIDEO_SONGS.page_size),
            resolver=lambda sid: resolver.song.get(LookupContext(sid, locale)),
            encode=lambda sid, sg: _song_resource(sf, sid, sg),
            fallback_ref=lambda sid: _catalog_ref(sf, "songs", sid),
            include_full=True,
        )
        if songs_block is not None:
            rels["songs"] = songs_block

    return rels


def _handle_songs(mock: MusicKitApiMock, req: Request, sf: str) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf)
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
        {
            "albums": _CATALOG_SONG_ALBUMS,
            "artists": _CATALOG_SONG_ARTISTS,
            "composers": _CATALOG_SONG_COMPOSERS,
        },
    )
    if err is not None:
        return err
    resolver = mock._data_resolver
    resources: list[dict[str, _JSONValue]] = []
    for song_id in _dedupe(ids):
        song = resolver.song.get(LookupContext(song_id, locale))
        if song is None:
            continue
        rels = _build_song_rels(
            mock, sf, song_id, song, locale=locale, includes=includes, sizes=sizes
        )
        resources.append(_song_resource(sf, song_id, song, relationships=rels or None))
    return _json_response(_batch_envelope(resources))


def _handle_albums(mock: MusicKitApiMock, req: Request, sf: str) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf)
    if err is not None:
        return err
    has_param, ids = _parse_ids(req.url)
    if not has_param:
        return _json_response(_missing_ids_param_400_envelope(), status=400)
    if not ids:
        return _json_response(_empty_ids_400_envelope(), status=400)
    includes = _parse_csv_param(req.url, "include")
    extends = _parse_csv_param(req.url, "extend")
    sizes, err = _parse_inline_limits(
        req,
        {
            "tracks": _CATALOG_ALBUM_TRACKS,
            "artists": _CATALOG_ALBUM_ARTISTS,
        },
    )
    if err is not None:
        return err
    resolver = mock._data_resolver
    resources: list[dict[str, _JSONValue]] = []
    for album_id in _dedupe(ids):
        album = resolver.album.get(LookupContext(album_id, locale))
        if album is None:
            continue
        rels = _build_album_rels(
            mock, sf, album_id, album, locale=locale, includes=includes, sizes=sizes
        )
        resources.append(
            _album_resource(
                sf,
                album_id,
                album,
                relationships=rels or None,
                extend_editorial_artwork="editorialArtwork" in extends,
            )
        )
    return _json_response(_batch_envelope(resources))


def _handle_playlists(mock: MusicKitApiMock, req: Request, sf: str) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf)
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
        {"tracks": _CATALOG_PLAYLIST_TRACKS},
    )
    if err is not None:
        return err
    resolver = mock._data_resolver
    resources: list[dict[str, _JSONValue]] = []
    for playlist_id in _dedupe(ids):
        playlist = resolver.playlist.get(LookupContext(playlist_id, locale))
        if playlist is None:
            continue
        rels = _build_playlist_rels(
            mock,
            sf,
            playlist_id,
            playlist,
            locale=locale,
            includes=includes,
            sizes=sizes,
        )
        resources.append(
            _playlist_resource(sf, playlist_id, playlist, relationships=rels or None)
        )
    return _json_response(_batch_envelope(resources))


def _handle_artists(mock: MusicKitApiMock, req: Request, sf: str) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf)
    if err is not None:
        return err
    has_param, ids = _parse_ids(req.url)
    if not has_param:
        return _json_response(_missing_ids_param_400_envelope(), status=400)
    if not ids:
        return _json_response(_empty_ids_400_envelope(), status=400)
    includes = _parse_csv_param(req.url, "include")
    sizes, err = _parse_inline_limits(req, {"albums": _ARTIST_ALBUMS})
    if err is not None:
        return err
    resolver = mock._data_resolver
    resources: list[dict[str, _JSONValue]] = []
    for artist_id in _dedupe(ids):
        artist = resolver.artist.get(LookupContext(artist_id, locale))
        if artist is None:
            continue
        rels = _build_artist_rels(
            mock,
            sf,
            artist_id,
            artist,
            locale=locale,
            includes=includes,
            sizes=sizes,
        )
        resources.append(
            _artist_resource(sf, artist_id, artist, relationships=rels or None)
        )
    return _json_response(_batch_envelope(resources))


def _handle_music_videos(mock: MusicKitApiMock, req: Request, sf: str) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf)
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
        {
            "albums": _CATALOG_MUSIC_VIDEO_ALBUMS,
            "artists": _CATALOG_MUSIC_VIDEO_ARTISTS,
        },
    )
    if err is not None:
        return err
    resolver = mock._data_resolver
    resources: list[dict[str, _JSONValue]] = []
    for music_video_id in _dedupe(ids):
        music_video = resolver.music_video.get(LookupContext(music_video_id, locale))
        if music_video is None:
            continue
        rels = _build_music_video_rels(
            mock,
            sf,
            music_video_id,
            music_video,
            locale=locale,
            includes=includes,
            sizes=sizes,
        )
        resources.append(
            _music_video_resource(
                sf, music_video_id, music_video, relationships=rels or None
            )
        )
    return _json_response(_batch_envelope(resources))


def _handle_stations(mock: MusicKitApiMock, req: Request, sf: str) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf)
    if err is not None:
        return err
    has_param, ids = _parse_ids(req.url)
    if not has_param:
        return _json_response(_missing_ids_param_400_envelope(), status=400)
    if not ids:
        return _json_response(_empty_ids_400_envelope(), status=400)
    resolver = mock._data_resolver
    resources: list[dict[str, _JSONValue]] = []
    for station_id in _dedupe(ids):
        station = resolver.station.get(LookupContext(station_id, locale))
        if station is None:
            continue
        resources.append(_station_resource(sf, station_id, station))
    return _json_response(_batch_envelope(resources))


def _build_station_rels(
    mock: MusicKitApiMock,
    sf: str,
    station_id: str,
    station: Station,
    *,
    locale: str | None,
    includes: set[str],
) -> dict[str, _JSONValue]:
    resolver = mock._data_resolver
    rels: dict[str, _JSONValue] = {}
    if "radio-show" in includes:
        href = f"/v1/catalog/{sf}/stations/{station_id}/radio-show"
        data: list[dict[str, _JSONValue]] = []
        if station.radio_show_id is not None:
            curator = resolver.curator.get(LookupContext(station.radio_show_id, locale))
            if curator is not None:
                data.append(_curator_resource(sf, station.radio_show_id, curator))
        rels["radio-show"] = _singleton_relationship_block(href, data)
    return rels


def _handle_station_singular(
    mock: MusicKitApiMock, req: Request, sf: str, station_id: str
) -> Response:
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf)
    if err is not None:
        return err
    includes = _parse_csv_param(req.url, "include")
    station = mock._data_resolver.station.get(LookupContext(station_id, locale))
    if station is None:
        return _json_response({"data": []})
    rels = _build_station_rels(
        mock, sf, station_id, station, locale=locale, includes=includes
    )
    return _json_response(
        _batch_envelope(
            [_station_resource(sf, station_id, station, relationships=rels or None)]
        )
    )


def _handle_song_singular(
    mock: MusicKitApiMock, req: Request, sf: str, song_id: str
) -> Response:
    """``/v1/catalog/<sf>/songs/<song_id>`` — single-resource endpoint.

    Apple wraps the single resource in a one-entry ``data`` array. Default
    emits ``relationships.albums`` + ``relationships.artists``;
    ``?include=composers`` adds the composers relation.
    """
    locale, err = _check_and_resolve_locale(req, storefront_slug=sf)
    if err is not None:
        return err
    includes = _parse_csv_param(req.url, "include")
    sizes, err = _parse_inline_limits(
        req,
        {
            "albums": _CATALOG_SONG_ALBUMS,
            "artists": _CATALOG_SONG_ARTISTS,
            "composers": _CATALOG_SONG_COMPOSERS,
        },
    )
    if err is not None:
        return err
    song = mock._data_resolver.song.get(LookupContext(song_id, locale))
    if song is None:
        return _json_response({"data": []})
    rels = _build_song_rels(
        mock, sf, song_id, song, locale=locale, includes=includes, sizes=sizes
    )
    return _json_response(
        _batch_envelope([_song_resource(sf, song_id, song, relationships=rels or None)])
    )


def _handle_unsupported_kind() -> Response:
    return _json_response({"errors": []}, status=404)
