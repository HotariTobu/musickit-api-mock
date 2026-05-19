"""Coverage-gap tests for endpoints added in the v0.2 round.

Companion to ``test_new_relationships.py`` (per-endpoint smoke tests):
this file covers behavior axes the smoke tests skip — pagination,
limit-overflow 400 envelope, missing-target None branches, inline
``?include=<rel>`` variants, full attribute shape, and zero-test
endpoints that the smoke pass missed.
"""

from __future__ import annotations

import json
from dataclasses import replace
from typing import TYPE_CHECKING, cast

from musickit_api_mock import (
    Album,
    Artist,
    Artwork,
    Curator,
    Description,
    Genre,
    Grouping,
    LibraryArtist,
    MusicKitApiMock,
    MusicVideo,
    Playlist,
    RecordLabel,
    Request,
    Song,
    Station,
)

if TYPE_CHECKING:
    from musickit_api_mock.json_value import _JSONValue

    from tests._apple_response import _AppleResponse


def _get(mock: MusicKitApiMock, url: str) -> tuple[int, _AppleResponse]:
    resp = mock.handle_request(Request(method="GET", url=url, headers={}, body=None))
    assert resp is not None
    return resp.status, json.loads(resp.body)


def _songs(mock: MusicKitApiMock) -> dict[str, Song]:
    return cast("dict[str, Song]", mock.data.songs)


def _albums(mock: MusicKitApiMock) -> dict[str, Album]:
    return cast("dict[str, Album]", mock.data.albums)


def _artists(mock: MusicKitApiMock) -> dict[str, Artist]:
    return cast("dict[str, Artist]", mock.data.artists)


def _music_videos(mock: MusicKitApiMock) -> dict[str, MusicVideo]:
    return cast("dict[str, MusicVideo]", mock.data.music_videos)


def _stations(mock: MusicKitApiMock) -> dict[str, Station]:
    return cast("dict[str, Station]", mock.data.stations)


def _curators(mock: MusicKitApiMock) -> dict[str, Curator]:
    return cast("dict[str, Curator]", mock.data.curators)


def _library_artists(mock: MusicKitApiMock) -> dict[str, LibraryArtist]:
    return cast("dict[str, LibraryArtist]", mock.data.library_artists)


def test_song_music_videos_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/songs/1/music-videos",
    )
    assert status == 200
    assert [x["id"] for x in body["data"]] == ["mv1"]
    assert body["data"][0]["type"] == "music-videos"


def test_album_genres_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/albums/a1/genres"
    )
    assert status == 200
    assert [x["id"] for x in body["data"]] == ["20"]


def test_artist_genres_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/artists/ar1/genres"
    )
    assert status == 200
    assert [x["id"] for x in body["data"]] == ["20"]


def test_music_video_genres_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/music-videos/mv1/genres",
    )
    assert status == 200
    assert [x["id"] for x in body["data"]] == ["20"]


def test_non_apple_curator_singular(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/curators/cu2")
    assert status == 200
    assert body["data"][0]["type"] == "curators"
    assert body["data"][0]["id"] == "cu2"
    rels = body["data"][0]["relationships"]
    assert rels["playlists"]["data"][0]["id"] == "pl1"
    assert "grouping" not in rels


def test_non_apple_curator_playlists_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/curators/cu2/playlists",
    )
    assert status == 200
    assert [x["id"] for x in body["data"]] == ["pl1"]


def test_song_inline_include_station(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/songs/1?include=station",
    )
    assert status == 200
    rels = body["data"][0]["relationships"]
    assert rels["station"]["data"][0]["type"] == "stations"
    assert rels["station"]["data"][0]["id"] == "ra.978194965"


def test_song_inline_include_music_videos(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/songs/1?include=music-videos",
    )
    assert status == 200
    rels = body["data"][0]["relationships"]
    assert rels["music-videos"]["data"][0]["id"] == "mv1"


def test_album_inline_include_genres(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/albums?ids=a1&include=genres",
    )
    assert status == 200
    rels = body["data"][0]["relationships"]
    assert rels["genres"]["data"][0]["id"] == "20"


def test_artist_inline_include_genres(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/artists?ids=ar1&include=genres",
    )
    assert status == 200
    rels = body["data"][0]["relationships"]
    assert rels["genres"]["data"][0]["id"] == "20"


