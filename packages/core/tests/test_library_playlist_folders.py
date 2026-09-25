from __future__ import annotations

import json
from dataclasses import replace
from typing import TYPE_CHECKING
from unittest.mock import ANY

import pytest
from musickit_api_mock import (
    Description,
    LibraryPlaylist,
    LibraryPlaylistFolder,
    LibraryPlaylistFolderChild,
    MusicKitApiMock,
    Playlist,
    Request,
    Storefront,
    StorefrontResponseSuccess,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from musickit_api_mock import CatalogSong, LibrarySong

_API = "https://api.music.apple.com"
_FOLDERS = "/v1/me/library/playlist-folders"


def _folder_child(item_id: str) -> LibraryPlaylistFolderChild:
    return LibraryPlaylistFolderChild(type="library-playlist-folders", id=item_id)


def _playlist_child(item_id: str) -> LibraryPlaylistFolderChild:
    return LibraryPlaylistFolderChild(type="library-playlists", id=item_id)


def _library_playlist(name: str, track_ids: list[str] | None = None) -> LibraryPlaylist:
    return LibraryPlaylist(
        name=name,
        can_edit=True,
        is_public=False,
        has_catalog=False,
        date_added="2024-01-01T00:00:00Z",
        last_modified_date="2024-01-02T00:00:00Z",
        track_ids=track_ids,
    )


@pytest.fixture
def mock(storefront: Storefront) -> MusicKitApiMock:
    m = MusicKitApiMock()
    m.endpoints.storefront = StorefrontResponseSuccess(storefront=storefront)
    m.data.library_playlists = {
        "p.pl1": _library_playlist("Top", track_ids=["i.s1", "i.s2"]),
        "p.pl2": _library_playlist("Inner"),
        "p.pl3": _library_playlist("Deep"),
    }
    m.data.library_playlist_folders = {
        "p.f1": LibraryPlaylistFolder(
            name="Outer",
            date_added="2023-01-01T00:00:00Z",
            children=[_folder_child("p.f2"), _playlist_child("p.pl2")],
        ),
        "p.f2": LibraryPlaylistFolder(
            name="Nested",
            date_added="2023-02-01T00:00:00Z",
            children=[_playlist_child("p.pl3")],
        ),
        "p.f3": LibraryPlaylistFolder(name="Empty", date_added="2023-03-01T00:00:00Z"),
    }
    m.data.library_playlist_root_children = [
        _folder_child("p.f1"),
        _playlist_child("p.pl1"),
        _folder_child("p.f3"),
    ]
    return m


def _get(mock: MusicKitApiMock, path: str) -> tuple[int, object]:
    resp = mock.handle_request(
        Request(method="GET", url=f"{_API}{path}", headers={}, body=None)
    )
    assert resp is not None
    return resp.status, json.loads(resp.body)


def _folder(
    folder_id: str,
    name: str,
    date_added: str,
    relationships: dict[str, object] | None = None,
) -> dict[str, object]:
    out: dict[str, object] = {
        "id": folder_id,
        "type": "library-playlist-folders",
        "href": f"{_FOLDERS}/{folder_id}",
        "attributes": {"name": name, "dateAdded": date_added},
    }
    if relationships is not None:
        out["relationships"] = relationships
    return out


_F1 = ("p.f1", "Outer", "2023-01-01T00:00:00Z")
_F2 = ("p.f2", "Nested", "2023-02-01T00:00:00Z")
_F3 = ("p.f3", "Empty", "2023-03-01T00:00:00Z")
_ROOT_REF = {
    "id": "p.playlistsroot",
    "type": "library-playlist-folders",
    "href": f"{_FOLDERS}/p.playlistsroot",
}


def _playlist(
    playlist_id: str,
    name: str,
    relationships: dict[str, object] | None = None,
    *,
    global_id: str | None = None,
) -> dict[str, object]:
    play_params: dict[str, object] = {
        "id": playlist_id,
        "kind": "playlist",
        "isLibrary": True,
    }
    if global_id is not None:
        play_params["globalId"] = global_id
    out: dict[str, object] = {
        "id": playlist_id,
        "type": "library-playlists",
        "href": f"/v1/me/library/playlists/{playlist_id}",
        "attributes": {
            "name": name,
            "canEdit": True,
            "isPublic": False,
            "dateAdded": "2024-01-01T00:00:00Z",
            "lastModifiedDate": "2024-01-02T00:00:00Z",
            "hasCatalog": False,
            "playParams": play_params,
        },
    }
    if relationships is not None:
        out["relationships"] = relationships
    return out


def _error(code: str, title: str, detail: str, status: str) -> dict[str, object]:
    return {
        "errors": [
            {
                "id": ANY,
                "title": title,
                "detail": detail,
                "status": status,
                "code": code,
            }
        ]
    }


def _param_error(parameter: str, detail: str) -> dict[str, object]:
    return {
        "errors": [
            {
                "id": ANY,
                "title": "Invalid Parameter Value",
                "detail": detail,
                "status": "400",
                "code": "40005",
                "source": {"parameter": parameter},
            }
        ]
    }


def _not_found() -> dict[str, object]:
    return _error(
        "40400", "Resource Not Found", "Resource with requested id was not found", "404"
    )


def _no_related(relationship: str) -> dict[str, object]:
    return _error(
        "40403",
        "No related resources",
        f"No related resources found for {relationship}",
        "404",
    )


def test_root_children(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}/p.playlistsroot/children")
    assert status == 200
    assert body == {
        "data": [_folder(*_F1), _playlist("p.pl1", "Top"), _folder(*_F3)],
        "meta": {"total": 3},
    }


def test_root_children_paginates(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}/p.playlistsroot/children?limit=2")
    assert status == 200
    assert body == {
        "data": [_folder(*_F1), _playlist("p.pl1", "Top")],
        "meta": {"total": 3},
        "next": f"{_FOLDERS}/p.playlistsroot/children?offset=2",
    }


def test_folder_children(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}/p.f1/children?offset=1")
    assert status == 200
    assert body == {"data": [_playlist("p.pl2", "Inner")], "meta": {"total": 2}}


@pytest.mark.parametrize(
    "path",
    [
        f"{_FOLDERS}/p.f3/children",
        f"{_FOLDERS}/p.missing/children",
        f"{_FOLDERS}/p.pl1/children",
        f"{_FOLDERS}/p.f1/children?offset=2",
        f"{_FOLDERS}/p.f1/children?offset=-1",
    ],
)
def test_children_without_results_404(mock: MusicKitApiMock, path: str) -> None:
    status, body = _get(mock, path)
    assert status == 404
    assert body == _no_related("children")


@pytest.mark.parametrize(
    ("query", "detail"),
    [
        (
            "limit=101",
            "Value must be an integer less than or equal to 100, but was: 101",
        ),
        ("limit=0", "Value must be an integer greater than or equal to 1"),
        ("limit=abc", "Value must be an integer"),
    ],
)
def test_children_invalid_limit_400(
    mock: MusicKitApiMock, query: str, detail: str
) -> None:
    status, body = _get(mock, f"{_FOLDERS}/p.f1/children?{query}")
    assert status == 400
    assert body == _param_error("limit", detail)


def test_children_include_tracks(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, f"{_FOLDERS}/p.playlistsroot/children?include=tracks&limit=2"
    )
    assert status == 200
    assert body == {
        "data": [
            _folder(*_F1),
            _playlist(
                "p.pl1",
                "Top",
                {
                    "tracks": {
                        "href": "/v1/me/library/playlists/p.pl1/tracks",
                        "next": "/v1/me/library/playlists/p.pl1/tracks?offset=0",
                        "data": [],
                        "meta": {"total": 2},
                    }
                },
            ),
        ],
        "meta": {"total": 3},
        "next": f"{_FOLDERS}/p.playlistsroot/children?offset=2",
    }


def test_children_include_parent_recurses_to_root(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}/p.f2/children?include=parent")
    root = {
        **_ROOT_REF,
        "relationships": {
            "parent": {
                "href": f"{_FOLDERS}/p.playlistsroot/parent",
                "data": [],
                "meta": {"total": 0},
            }
        },
    }
    outer = _folder(
        *_F1,
        {
            "parent": {
                "href": f"{_FOLDERS}/p.f1/parent",
                "data": [root],
                "meta": {"total": 1},
            }
        },
    )
    nested = _folder(
        *_F2,
        {
            "parent": {
                "href": f"{_FOLDERS}/p.f2/parent",
                "data": [outer],
                "meta": {"total": 1},
            }
        },
    )
    assert status == 200
    assert body == {
        "data": [
            _playlist(
                "p.pl3",
                "Deep",
                {
                    "parent": {
                        "href": "/v1/me/library/playlists/p.pl3/parent",
                        "data": [nested],
                        "meta": {"total": 1},
                    }
                },
            )
        ],
        "meta": {"total": 1},
    }


def test_folder(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}/p.f1")
    assert status == 200
    assert body == {"data": [_folder(*_F1)]}


def test_folder_for_playlist_id(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}/p.pl1")
    assert status == 200
    assert body == {"data": [_folder("p.pl1", "Top", "2024-01-01T00:00:00Z")]}


@pytest.mark.parametrize(
    "path",
    [
        f"{_FOLDERS}/p.missing",
        f"{_FOLDERS}/p.missing?include=children",
        f"{_FOLDERS}/p.playlistsroot",
    ],
)
def test_folder_not_found_404(mock: MusicKitApiMock, path: str) -> None:
    status, body = _get(mock, path)
    assert status == 404
    assert body == _not_found()


def test_folder_include_children_and_parent(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, f"{_FOLDERS}/p.f2?include=children,parent&limit[children]=1"
    )
    assert status == 200
    assert body == {
        "data": [
            _folder(
                *_F2,
                {
                    "children": {
                        "href": f"{_FOLDERS}/p.f2/children",
                        "data": [_playlist("p.pl3", "Deep")],
                        "meta": {"total": 1},
                    },
                    "parent": {
                        "href": f"{_FOLDERS}/p.f2/parent",
                        "data": [_folder(*_F1)],
                        "meta": {"total": 1},
                    },
                },
            )
        ]
    }


def test_empty_folder_include_children(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}/p.f3?include=children")
    assert status == 200
    assert body == {
        "data": [
            _folder(
                *_F3,
                {
                    "children": {
                        "href": f"{_FOLDERS}/p.f3/children",
                        "data": [],
                        "meta": {"total": 0},
                    }
                },
            )
        ]
    }


def test_root_include_children(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, f"{_FOLDERS}/p.playlistsroot?include=children&limit[children]=1"
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **_ROOT_REF,
                "relationships": {
                    "children": {
                        "href": f"{_FOLDERS}/p.playlistsroot/children",
                        "next": f"{_FOLDERS}/p.playlistsroot/children?offset=1",
                        "data": [_folder(*_F1)],
                        "meta": {"total": 3},
                    }
                },
            }
        ]
    }


