"""Every id-keyed ``mock.data.*`` source accepts ``Callable[[LookupContext], T | None]``.

The data resolver layer is uniform across resource types: per-id lookup
runs through ``_lookup_source``, which dispatches dict / callable / None
the same way for every resource. ``test_catalog.py`` covers the songs +
artists callable forms and the locale-thread case for albums; this file
fills in the remaining resources so every public id-keyed
``mock.data.<field>`` surface has at least one callable-form test.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
from musickit_api_mock import (
    Account,
    AccountResponseSuccess,
    Artwork,
    Curator,
    LibraryAlbum,
    LibraryArtist,
    LibraryMusicVideo,
    LibraryPlaylist,
    LibraryPlaylistFolder,
    LibraryPlaylistFolderChild,
    LibrarySong,
    LookupContext,
    MusicKitApiMock,
    MusicVideo,
    Playlist,
    Preview,
    Request,
    Station,
    Storefront,
    StorefrontResponseSuccess,
    UploadedLibraryAlbum,
    UploadedLibraryArtist,
    UploadedLibrarySong,
)

if TYPE_CHECKING:
    from tests._apple_response import AppleResponse


def _get(mock: MusicKitApiMock, url: str) -> tuple[int, AppleResponse]:
    resp = mock.handle_request(Request(method="GET", url=url, headers={}, body=None))
    assert resp is not None
    return resp.status, json.loads(resp.body)


def _bare_mock() -> MusicKitApiMock:
    m = MusicKitApiMock()
    m.endpoints.storefront = StorefrontResponseSuccess(
        storefront=Storefront(
            id="us",
            name="US",
            default_language_tag="en-US",
            supported_language_tags=["en-US"],
            explicit_content_policy="allowed",
        )
    )
    m.endpoints.account = AccountResponseSuccess(
        account=Account(subscription_active=True, subscription_storefront="us")
    )
    return m


def _aw() -> Artwork:
    return Artwork(url="x", width=1, height=1)


def test_data_playlists_callable() -> None:
    m = _bare_mock()

    def resolver(ctx: LookupContext) -> Playlist | None:
        if ctx.id != "pl-x":
            return None
        return Playlist(
            name=f"PL {ctx.id}",
            playlist_type="user-shared",
            curator_name="C",
            has_collaboration=False,
            is_chart=False,
            audio_traits=[],
            supports_sing=False,
            url="x",
            artwork=_aw(),
            last_modified="2024-01-01",
        )

    m.data.playlists = resolver
    status, body = _get(
        m, "https://api.music.apple.com/v1/catalog/us/playlists?ids=pl-x"
    )
    assert status == 200
    assert body["data"][0]["attributes"]["name"] == "PL pl-x"


def test_data_music_videos_callable() -> None:
    m = _bare_mock()

    def resolver(ctx: LookupContext) -> MusicVideo | None:
        if ctx.id != "mv-x":
            return None
        return MusicVideo(
            name=f"MV {ctx.id}",
            artist_name="A",
            artwork=_aw(),
            duration_ms=1,
            genre_names=[],
            has_4k=False,
            has_hdr=False,
            isrc="X",
            release_date="2020-01-01",
            url="x",
            previews=[Preview(url="x")],
            video_traits=[],
        )

    m.data.music_videos = resolver
    status, body = _get(
        m, "https://api.music.apple.com/v1/catalog/us/music-videos?ids=mv-x"
    )
    assert status == 200
    assert body["data"][0]["attributes"]["name"] == "MV mv-x"


def test_data_stations_callable() -> None:
    m = _bare_mock()

    def resolver(ctx: LookupContext) -> Station | None:
        if ctx.id != "ra.x":
            return None
        return Station(
            name=f"S {ctx.id}",
            artwork=_aw(),
            is_live=True,
            media_kind="audio",
            url="x",
            is_tracks_station=False,
            has_drm=True,
            kind="radio",
            radio_url="x",
            requires_subscription=True,
        )

    m.data.stations = resolver
    status, body = _get(
        m, "https://api.music.apple.com/v1/catalog/us/stations?ids=ra.x"
    )
    assert status == 200
    assert body["data"][0]["attributes"]["name"] == "S ra.x"


def test_data_curators_callable() -> None:
    """``data.curators`` callable resolves the playlist's curator relationship."""
    m = _bare_mock()
    m.data.playlists = {
        "pl1": Playlist(
            name="PL",
            playlist_type="editorial",
            curator_name="C",
            has_collaboration=False,
            is_chart=False,
            audio_traits=[],
            supports_sing=False,
            url="x",
            artwork=_aw(),
            last_modified="2024-01-01",
            curator_id="cu-x",
        )
    }

    def resolver(ctx: LookupContext) -> Curator | None:
        if ctx.id != "cu-x":
            return None
        return Curator(
            name=f"Curator {ctx.id}",
            type="apple-curators",
            short_name="X",
            kind="Genre",
            url="x",
            artwork=_aw(),
        )

    m.data.curators = resolver
    status, body = _get(
        m,
        "https://api.music.apple.com/v1/catalog/us/playlists?ids=pl1&include=curator",
    )
    assert status == 200
    rels = body["data"][0]["relationships"]
    curator_data = rels["curator"]["data"][0]
    assert curator_data["id"] == "cu-x"
    assert curator_data["attributes"]["name"] == "Curator cu-x"