def test_artist_inline_include_music_videos(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/artists?ids=ar1&include=music-videos",
    )
    assert status == 200
    rels = body["data"][0]["relationships"]
    assert rels["music-videos"]["data"][0]["id"] == "mv1"


def test_artist_inline_include_playlists(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/artists?ids=ar1&include=playlists",
    )
    assert status == 200
    rels = body["data"][0]["relationships"]
    assert rels["playlists"]["data"][0]["id"] == "pl1"


def test_artist_inline_include_station(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/artists?ids=ar1&include=station",
    )
    assert status == 200
    rels = body["data"][0]["relationships"]
    assert rels["station"]["data"][0]["id"] == "ra.978194965"


def test_music_video_inline_include_genres(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/music-videos?ids=mv1&include=genres",
    )
    assert status == 200
    rels = body["data"][0]["relationships"]
    assert rels["genres"]["data"][0]["id"] == "20"


def test_music_video_inline_include_songs(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/music-videos?ids=mv1&include=songs",
    )
    assert status == 200
    rels = body["data"][0]["relationships"]
    assert rels["songs"]["data"][0]["id"] == "1"


def test_music_video_inline_include_library(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/music-videos?ids=mv1&include=library",
    )
    assert status == 200
    rels = body["data"][0]["relationships"]
    assert rels["library"]["data"][0]["type"] == "library-music-videos"
    assert rels["library"]["data"][0]["id"] == "i.mv1"


def test_playlist_inline_include_library(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/playlists?ids=pl1&include=library",
    )
    assert status == 200
    rels = body["data"][0]["relationships"]
    assert rels["library"]["data"][0]["type"] == "library-playlists"
    assert rels["library"]["data"][0]["id"] == "p.pl1"


def test_library_song_inline_include_artists(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/songs/i.s1?include=artists",
    )
    assert status == 200
    rels = body["data"][0]["relationships"]
    assert rels["artists"]["data"][0]["id"] == "r.ar1"


def test_library_song_inline_include_catalog(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/songs/i.s1?include=catalog",
    )
    assert status == 200
    rels = body["data"][0]["relationships"]
    assert rels["catalog"]["data"][0]["type"] == "songs"
    assert rels["catalog"]["data"][0]["id"] == "1"


def test_library_music_video_inline_include_catalog(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/music-videos/i.mv1?include=catalog",
    )
    assert status == 200
    rels = body["data"][0]["relationships"]
    assert rels["catalog"]["data"][0]["type"] == "music-videos"
    assert rels["catalog"]["data"][0]["id"] == "mv1"


def test_library_playlist_inline_include_catalog(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/playlists/p.pl1?include=catalog",
    )
    assert status == 200
    rels = body["data"][0]["relationships"]
    assert rels["catalog"]["data"][0]["type"] == "playlists"
    assert rels["catalog"]["data"][0]["id"] == "pl1"


def test_apple_curator_inline_include_playlists(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/apple-curators/cu1?include=playlists",
    )
    assert status == 200
    rels = body["data"][0]["relationships"]
    playlist_item = rels["playlists"]["data"][0]
    assert playlist_item["type"] == "playlists"
    assert playlist_item["id"] == "pl1"
    assert "attributes" in playlist_item


def test_artist_playlists_limit_overflow_returns_400(
    mock: MusicKitApiMock,
) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/artists/ar1/playlists?limit=99",
    )
    assert status == 400
    assert body["errors"][0]["status"] == "400"


def test_artist_albums_limit_overflow_paginated(mock: MusicKitApiMock) -> None:
    status, _ = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/artists/r.ar1/albums?limit=999",
    )
    assert status == 400


def test_artist_playlists_paginated_with_offset(mock: MusicKitApiMock) -> None:
    # 12 playlists, page_size=10 default, offset=10 returns last 2
    pl_ids = [f"pl{i}" for i in range(1, 13)]
    pls = {
        pid: Playlist(
            name=pid,
            playlist_type="editorial",
            curator_name="C",
            has_collaboration=False,
            is_chart=False,
            audio_traits=[],
            supports_sing=False,
            url=f"https://music.apple.com/us/playlist/{pid}",
        )
        for pid in pl_ids
    }
    mock.data.playlists = pls
    artist = next(iter(_artists(mock).values()))
    new_artist = replace(artist, playlist_ids=pl_ids)
    mock.data.artists = {"ar1": new_artist}
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/artists/ar1/playlists?offset=10",
    )
    assert status == 200
    # default page_size=10, but the slice starts at offset 10 → returns ids 11..12
    assert [x["id"] for x in body["data"]] == ["pl11", "pl12"]