def test_root_include_parent(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}/p.playlistsroot?include=parent")
    assert status == 200
    assert body == {
        "data": [
            {
                **_ROOT_REF,
                "relationships": {
                    "parent": {
                        "href": f"{_FOLDERS}/p.playlistsroot/parent",
                        "data": [],
                        "meta": {"total": 0},
                    }
                },
            }
        ]
    }


@pytest.mark.parametrize(
    ("query", "detail"),
    [
        ("limit[children]=0", "Value must be an integer greater than or equal to 1"),
        (
            "limit[children]=101",
            "Value must be an integer less than or equal to 100, but was: 101",
        ),
    ],
)
def test_folder_invalid_children_limit_400(
    mock: MusicKitApiMock, query: str, detail: str
) -> None:
    status, body = _get(mock, f"{_FOLDERS}/p.f1?include=children&{query}")
    parameter = "limit" if "101" in query else "limit[children]"
    assert status == 400
    assert body == _param_error(parameter, detail)


def test_folder_list(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, _FOLDERS)
    assert status == 200
    assert body == {
        "data": [_folder(*_F1), _folder(*_F2), _folder(*_F3)],
        "meta": {"total": 3},
    }


def test_folder_list_paginates(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}?limit=1&offset=1")
    assert status == 200
    assert body == {
        "data": [_folder(*_F2)],
        "meta": {"total": 3},
        "next": f"{_FOLDERS}?offset=2",
    }


