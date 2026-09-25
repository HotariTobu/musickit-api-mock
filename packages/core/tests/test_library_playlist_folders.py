from __future__ import annotations

import json
from unittest.mock import ANY

import pytest
from musickit_api_mock import (
    LibraryPlaylist,
    LibraryPlaylistFolder,
    LibraryPlaylistFolderChild,
    MusicKitApiMock,
    Request,
    Storefront,
    StorefrontResponseSuccess,
)

_API = "https://api.music.apple.com"
_FOLDERS = "/v1/me/library/playlist-folders"


def _folder_child(item_id: str) -> LibraryPlaylistFolderChild:
    return LibraryPlaylistFolderChild(type="library-playlist-folders", id=item_id)


def _playlist_child(item_id: str) -> LibraryPlaylistFolderChild:
    return LibraryPlaylistFolderChild(type="library-playlists", id=item_id)


def _library_playlist(name: str, track_ids: list[str] | None = None) -> LibraryPlaylist:
    return LibraryPlaylist(
        name=name,
        can_delete=True,
        can_edit=True,
        is_public=False,
        has_catalog=False,
        has_collaboration=False,
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
    playlist_id: str, name: str, relationships: dict[str, object] | None = None
) -> dict[str, object]:
    out: dict[str, object] = {
        "id": playlist_id,
        "type": "library-playlists",
        "href": f"/v1/me/library/playlists/{playlist_id}",
        "attributes": {
            "name": name,
            "canDelete": True,
            "canEdit": True,
            "isPublic": False,
            "dateAdded": "2024-01-01T00:00:00Z",
            "lastModifiedDate": "2024-01-02T00:00:00Z",
            "hasCatalog": False,
            "hasCollaboration": False,
            "playParams": {
                "id": playlist_id,
                "kind": "playlist",
                "isLibrary": True,
                "reporting": False,
                "reportingId": ANY,
            },
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