def test_artist_playlists_emits_next_link_when_more(mock: MusicKitApiMock) -> None:
    pl_ids = [f"pl{i}" for i in range(1, 13)]
    pls = {
        pid: Playlist(
            name=pid,
            playlist_type="editorial",
            curator_name="C",
            has_collaboration=False,
            is_chart=False,
            audio_traits=[],
            supports_sing=False,
            url=f"https://music.apple.com/us/playlist/{pid}",
        )
        for pid in pl_ids
    }
    mock.data.playlists = pls
    artist = next(iter(_artists(mock).values()))
    mock.data.artists = {"ar1": replace(artist, playlist_ids=pl_ids)}
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/artists/ar1/playlists",
    )
    assert status == 200
    assert body["next"] == "/v1/catalog/us/artists/ar1/playlists?offset=10"


def test_library_artist_albums_accepts_inline_limit(
    mock: MusicKitApiMock,
) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/artists/r.ar1/albums?limit=50",
    )
    assert status == 200
    assert [x["id"] for x in body["data"]] == ["l.a1"]


def test_song_library_returns_empty_when_library_song_id_is_none(
    mock: MusicKitApiMock,
) -> None:
    song = _songs(mock)["1"]
    assert isinstance(song, Song)
    mock.data.songs = {"1": replace(song, library_song_id=None)}
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs/1/library"
    )
    assert status == 200
    assert body["data"] == []


def test_song_station_returns_empty_when_station_id_is_none(
    mock: MusicKitApiMock,
) -> None:
    song = _songs(mock)["1"]
    assert isinstance(song, Song)
    mock.data.songs = {"1": replace(song, station_id=None)}
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs/1/station"
    )
    assert status == 200
    assert body["data"] == []


def test_album_library_returns_empty_when_library_album_id_is_none(
    mock: MusicKitApiMock,
) -> None:
    album = _albums(mock)["a1"]
    assert isinstance(album, Album)
    mock.data.albums = {"a1": replace(album, library_album_id=None)}
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/albums/a1/library"
    )
    assert status == 200
    assert body["data"] == []


def test_artist_station_returns_empty_when_station_id_is_none(
    mock: MusicKitApiMock,
) -> None:
    artist = _artists(mock)["ar1"]
    assert isinstance(artist, Artist)
    mock.data.artists = {"ar1": replace(artist, station_id=None)}
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/artists/ar1/station"
    )
    assert status == 200
    assert body["data"] == []


def test_music_video_library_returns_empty_when_id_is_none(
    mock: MusicKitApiMock,
) -> None:
    mv = _music_videos(mock)["mv1"]
    assert isinstance(mv, MusicVideo)
    mock.data.music_videos = {"mv1": replace(mv, library_music_video_id=None)}
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/music-videos/mv1/library",
    )
    assert status == 200
    assert body["data"] == []


def test_station_radio_show_returns_empty_when_id_is_none(
    mock: MusicKitApiMock,
) -> None:
    st = _stations(mock)["ra.978194965"]
    assert isinstance(st, Station)
    mock.data.stations = {"ra.978194965": replace(st, radio_show_id=None)}
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/stations/ra.978194965/radio-show",
    )
    assert status == 200
    assert body["data"] == []


def test_apple_curator_grouping_empty_when_grouping_id_is_none(
    mock: MusicKitApiMock,
) -> None:
    cu = _curators(mock)["cu1"]
    assert isinstance(cu, Curator)
    mock.data.curators = {"cu1": replace(cu, grouping_id=None), "cu2": cu}
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/apple-curators/cu1/grouping",
    )
    assert status == 200
    assert body["data"] == []


def test_library_artist_albums_empty_when_album_ids_none(
    mock: MusicKitApiMock,
) -> None:
    la = _library_artists(mock)["r.ar1"]
    mock.data.library_artists = {"r.ar1": replace(la, album_ids=None)}
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/artists/r.ar1/albums"
    )
    assert status == 200
    assert body["data"] == []