def test_folder_list_offset_past_end(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}?offset=10")
    assert status == 200
    assert body == {"data": [], "meta": {"total": 3}}


def test_folder_list_limit_over_max_400(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}?limit=101")
    assert status == 400
    assert body == _param_error(
        "limit", "Value must be an integer less than or equal to 100, but was: 101"
    )


def test_folder_ids(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}?ids=p.f2,p.missing,p.pl1")
    assert status == 200
    assert body == {
        "data": [_folder(*_F2), _folder("p.pl1", "Top", "2024-01-01T00:00:00Z")]
    }


def test_folder_ids_empty_400(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}?ids=")
    assert status == 400
    assert body == _param_error("ids", "No id(s) supplied in the 'ids' query parameter")


def test_folder_parent_nested(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}/p.f2/parent")
    assert status == 200
    assert body == {"data": [_folder(*_F1)], "meta": {"total": 1}}


def test_folder_parent_top_level_is_root_ref(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}/p.f1/parent")
    assert status == 200
    assert body == {"data": [_ROOT_REF], "meta": {"total": 1}}


def test_folder_parent_for_playlist_id(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}/p.pl2/parent")
    assert status == 200
    assert body == {"data": [_folder(*_F1)], "meta": {"total": 1}}


@pytest.mark.parametrize(
    "path",
    [
        f"{_FOLDERS}/p.playlistsroot/parent",
        f"{_FOLDERS}/p.missing/parent",
        "/v1/me/library/playlists/p.missing/parent",
    ],
)
def test_parent_without_results_404(mock: MusicKitApiMock, path: str) -> None:
    status, body = _get(mock, path)
    assert status == 404
    assert body == _no_related("parent")