def test_data_library_songs_callable() -> None:
    m = _bare_mock()

    def resolver(ctx: LookupContext) -> LibrarySong | None:
        if ctx.id != "i.s-x":
            return None
        return UploadedLibrarySong(
            name=f"LS {ctx.id}",
            artist_name="A",
            artwork=_aw(),
            duration_ms=1,
            genre_names=[],
            has_lyrics=False,
            audio=b"",
            disc_number=0,
            track_number=0,
        )

    m.data.library_songs = resolver
    status, body = _get(m, "https://api.music.apple.com/v1/me/library/songs/i.s-x")
    assert status == 200
    assert body["data"][0]["attributes"]["name"] == "LS i.s-x"


def test_data_library_albums_callable() -> None:
    m = _bare_mock()

    def resolver(ctx: LookupContext) -> LibraryAlbum | None:
        if ctx.id != "l.a-x":
            return None
        return UploadedLibraryAlbum(
            name=f"LA {ctx.id}",
            artist_name="A",
            artwork=_aw(),
            genre_names=[],
            track_count=0,
        )

    m.data.library_albums = resolver
    status, body = _get(m, "https://api.music.apple.com/v1/me/library/albums/l.a-x")
    assert status == 200
    assert body["data"][0]["attributes"]["name"] == "LA l.a-x"


def test_data_library_playlists_callable() -> None:
    m = _bare_mock()

    def resolver(ctx: LookupContext) -> LibraryPlaylist | None:
        if ctx.id != "p.pl-x":
            return None
        return LibraryPlaylist(
            name=f"LPL {ctx.id}",
            can_edit=True,
            is_public=False,
            has_catalog=False,
        )

    m.data.library_playlists = resolver
    status, body = _get(m, "https://api.music.apple.com/v1/me/library/playlists/p.pl-x")
    assert status == 200
    assert body["data"][0]["attributes"]["name"] == "LPL p.pl-x"
    with pytest.raises(ValueError, match="require a mapping source"):
        m.handle_request(
            Request(
                method="GET",
                url="https://api.music.apple.com/v1/me/library/playlists",
                headers={},
                body=None,
            )
        )


def _library_playlist_folders_callable_mock() -> MusicKitApiMock:
    m = _bare_mock()
    folders = {
        "p.f-x": LibraryPlaylistFolder(
            name="LPF p.f-x",
            children=[
                LibraryPlaylistFolderChild(type="library-playlist-folders", id="p.f-y")
            ],
        ),
        "p.f-y": LibraryPlaylistFolder(name="LPF p.f-y"),
    }

    def resolver(ctx: LookupContext) -> LibraryPlaylistFolder | None:
        return folders.get(ctx.id)

    m.data.library_playlist_folders = resolver
    m.data.library_playlist_root_children = [
        LibraryPlaylistFolderChild(type="library-playlist-folders", id="p.f-x")
    ]
    return m


def _folder_resource(folder_id: str) -> dict[str, object]:
    return {
        "id": folder_id,
        "type": "library-playlist-folders",
        "href": f"/v1/me/library/playlist-folders/{folder_id}",
        "attributes": {"name": f"LPF {folder_id}"},
    }


def test_data_library_playlist_folders_callable() -> None:
    m = _library_playlist_folders_callable_mock()
    base = "https://api.music.apple.com/v1/me/library/playlist-folders"

    status, body = _get(m, f"{base}/p.f-x")
    assert status == 200
    assert body == {"data": [_folder_resource("p.f-x")]}

    status, body = _get(m, f"{base}?ids=p.f-x,p.f-y")
    assert status == 200
    assert body == {"data": [_folder_resource("p.f-x"), _folder_resource("p.f-y")]}

    status, body = _get(m, f"{base}/p.f-x/children")
    assert status == 200
    assert body == {"data": [_folder_resource("p.f-y")], "meta": {"total": 1}}

    status, body = _get(m, f"{base}/p.f-x/parent")
    assert status == 200
    assert body == {
        "data": [
            {
                "id": "p.playlistsroot",
                "type": "library-playlist-folders",
                "href": "/v1/me/library/playlist-folders/p.playlistsroot",
            }
        ],
        "meta": {"total": 1},
    }


@pytest.mark.parametrize(
    "path",
    [
        "/v1/me/library/playlist-folders",
        "/v1/me/library/playlist-folders/p.f-y/parent",
        "/v1/me/library/playlist-folders/p.f-y?include=parent",
    ],
)
def test_data_library_playlist_folders_callable_rejects_enumeration(path: str) -> None:
    m = _library_playlist_folders_callable_mock()
    with pytest.raises(ValueError, match="require a mapping source"):
        m.handle_request(
            Request(
                method="GET",
                url=f"https://api.music.apple.com{path}",
                headers={},
                body=None,
            )
        )


def test_data_library_artists_callable() -> None:
    m = _bare_mock()

    def resolver(ctx: LookupContext) -> LibraryArtist | None:
        if ctx.id != "r.ar-x":
            return None
        return UploadedLibraryArtist(name=f"LAR {ctx.id}")

    m.data.library_artists = resolver
    status, body = _get(m, "https://api.music.apple.com/v1/me/library/artists/r.ar-x")
    assert status == 200
    assert body["data"][0]["attributes"]["name"] == "LAR r.ar-x"


def test_data_library_music_videos_callable() -> None:
    m = _bare_mock()

    def resolver(ctx: LookupContext) -> LibraryMusicVideo | None:
        if ctx.id != "i.mv-x":
            return None
        return LibraryMusicVideo(
            name=f"LMV {ctx.id}",
            artist_name="A",
            artwork=_aw(),
            duration_ms=1,
            genre_names=[],
        )

    m.data.library_music_videos = resolver
    status, body = _get(
        m, "https://api.music.apple.com/v1/me/library/music-videos/i.mv-x"
    )
    assert status == 200
    assert body["data"][0]["attributes"]["name"] == "LMV i.mv-x"