def test_library_artist_catalog_empty_when_catalog_id_none(
    mock: MusicKitApiMock,
) -> None:
    la = _library_artists(mock)["r.ar1"]
    mock.data.library_artists = {"r.ar1": replace(la, catalog_id=None)}
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/library/artists/r.ar1/catalog"
    )
    assert status == 200
    assert body["data"] == []


def test_song_genres_empty_when_genre_ids_none(mock: MusicKitApiMock) -> None:
    song = _songs(mock)["1"]
    assert isinstance(song, Song)
    mock.data.songs = {"1": replace(song, genre_ids=None)}
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs/1/genres"
    )
    assert status == 200
    assert body["data"] == []


def test_song_library_missing_parent_song_returns_empty(
    mock: MusicKitApiMock,
) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs/nonexistent/library"
    )
    assert status == 200
    assert body["data"] == []


def test_recommendation_singular_missing_returns_empty(
    mock: MusicKitApiMock,
) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/me/recommendations/nonexistent"
    )
    assert status == 200
    assert body["data"] == []


def test_genres_batch_missing_id_filtered_out(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/genres?ids=20,nonexistent",
    )
    assert status == 200
    assert [x["id"] for x in body["data"]] == ["20"]


def test_genre_attributes_full_shape(mock: MusicKitApiMock) -> None:
    _, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/genres/20")
    attrs = body["data"][0]["attributes"]
    assert attrs["name"] == "Pop"
    assert attrs["url"] == "https://music.apple.com/us/genre/20"
    assert attrs["parentId"] == "34"
    assert attrs["parentName"] == "Music"


def test_genre_attributes_omit_optional_when_none(mock: MusicKitApiMock) -> None:
    mock.data.genres = {"5": Genre(name="X", url="https://music.apple.com/us/genre/5")}
    _, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/genres/5")
    attrs = body["data"][0]["attributes"]
    assert "parentId" not in attrs
    assert "parentName" not in attrs


def test_record_label_full_attributes(mock: MusicKitApiMock) -> None:
    art = Artwork(url="https://example.com/rl.jpg", width=400, height=400)
    desc = Description(standard="A great label.", short="A label")
    mock.data.record_labels = {
        "rl1": RecordLabel(
            name="Indie",
            url="https://music.apple.com/us/record-label/rl1",
            artwork=art,
            description=desc,
        )
    }
    _, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/record-labels/rl1")
    attrs = body["data"][0]["attributes"]
    assert attrs["name"] == "Indie"
    assert attrs["url"] == "https://music.apple.com/us/record-label/rl1"
    artwork = cast("dict[str, _JSONValue]", attrs["artwork"])
    assert artwork["url"] == "https://example.com/rl.jpg"
    description = cast("dict[str, _JSONValue]", attrs["description"])
    assert description["standard"] == "A great label."
    assert description["short"] == "A label"


def test_grouping_with_artwork_emits_artwork(mock: MusicKitApiMock) -> None:
    art = Artwork(url="https://example.com/gp.jpg", width=300, height=300)
    mock.data.groupings = {
        "gp1": Grouping(
            name="Curators",
            url="https://music.apple.com/us/grouping/gp1",
            artwork=art,
        )
    }
    _, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/apple-curators/cu1/grouping",
    )
    attrs = body["data"][0]["attributes"]
    artwork = cast("dict[str, _JSONValue]", attrs["artwork"])
    assert artwork["url"] == "https://example.com/gp.jpg"
    assert attrs["name"] == "Curators"


def test_curator_attributes_emit_kind_and_short_name(mock: MusicKitApiMock) -> None:
    _, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/apple-curators/cu1")
    attrs = body["data"][0]["attributes"]
    assert attrs["name"] == "Apple Music Pop"
    assert attrs["kind"] == "Genre"
    assert attrs["shortName"] == "Pop"


def test_non_apple_curator_omits_short_name_and_kind(
    mock: MusicKitApiMock,
) -> None:
    _, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/curators/cu2")
    attrs = body["data"][0]["attributes"]
    assert attrs["name"] == "Third Party Curator"
    assert "shortName" not in attrs
    assert "kind" not in attrs


def test_song_library_response_uses_singular_data_shape(
    mock: MusicKitApiMock,
) -> None:
    """Singular cross-rel returns ``{data: [single_item]}`` — 1-entry list, no next/meta."""
    _, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/songs/1/library")
    assert isinstance(body["data"], list)
    assert len(body["data"]) == 1
    assert "next" not in body
    assert "meta" not in body