def test_folder_parent_limit_over_max_400(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}/p.f2/parent?limit=5")
    assert status == 400
    assert body == _param_error(
        "limit", "Value must be an integer less than or equal to 1, but was: 5"
    )


def test_playlist_parent(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "/v1/me/library/playlists/p.pl3/parent")
    assert status == 200
    assert body == {"data": [_folder(*_F2)], "meta": {"total": 1}}


def test_playlist_include_parent(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "/v1/me/library/playlists/p.pl2?include=parent")
    assert status == 200
    assert body == {
        "data": [
            _playlist(
                "p.pl2",
                "Inner",
                {
                    "parent": {
                        "href": "/v1/me/library/playlists/p.pl2/parent",
                        "data": [_folder(*_F1)],
                        "meta": {"total": 1},
                    }
                },
            )
        ]
    }


_PLAYLISTS = "/v1/me/library/playlists"


@pytest.mark.parametrize("path", [_PLAYLISTS, f"{_PLAYLISTS}/"])
def test_playlist_list(mock: MusicKitApiMock, path: str) -> None:
    status, body = _get(mock, path)
    assert status == 200
    assert body == {
        "data": [
            _playlist("p.pl1", "Top"),
            _playlist("p.pl2", "Inner"),
            _playlist("p.pl3", "Deep"),
        ],
        "meta": {"total": 3},
    }


def test_playlist_list_paginates(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_PLAYLISTS}?limit=1&offset=1")
    assert status == 200
    assert body == {
        "data": [_playlist("p.pl2", "Inner")],
        "meta": {"total": 3},
        "next": f"{_PLAYLISTS}?offset=2",
    }


def test_playlist_list_default_page_size(storefront: Storefront) -> None:
    m = MusicKitApiMock()
    m.endpoints.storefront = StorefrontResponseSuccess(storefront=storefront)
    m.data.library_playlists = {
        f"p.pl{i}": _library_playlist(f"Playlist {i}") for i in range(26)
    }
    status, body = _get(m, _PLAYLISTS)
    assert status == 200
    assert body == {
        "data": [_playlist(f"p.pl{i}", f"Playlist {i}") for i in range(25)],
        "meta": {"total": 26},
        "next": f"{_PLAYLISTS}?offset=25",
    }


def test_playlist_list_next_keeps_only_language_tag(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_PLAYLISTS}?l=en-US&include=parent&limit=1")
    assert status == 200
    assert body == {
        "data": [_playlist("p.pl1", "Top", _parent("p.pl1", _ROOT_REF))],
        "meta": {"total": 3},
        "next": f"{_PLAYLISTS}?l=en-US&offset=1",
    }


def test_playlist_list_offset_past_end(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_PLAYLISTS}?offset=3")
    assert status == 200
    assert body == {"data": [], "meta": {"total": 3}}


@pytest.mark.parametrize(
    ("query", "parameter", "detail"),
    [
        (
            "limit=101",
            "limit",
            "Value must be an integer less than or equal to 100, but was: 101",
        ),
        ("limit=0", "limit", "Value must be an integer greater than or equal to 1"),
        ("limit=abc", "limit", "Value must be an integer"),
        (
            "offset=-1",
            "offset",
            "Value must be an integer greater than or equal to 0",
        ),
        ("offset=abc", "offset", "Value must be an integer"),
    ],
)
def test_playlist_list_invalid_pagination_400(
    mock: MusicKitApiMock, query: str, parameter: str, detail: str
) -> None:
    status, body = _get(mock, f"{_PLAYLISTS}?{query}")
    assert status == 400
    assert body == _param_error(parameter, detail)


def _parent(playlist_id: str, parent: Mapping[str, object]) -> dict[str, object]:
    return {
        "parent": {
            "href": f"{_PLAYLISTS}/{playlist_id}/parent",
            "data": [parent],
            "meta": {"total": 1},
        }
    }


def test_playlist_list_include_parent(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_PLAYLISTS}?include=parent")
    assert status == 200
    assert body == {
        "data": [
            _playlist("p.pl1", "Top", _parent("p.pl1", _ROOT_REF)),
            _playlist("p.pl2", "Inner", _parent("p.pl2", _folder(*_F1))),
            _playlist("p.pl3", "Deep", _parent("p.pl3", _folder(*_F2))),
        ],
        "meta": {"total": 3},
    }


def test_playlist_list_include_parent_paginates(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_PLAYLISTS}?include=parent&limit=1&offset=1")
    assert status == 200
    assert body == {
        "data": [_playlist("p.pl2", "Inner", _parent("p.pl2", _folder(*_F1)))],
        "meta": {"total": 3},
        "next": f"{_PLAYLISTS}?offset=2",
    }


def test_playlist_list_include_catalog(
    mock: MusicKitApiMock, playlist: Playlist
) -> None:
    mock.data.library_playlists = {
        "p.pl1": replace(_library_playlist("Top"), catalog_id="pl.1"),
        "p.pl2": _library_playlist("Inner"),
    }
    mock.data.playlists = {"pl.1": playlist}
    _, single = _get(mock, f"{_PLAYLISTS}/p.pl1?include=catalog")
    assert isinstance(single, dict)
    catalog_resource = single["data"][0]["relationships"]["catalog"]["data"][0]
    status, body = _get(mock, f"{_PLAYLISTS}?include=catalog")
    assert status == 200
    assert body == {
        "data": [
            _playlist(
                "p.pl1",
                "Top",
                {
                    "catalog": {
                        "href": f"{_PLAYLISTS}/p.pl1/catalog",
                        "data": [catalog_resource],
                    }
                },
                global_id="pl.1",
            ),
            _playlist(
                "p.pl2",
                "Inner",
                {"catalog": {"href": f"{_PLAYLISTS}/p.pl2/catalog", "data": []}},
            ),
        ],
        "meta": {"total": 2},
    }


def _tracks_block(
    mock: MusicKitApiMock, playlist_id: str, next_offset: int | None = None
) -> dict[str, object]:
    songs = [_get(mock, f"/v1/me/library/songs/{sid}")[1] for sid in ("i.s1", "i.s2")]
    data = [song["data"][0] for song in songs if isinstance(song, dict)]
    out: dict[str, object] = {
        "href": f"{_PLAYLISTS}/{playlist_id}/tracks",
        "data": data if next_offset is None else data[:next_offset],
        "meta": {"total": 2},
    }
    if next_offset is not None:
        out["next"] = f"{_PLAYLISTS}/{playlist_id}/tracks?offset={next_offset}"
    return out


@pytest.fixture
def mock_with_tracks(
    mock: MusicKitApiMock, library_song: LibrarySong, song: CatalogSong
) -> MusicKitApiMock:
    mock.data.library_songs = {"i.s1": library_song, "i.s2": library_song}
    mock.data.songs = {"1": song}
    return mock


def test_playlist_list_include_tracks_single_resource(
    mock_with_tracks: MusicKitApiMock,
) -> None:
    status, body = _get(mock_with_tracks, f"{_PLAYLISTS}?include=tracks&limit=1")
    assert status == 200
    assert body == {
        "data": [
            _playlist(
                "p.pl1", "Top", {"tracks": _tracks_block(mock_with_tracks, "p.pl1")}
            )
        ],
        "meta": {"total": 3},
        "next": f"{_PLAYLISTS}?offset=1",
    }