def test_paginated_endpoint_has_data_array(mock: MusicKitApiMock) -> None:
    """Paginated rel endpoint returns ``{data: [items], next?: str}`` shape."""
    _, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/songs/1/genres")
    assert isinstance(body["data"], list)


# F. Locale (?l=) handling for new endpoints


def test_song_library_invalid_language_tag_400(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/songs/1/library?l=invalid-XX",
    )
    assert status == 400
    err = body["errors"][0]
    assert err["code"] == "40005"
    assert err["source"] == {"parameter": "l"}


def test_song_genres_valid_language_tag_passes(mock: MusicKitApiMock) -> None:
    status, _ = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/songs/1/genres?l=ja-JP",
    )
    assert status == 200


def test_apple_curator_singular_invalid_language_tag_400(
    mock: MusicKitApiMock,
) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/apple-curators/cu1?l=bogus",
    )
    assert status == 400
    assert body["errors"][0]["code"] == "40005"


def test_recommendation_singular_invalid_language_tag_400(
    mock: MusicKitApiMock,
) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/me/recommendations/rec1?l=zz-ZZ-bogus",
    )
    assert status == 400
    assert body["errors"][0]["code"] == "40005"


def test_genres_batch_invalid_language_tag_400(mock: MusicKitApiMock) -> None:
    status, _ = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/genres?l=invalid-XX",
    )
    assert status == 400


def test_library_song_albums_invalid_language_tag_400(
    mock: MusicKitApiMock,
) -> None:
    status, _ = _get(
        mock,
        "https://api.music.apple.com/v1/me/library/songs/i.s1/albums?l=invalid-XX",
    )
    assert status == 400


def test_song_genres_callable_resolver_threads_locale(
    mock: MusicKitApiMock,
) -> None:
    from musickit_api_mock import LookupContext

    seen: list[str | None] = []

    def genre_callable(ctx: LookupContext) -> Genre | None:
        seen.append(ctx.locale)
        if ctx.id != "20":
            return None
        return Genre(name="Pop", url="https://music.apple.com/us/genre/20")

    mock.data.genres = genre_callable
    _, _ = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/songs/1/genres?l=ja-JP",
    )
    assert "ja-JP" in seen


# G. Callable source variant for new resources


def test_genre_singular_works_with_callable_source(
    mock: MusicKitApiMock,
) -> None:
    from musickit_api_mock import LookupContext

    def callable_source(ctx: LookupContext) -> Genre | None:
        if ctx.id != "99":
            return None
        return Genre(name="Jazz", url="https://music.apple.com/us/genre/99")

    mock.data.genres = callable_source
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/genres/99")
    assert status == 200
    assert body["data"][0]["attributes"]["name"] == "Jazz"


def test_record_label_singular_works_with_callable_source(
    mock: MusicKitApiMock,
) -> None:
    from musickit_api_mock import LookupContext

    def callable_source(ctx: LookupContext) -> RecordLabel | None:
        if ctx.id != "rl99":
            return None
        return RecordLabel(
            name="Big",
            url="https://music.apple.com/us/record-label/rl99",
        )

    mock.data.record_labels = callable_source
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/record-labels/rl99"
    )
    assert status == 200
    assert body["data"][0]["attributes"]["name"] == "Big"


def test_recommendation_singular_works_with_callable_source(
    mock: MusicKitApiMock,
) -> None:
    from musickit_api_mock import LookupContext, PersonalRecommendation

    def callable_source(
        ctx: LookupContext,
    ) -> PersonalRecommendation | None:
        if ctx.id != "rec99":
            return None
        return PersonalRecommendation(
            title="From Callable",
            is_group_recommendation=False,
            kind="music-recommendations",
        )

    mock.data.personal_recommendations = callable_source
    status, body = _get(mock, "https://api.music.apple.com/v1/me/recommendations/rec99")
    assert status == 200
    title = cast("dict[str, _JSONValue]", body["data"][0]["attributes"]["title"])
    assert title["stringForDisplay"] == "From Callable"


def test_recommendations_batch_with_callable_source_raises_on_list_all(
    mock: MusicKitApiMock,
) -> None:
    import pytest
    from musickit_api_mock import LookupContext, PersonalRecommendation

    def callable_source(
        _ctx: LookupContext,
    ) -> PersonalRecommendation | None:
        return None

    mock.data.personal_recommendations = callable_source
    with pytest.raises(ValueError, match="callable source"):
        _get(mock, "https://api.music.apple.com/v1/me/recommendations")