def test_playlist_list_include_tracks_last_resource(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_PLAYLISTS}?include=tracks&offset=2&limit=2")
    assert status == 200
    assert body == {
        "data": [_playlist("p.pl3", "Deep", _empty_tracks("p.pl3"))],
        "meta": {"total": 3},
    }


def test_playlist_list_include_tracks_multiple_resources_400(
    mock: MusicKitApiMock,
) -> None:
    status, body = _get(mock, f"{_PLAYLISTS}?include=tracks&limit=2")
    assert status == 400
    assert body == _param_error(
        "include",
        "The 'tracks' relationship may only be activated with a single resource fetch",
    )


def test_playlist_list_ignores_unknown_include(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_PLAYLISTS}?include=foo&limit=1")
    assert status == 200
    assert body == {
        "data": [_playlist("p.pl1", "Top")],
        "meta": {"total": 3},
        "next": f"{_PLAYLISTS}?offset=1",
    }


def _empty_tracks(playlist_id: str) -> dict[str, object]:
    return {
        "tracks": {
            "href": f"{_PLAYLISTS}/{playlist_id}/tracks",
            "data": [],
            "meta": {"total": 0},
        }
    }


def _placeholder(
    playlist_id: str, relationships: dict[str, object] | None = None
) -> dict[str, object]:
    out: dict[str, object] = {
        "id": playlist_id,
        "type": "library-playlists",
        "href": f"{_PLAYLISTS}/{playlist_id}",
        "attributes": {
            "canEdit": False,
            "isPublic": False,
            "lastModifiedDate": "1970-01-01T00:00:00Z",
            "hasCatalog": False,
            "playParams": {"id": playlist_id, "kind": "playlist", "isLibrary": True},
        },
    }
    if relationships is not None:
        out["relationships"] = relationships
    return out


def _folder_as_playlist(
    folder_id: str,
    name: str,
    date_added: str,
    relationships: dict[str, object] | None = None,
) -> dict[str, object]:
    out: dict[str, object] = {
        "id": folder_id,
        "type": "library-playlists",
        "href": f"{_PLAYLISTS}/{folder_id}",
        "attributes": {
            "name": name,
            "canEdit": False,
            "isPublic": False,
            "dateAdded": date_added,
            "lastModifiedDate": "2023-04-01T00:00:00Z",
            "hasCatalog": False,
            "playParams": {"id": folder_id, "kind": "playlist", "isLibrary": True},
        },
    }
    if relationships is not None:
        out["relationships"] = relationships
    return out


@pytest.fixture
def mock_with_folder_dates(mock: MusicKitApiMock) -> MusicKitApiMock:
    folders = mock.data.library_playlist_folders
    assert isinstance(folders, dict)
    mock.data.library_playlist_folders = {
        folder_id: replace(folder, last_modified_date="2023-04-01T00:00:00Z")
        for folder_id, folder in folders.items()
    }
    return mock


@pytest.mark.parametrize("path", [_PLAYLISTS, f"{_PLAYLISTS}/"])
def test_playlist_ids(mock: MusicKitApiMock, path: str) -> None:
    status, body = _get(
        mock, f"{path}?ids=p.pl2,p.missing,i.missing,p.pl1,p.pl2&offset=1"
    )
    assert status == 200
    assert body == {
        "data": [
            _playlist("p.pl2", "Inner"),
            _placeholder("p.missing"),
            _playlist("p.pl1", "Top"),
        ]
    }


def test_playlist_ids_all_unknown(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_PLAYLISTS}?ids=p.missing1,p.missing2")
    assert status == 200
    assert body == {"data": []}


def test_playlist_ids_placeholder_relationships(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, f"{_PLAYLISTS}?ids=p.pl2,p.missing&include=parent,catalog"
    )
    catalog = {"href": f"{_PLAYLISTS}/p.missing/catalog", "data": []}
    assert status == 200
    assert body == {
        "data": [
            _playlist(
                "p.pl2",
                "Inner",
                {
                    **_parent("p.pl2", _folder(*_F1)),
                    "catalog": {"href": f"{_PLAYLISTS}/p.pl2/catalog", "data": []},
                },
            ),
            _placeholder(
                "p.missing",
                {**_parent("p.missing", _ROOT_REF), "catalog": catalog},
            ),
        ]
    }


def test_playlist_ids_folder(mock_with_folder_dates: MusicKitApiMock) -> None:
    status, body = _get(mock_with_folder_dates, f"{_PLAYLISTS}?ids=p.f2,p.missing")
    assert status == 200
    assert body == {
        "data": [
            _folder_as_playlist("p.f2", "Nested", "2023-02-01T00:00:00Z"),
            _placeholder("p.missing"),
        ]
    }


def test_single_playlist_for_folder_id(
    mock_with_folder_dates: MusicKitApiMock,
) -> None:
    status, body = _get(
        mock_with_folder_dates, f"{_PLAYLISTS}/p.f2?include=tracks,parent,catalog"
    )
    assert status == 200
    assert body == {
        "data": [
            _folder_as_playlist(
                "p.f2",
                "Nested",
                "2023-02-01T00:00:00Z",
                {
                    **_empty_tracks("p.f2"),
                    **_parent("p.f2", _folder(*_F1)),
                    "catalog": {"href": f"{_PLAYLISTS}/p.f2/catalog", "data": []},
                },
            )
        ]
    }


def test_single_playlist_default_has_no_relationships(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_PLAYLISTS}/p.pl1")
    assert status == 200
    assert body == {"data": [_playlist("p.pl1", "Top")]}


def test_single_playlist_include_catalog_without_match(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_PLAYLISTS}/p.pl2?include=catalog")
    assert status == 200
    assert body == {
        "data": [
            _playlist(
                "p.pl2",
                "Inner",
                {"catalog": {"href": f"{_PLAYLISTS}/p.pl2/catalog", "data": []}},
            )
        ]
    }


def test_single_playlist_not_found_404(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_PLAYLISTS}/p.missing")
    assert status == 404
    assert body == _not_found()


def test_playlist_description(mock: MusicKitApiMock) -> None:
    mock.data.library_playlists = {
        "p.pl1": replace(_library_playlist("Top"), description=Description(standard=""))
    }
    status, body = _get(mock, f"{_PLAYLISTS}/p.pl1")
    expected = _playlist("p.pl1", "Top")
    attributes = expected["attributes"]
    assert isinstance(attributes, dict)
    attributes["description"] = {"standard": ""}
    assert status == 200
    assert body == {"data": [expected]}


def test_playlist_ids_include_parent(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_PLAYLISTS}?ids=p.pl2&include=parent")
    assert status == 200
    assert body == {
        "data": [_playlist("p.pl2", "Inner", _parent("p.pl2", _folder(*_F1)))]
    }


def test_playlist_ids_include_tracks(mock_with_tracks: MusicKitApiMock) -> None:
    status, body = _get(
        mock_with_tracks,
        f"{_PLAYLISTS}?ids=p.pl1,p.pl1&include=tracks&limit[tracks]=1",
    )
    assert status == 200
    assert body == {
        "data": [
            _playlist(
                "p.pl1",
                "Top",
                {"tracks": _tracks_block(mock_with_tracks, "p.pl1", 1)},
            )
        ]
    }


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("ids=", _param_error("ids", "No id(s) supplied in the 'ids' query parameter")),
        (
            "ids=p.pl1,p.pl2&include=tracks",
            _param_error(
                "include",
                "The 'tracks' relationship may only be activated with a single"
                " resource fetch",
            ),
        ),
        (
            "ids=p.pl1&limit=1",
            {
                "errors": [
                    {
                        "id": ANY,
                        "title": "Invalid Parameter",
                        "detail": "Limit may not be supplied on this request",
                        "status": "400",
                        "code": "40004",
                        "source": {"parameter": "limit"},
                    }
                ]
            },
        ),
    ],
)
def test_playlist_ids_400(
    mock: MusicKitApiMock, query: str, expected: dict[str, object]
) -> None:
    status, body = _get(mock, f"{_PLAYLISTS}?{query}")
    assert status == 400
    assert body == expected


def test_root_children_unset_raises(storefront: Storefront) -> None:
    m = MusicKitApiMock()
    m.endpoints.storefront = StorefrontResponseSuccess(storefront=storefront)
    m.data.library_playlist_folders = {}
    with pytest.raises(ValueError, match="library_playlist_root_children is not set"):
        m.handle_request(
            Request(
                method="GET",
                url=f"{_API}{_FOLDERS}/p.playlistsroot/children",
                headers={},
                body=None,
            )
        )