def test_genres_batch_with_callable_source_raises_on_list_all(
    mock: MusicKitApiMock,
) -> None:
    import pytest
    from musickit_api_mock import LookupContext

    def callable_source(_ctx: LookupContext) -> Genre | None:
        return None

    mock.data.genres = callable_source
    with pytest.raises(ValueError, match="callable source"):
        _get(mock, "https://api.music.apple.com/v1/catalog/us/genres")


def test_apple_curator_works_with_callable_source(mock: MusicKitApiMock) -> None:
    from musickit_api_mock import LookupContext

    def callable_source(ctx: LookupContext) -> Curator | None:
        if ctx.id != "cu99":
            return None
        return Curator(
            name="From Callable",
            type="apple-curators",
            url="https://music.apple.com/us/curator/from-callable/cu99",
            artwork=Artwork(url="https://example.com/c.jpg", width=300, height=300),
            playlist_ids=["pl1"],
        )

    mock.data.curators = callable_source
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/apple-curators/cu99"
    )
    assert status == 200
    assert body["data"][0]["attributes"]["name"] == "From Callable"


def test_grouping_works_with_callable_source(mock: MusicKitApiMock) -> None:
    from musickit_api_mock import LookupContext

    def grouping_source(ctx: LookupContext) -> Grouping | None:
        if ctx.id != "gp1":
            return None
        return Grouping(
            name="GroupedCallable",
            url="https://music.apple.com/us/grouping/gp1",
        )

    mock.data.groupings = grouping_source
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/apple-curators/cu1/grouping",
    )
    assert status == 200
    assert body["data"][0]["attributes"]["name"] == "GroupedCallable"


def test_recommendations_batch_empty_ids_returns_400(
    mock: MusicKitApiMock,
) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/me/recommendations?ids=")
    assert status == 400
    err = cast("dict[str, _JSONValue]", body["errors"][0])
    assert err["code"] == "40005"
    source = cast("dict[str, _JSONValue]", err["source"])
    assert source["parameter"] == "ids"


def test_genres_batch_empty_ids_returns_400(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/genres?ids=")
    assert status == 400
    err = cast("dict[str, _JSONValue]", body["errors"][0])
    assert err["code"] == "40005"
    source = cast("dict[str, _JSONValue]", err["source"])
    assert source["parameter"] == "ids"


def test_record_labels_batch_empty_ids_returns_400(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/record-labels?ids="
    )
    assert status == 400
    err = cast("dict[str, _JSONValue]", body["errors"][0])
    assert err["code"] == "40005"
    source = cast("dict[str, _JSONValue]", err["source"])
    assert source["parameter"] == "ids"


def test_apple_curator_singular_type_mismatch_returns_404(
    mock: MusicKitApiMock,
) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/apple-curators/cu2"
    )
    assert status == 404
    err = cast("dict[str, _JSONValue]", body["errors"][0])
    assert err["code"] == "40400"


def test_curator_singular_type_mismatch_returns_404(
    mock: MusicKitApiMock,
) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/curators/cu1")
    assert status == 404
    err = cast("dict[str, _JSONValue]", body["errors"][0])
    assert err["code"] == "40400"


def test_apple_curator_singular_missing_id_returns_404(
    mock: MusicKitApiMock,
) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/apple-curators/nonexistent",
    )
    assert status == 404
    err = cast("dict[str, _JSONValue]", body["errors"][0])
    assert err["code"] == "40400"


def test_station_singular_bare_emits_no_relationships(
    mock: MusicKitApiMock,
) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/stations/ra.978194965"
    )
    assert status == 200
    resource = cast("dict[str, _JSONValue]", body["data"][0])
    assert resource["type"] == "stations"
    assert resource["id"] == "ra.978194965"
    assert "relationships" not in resource


def test_station_singular_include_radio_show_emits_relationships_block(
    mock: MusicKitApiMock,
) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/stations/ra.978194965?include=radio-show",
    )
    assert status == 200
    rels = cast(
        "dict[str, _JSONValue]",
        cast("dict[str, _JSONValue]", body["data"][0])["relationships"],
    )
    radio_show = cast("dict[str, _JSONValue]", rels["radio-show"])
    assert radio_show["href"] == "/v1/catalog/us/stations/ra.978194965/radio-show"
    data = cast("list[_JSONValue]", radio_show["data"])
    item = cast("dict[str, _JSONValue]", data[0])
    assert item["type"] == "apple-curators"
    assert item["id"] == "cu1"


def test_station_singular_include_radio_show_empty_when_show_missing(
    mock: MusicKitApiMock,
) -> None:
    target = _stations(mock)["ra.978194965"]
    mock.data.stations = {
        "ra.978194965": replace(target, radio_show_id=None),
    }
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/stations/ra.978194965?include=radio-show",
    )
    assert status == 200
    rels = cast(
        "dict[str, _JSONValue]",
        cast("dict[str, _JSONValue]", body["data"][0])["relationships"],
    )
    radio_show = cast("dict[str, _JSONValue]", rels["radio-show"])
    assert radio_show["data"] == []


def test_recommendation_contents_mix_types(mock: MusicKitApiMock) -> None:
    """A single recommendation row can mix content types (probe-confirmed)."""
    from musickit_api_mock import (
        PersonalRecommendation,
        PersonalRecommendationContent,
    )

    mock.data.personal_recommendations = {
        "mixed": PersonalRecommendation(
            title="Recently Played",
            is_group_recommendation=False,
            kind="recently-played",
            contents=[
                PersonalRecommendationContent(type="playlists", id="pl1"),
                PersonalRecommendationContent(type="albums", id="a1"),
                PersonalRecommendationContent(type="stations", id="ra.978194965"),
            ],
        )
    }
    status, body = _get(mock, "https://api.music.apple.com/v1/me/recommendations/mixed")
    assert status == 200
    rels = cast(
        "dict[str, _JSONValue]",
        cast("dict[str, _JSONValue]", body["data"][0])["relationships"],
    )
    contents = cast("dict[str, _JSONValue]", rels["contents"])
    items = cast("list[_JSONValue]", contents["data"])
    types = [cast("dict[str, _JSONValue]", x)["type"] for x in items]
    ids = [cast("dict[str, _JSONValue]", x)["id"] for x in items]
    assert types == ["playlists", "albums", "stations"]
    assert ids == ["pl1", "a1", "ra.978194965"]


def test_recommendation_emits_display_attrs(mock: MusicKitApiMock) -> None:
    """display / hasSeeAll / version surface in attributes when set."""
    status, body = _get(mock, "https://api.music.apple.com/v1/me/recommendations/rec1")
    assert status == 200
    attrs = cast(
        "dict[str, _JSONValue]",
        cast("dict[str, _JSONValue]", body["data"][0])["attributes"],
    )
    display = cast("dict[str, _JSONValue]", attrs["display"])
    assert display["kind"] == "MusicCoverShelf"
    assert display["decorations"] == []
    assert attrs["hasSeeAll"] is False
    assert attrs["version"] == 2


def test_recommendation_kind_recently_played_accepted(
    mock: MusicKitApiMock,
) -> None:
    """``kind="recently-played"`` is accepted (probe-confirmed value)."""
    from musickit_api_mock import PersonalRecommendation

    mock.data.personal_recommendations = {
        "rec1": PersonalRecommendation(
            title="Recently",
            is_group_recommendation=False,
            kind="recently-played",
        )
    }
    status, body = _get(mock, "https://api.music.apple.com/v1/me/recommendations/rec1")
    assert status == 200
    attrs = cast(
        "dict[str, _JSONValue]",
        cast("dict[str, _JSONValue]", body["data"][0])["attributes"],
    )
    assert attrs["kind"] == "recently-played"


def test_repeated_limit_param_uses_last_value(mock: MusicKitApiMock) -> None:
    """Apple applies the last-occurrence value when ``?limit=`` is repeated."""
    target = _music_videos(mock)["mv1"]
    mock.data.music_videos = {
        "mv1": replace(target, song_ids=["1", "2", "3", "4", "5"]),
    }
    song1 = _songs(mock)["1"]
    mock.data.songs = {
        sid: replace(song1, library_song_id=None) for sid in ["1", "2", "3", "4", "5"]
    }
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/music-videos/mv1/songs?limit=1&limit=3",
    )
    assert status == 200
    assert len(cast("list[_JSONValue]", body["data"])) == 3
