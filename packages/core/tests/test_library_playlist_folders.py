from __future__ import annotations

import json
from dataclasses import replace
from typing import TYPE_CHECKING

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

from tests._expected import (
    ERROR_ID,
    LIBRARY_SONG,
    LIBRARY_SONG_ATTRIBUTES,
    PLAYLIST_ATTRIBUTES,
)

if TYPE_CHECKING:
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
    return (resp.status, json.loads(resp.body))


_F1 = {
    "id": "p.f1",
    "type": "library-playlist-folders",
    "href": "/v1/me/library/playlist-folders/p.f1",
    "attributes": {"name": "Outer", "dateAdded": "2023-01-01T00:00:00Z"},
}
_F2 = {
    "id": "p.f2",
    "type": "library-playlist-folders",
    "href": "/v1/me/library/playlist-folders/p.f2",
    "attributes": {"name": "Nested", "dateAdded": "2023-02-01T00:00:00Z"},
}
_F3 = {
    "id": "p.f3",
    "type": "library-playlist-folders",
    "href": "/v1/me/library/playlist-folders/p.f3",
    "attributes": {"name": "Empty", "dateAdded": "2023-03-01T00:00:00Z"},
}
_TOP_PLAYLIST_ATTRIBUTES = {
    "name": "Top",
    "canEdit": True,
    "isPublic": False,
    "dateAdded": "2024-01-01T00:00:00Z",
    "lastModifiedDate": "2024-01-02T00:00:00Z",
    "hasCatalog": False,
    "playParams": {"id": "p.pl1", "kind": "playlist", "isLibrary": True},
}
_TOP_PLAYLIST = {
    "id": "p.pl1",
    "type": "library-playlists",
    "href": "/v1/me/library/playlists/p.pl1",
    "attributes": _TOP_PLAYLIST_ATTRIBUTES,
}
_INNER_PLAYLIST_ATTRIBUTES = {
    "name": "Inner",
    "canEdit": True,
    "isPublic": False,
    "dateAdded": "2024-01-01T00:00:00Z",
    "lastModifiedDate": "2024-01-02T00:00:00Z",
    "hasCatalog": False,
    "playParams": {"id": "p.pl2", "kind": "playlist", "isLibrary": True},
}
_INNER_PLAYLIST = {
    "id": "p.pl2",
    "type": "library-playlists",
    "href": "/v1/me/library/playlists/p.pl2",
    "attributes": _INNER_PLAYLIST_ATTRIBUTES,
}
_DEEP_PLAYLIST_ATTRIBUTES = {
    "name": "Deep",
    "canEdit": True,
    "isPublic": False,
    "dateAdded": "2024-01-01T00:00:00Z",
    "lastModifiedDate": "2024-01-02T00:00:00Z",
    "hasCatalog": False,
    "playParams": {"id": "p.pl3", "kind": "playlist", "isLibrary": True},
}
_DEEP_PLAYLIST = {
    "id": "p.pl3",
    "type": "library-playlists",
    "href": "/v1/me/library/playlists/p.pl3",
    "attributes": _DEEP_PLAYLIST_ATTRIBUTES,
}
_ROOT_REF = {
    "id": "p.playlistsroot",
    "type": "library-playlist-folders",
    "href": f"{_FOLDERS}/p.playlistsroot",
}


def test_root_children(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}/p.playlistsroot/children")
    assert status == 200
    assert body == {"data": [_F1, _TOP_PLAYLIST, _F3], "meta": {"total": 3}}


def test_root_children_paginates(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}/p.playlistsroot/children?limit=2")
    assert status == 200
    assert body == {
        "data": [_F1, _TOP_PLAYLIST],
        "meta": {"total": 3},
        "next": f"{_FOLDERS}/p.playlistsroot/children?offset=2",
    }


def test_folder_children(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}/p.f1/children?offset=1")
    assert status == 200
    assert body == {"data": [_INNER_PLAYLIST], "meta": {"total": 2}}


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
    assert body == {
        "errors": [
            {
                "id": ERROR_ID,
                "title": "No related resources",
                "detail": "No related resources found for children",
                "status": "404",
                "code": "40403",
            }
        ]
    }


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
    assert body == {
        "errors": [
            {
                "id": ERROR_ID,
                "title": "Invalid Parameter Value",
                "detail": detail,
                "status": "400",
                "code": "40005",
                "source": {"parameter": "limit"},
            }
        ]
    }


def test_children_include_tracks(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, f"{_FOLDERS}/p.playlistsroot/children?include=tracks&limit=2"
    )
    assert status == 200
    assert body == {
        "data": [
            _F1,
            {
                **_TOP_PLAYLIST,
                "relationships": {
                    "tracks": {
                        "href": "/v1/me/library/playlists/p.pl1/tracks",
                        "next": "/v1/me/library/playlists/p.pl1/tracks?offset=0",
                        "data": [],
                        "meta": {"total": 2},
                    }
                },
            },
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
    outer = {
        **_F1,
        "relationships": {
            "parent": {
                "href": f"{_FOLDERS}/p.f1/parent",
                "data": [root],
                "meta": {"total": 1},
            }
        },
    }
    nested = {
        **_F2,
        "relationships": {
            "parent": {
                "href": f"{_FOLDERS}/p.f2/parent",
                "data": [outer],
                "meta": {"total": 1},
            }
        },
    }
    assert status == 200
    assert body == {
        "data": [
            {
                **_DEEP_PLAYLIST,
                "relationships": {
                    "parent": {
                        "href": "/v1/me/library/playlists/p.pl3/parent",
                        "data": [nested],
                        "meta": {"total": 1},
                    }
                },
            }
        ],
        "meta": {"total": 1},
    }


def test_folder(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}/p.f1")
    assert status == 200
    assert body == {"data": [_F1]}


def test_folder_for_playlist_id(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}/p.pl1")
    assert status == 200
    assert body == {
        "data": [
            {
                "id": "p.pl1",
                "type": "library-playlist-folders",
                "href": "/v1/me/library/playlist-folders/p.pl1",
                "attributes": {"name": "Top", "dateAdded": "2024-01-01T00:00:00Z"},
            }
        ]
    }


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
    assert body == {
        "errors": [
            {
                "id": ERROR_ID,
                "title": "Resource Not Found",
                "detail": "Resource with requested id was not found",
                "status": "404",
                "code": "40400",
            }
        ]
    }


def test_folder_include_children_and_parent(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, f"{_FOLDERS}/p.f2?include=children,parent&limit[children]=1"
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **_F2,
                "relationships": {
                    "children": {
                        "href": f"{_FOLDERS}/p.f2/children",
                        "data": [_DEEP_PLAYLIST],
                        "meta": {"total": 1},
                    },
                    "parent": {
                        "href": f"{_FOLDERS}/p.f2/parent",
                        "data": [_F1],
                        "meta": {"total": 1},
                    },
                },
            }
        ]
    }


def test_empty_folder_include_children(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}/p.f3?include=children")
    assert status == 200
    assert body == {
        "data": [
            {
                **_F3,
                "relationships": {
                    "children": {
                        "href": f"{_FOLDERS}/p.f3/children",
                        "data": [],
                        "meta": {"total": 0},
                    }
                },
            }
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
                        "data": [_F1],
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
    assert body == {
        "errors": [
            {
                "id": ERROR_ID,
                "title": "Invalid Parameter Value",
                "detail": detail,
                "status": "400",
                "code": "40005",
                "source": {"parameter": parameter},
            }
        ]
    }


def test_folder_list(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, _FOLDERS)
    assert status == 200
    assert body == {"data": [_F1, _F2, _F3], "meta": {"total": 3}}


def test_folder_list_paginates(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}?limit=1&offset=1")
    assert status == 200
    assert body == {"data": [_F2], "meta": {"total": 3}, "next": f"{_FOLDERS}?offset=2"}


def test_folder_list_offset_past_end(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}?offset=10")
    assert status == 200
    assert body == {"data": [], "meta": {"total": 3}}


def test_folder_list_limit_over_max_400(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}?limit=101")
    assert status == 400
    assert body == {
        "errors": [
            {
                "id": ERROR_ID,
                "title": "Invalid Parameter Value",
                "detail": "Value must be an integer less than or equal to 100, but was: 101",
                "status": "400",
                "code": "40005",
                "source": {"parameter": "limit"},
            }
        ]
    }


def test_folder_ids(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}?ids=p.f2,p.missing,p.pl1")
    assert status == 200
    assert body == {
        "data": [
            _F2,
            {
                "id": "p.pl1",
                "type": "library-playlist-folders",
                "href": "/v1/me/library/playlist-folders/p.pl1",
                "attributes": {"name": "Top", "dateAdded": "2024-01-01T00:00:00Z"},
            },
        ]
    }


def test_folder_ids_empty_400(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}?ids=")
    assert status == 400
    assert body == {
        "errors": [
            {
                "id": ERROR_ID,
                "title": "Invalid Parameter Value",
                "detail": "No id(s) supplied in the 'ids' query parameter",
                "status": "400",
                "code": "40005",
                "source": {"parameter": "ids"},
            }
        ]
    }


def test_folder_list_include_parent(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}?include=parent")
    assert status == 200
    assert body == {
        "data": [
            {
                **_F1,
                "relationships": {
                    "parent": {
                        "href": "/v1/me/library/playlist-folders/p.f1/parent",
                        "data": [_ROOT_REF],
                        "meta": {"total": 1},
                    }
                },
            },
            {
                **_F2,
                "relationships": {
                    "parent": {
                        "href": "/v1/me/library/playlist-folders/p.f2/parent",
                        "data": [_F1],
                        "meta": {"total": 1},
                    }
                },
            },
            {
                **_F3,
                "relationships": {
                    "parent": {
                        "href": "/v1/me/library/playlist-folders/p.f3/parent",
                        "data": [_ROOT_REF],
                        "meta": {"total": 1},
                    }
                },
            },
        ],
        "meta": {"total": 3},
    }


def test_folder_list_next_keeps_only_language_tag(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}?l=en-US&include=parent&limit=1")
    assert status == 200
    assert body == {
        "data": [
            {
                **_F1,
                "relationships": {
                    "parent": {
                        "href": "/v1/me/library/playlist-folders/p.f1/parent",
                        "data": [_ROOT_REF],
                        "meta": {"total": 1},
                    }
                },
            }
        ],
        "meta": {"total": 3},
        "next": f"{_FOLDERS}?l=en-US&offset=1",
    }


def test_folder_list_include_children_single_resource(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}?include=children&limit=1&offset=1")
    assert status == 200
    assert body == {
        "data": [
            {
                **_F2,
                "relationships": {
                    "children": {
                        "href": f"{_FOLDERS}/p.f2/children",
                        "data": [_DEEP_PLAYLIST],
                        "meta": {"total": 1},
                    }
                },
            }
        ],
        "meta": {"total": 3},
        "next": f"{_FOLDERS}?offset=2",
    }


@pytest.mark.parametrize(
    "query",
    [
        "include=children&limit=2",
        "include=parent,children",
        "ids=p.f1,p.f2&include=children",
    ],
)
def test_folder_list_include_children_multiple_resources_400(
    mock: MusicKitApiMock, query: str
) -> None:
    status, body = _get(mock, f"{_FOLDERS}?{query}")
    assert status == 400
    assert body == {
        "errors": [
            {
                "id": ERROR_ID,
                "title": "Invalid Parameter Value",
                "detail": "The 'children' relationship may only be activated with a single resource fetch",
                "status": "400",
                "code": "40005",
                "source": {"parameter": "include"},
            }
        ]
    }


def test_folder_ids_include_parent(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}?ids=p.f2,p.f1,p.pl2&include=parent")
    assert status == 200
    assert body == {
        "data": [
            {
                **_F2,
                "relationships": {
                    "parent": {
                        "href": "/v1/me/library/playlist-folders/p.f2/parent",
                        "data": [_F1],
                        "meta": {"total": 1},
                    }
                },
            },
            {
                **_F1,
                "relationships": {
                    "parent": {
                        "href": "/v1/me/library/playlist-folders/p.f1/parent",
                        "data": [_ROOT_REF],
                        "meta": {"total": 1},
                    }
                },
            },
            {
                "id": "p.pl2",
                "type": "library-playlist-folders",
                "href": "/v1/me/library/playlist-folders/p.pl2",
                "attributes": {"name": "Inner", "dateAdded": "2024-01-01T00:00:00Z"},
                "relationships": {
                    "parent": {
                        "href": "/v1/me/library/playlist-folders/p.pl2/parent",
                        "data": [_F1],
                        "meta": {"total": 1},
                    }
                },
            },
        ]
    }


def test_folder_ids_include_children(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}?ids=p.f2&include=children")
    assert status == 200
    assert body == {
        "data": [
            {
                **_F2,
                "relationships": {
                    "children": {
                        "href": f"{_FOLDERS}/p.f2/children",
                        "data": [_DEEP_PLAYLIST],
                        "meta": {"total": 1},
                    }
                },
            }
        ]
    }


def test_folder_ids_root_without_include(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}?ids=p.playlistsroot")
    assert status == 200
    assert body == {"data": []}


def test_folder_ids_root_include_parent(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}?ids=p.playlistsroot&include=parent")
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


def test_folder_ids_root_include_children(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, f"{_FOLDERS}?ids=p.playlistsroot&include=children&limit[children]=1"
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
                        "data": [_F1],
                        "meta": {"total": 3},
                    }
                },
            }
        ]
    }


def test_folder_parent_nested(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}/p.f2/parent")
    assert status == 200
    assert body == {"data": [_F1], "meta": {"total": 1}}


def test_folder_parent_top_level_is_root_ref(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}/p.f1/parent")
    assert status == 200
    assert body == {"data": [_ROOT_REF], "meta": {"total": 1}}


def test_folder_parent_for_playlist_id(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}/p.pl2/parent")
    assert status == 200
    assert body == {"data": [_F1], "meta": {"total": 1}}


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
    assert body == {
        "errors": [
            {
                "id": ERROR_ID,
                "title": "No related resources",
                "detail": "No related resources found for parent",
                "status": "404",
                "code": "40403",
            }
        ]
    }


def test_folder_parent_limit_over_max_400(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_FOLDERS}/p.f2/parent?limit=5")
    assert status == 400
    assert body == {
        "errors": [
            {
                "id": ERROR_ID,
                "title": "Invalid Parameter Value",
                "detail": "Value must be an integer less than or equal to 1, but was: 5",
                "status": "400",
                "code": "40005",
                "source": {"parameter": "limit"},
            }
        ]
    }


def test_playlist_parent(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "/v1/me/library/playlists/p.pl3/parent")
    assert status == 200
    assert body == {"data": [_F2], "meta": {"total": 1}}


def test_playlist_include_parent(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "/v1/me/library/playlists/p.pl2?include=parent")
    assert status == 200
    assert body == {
        "data": [
            {
                **_INNER_PLAYLIST,
                "relationships": {
                    "parent": {
                        "href": "/v1/me/library/playlists/p.pl2/parent",
                        "data": [_F1],
                        "meta": {"total": 1},
                    }
                },
            }
        ]
    }


_PLAYLISTS = "/v1/me/library/playlists"


@pytest.mark.parametrize("path", [_PLAYLISTS, f"{_PLAYLISTS}/"])
def test_playlist_list(mock: MusicKitApiMock, path: str) -> None:
    status, body = _get(mock, path)
    assert status == 200
    assert body == {
        "data": [_TOP_PLAYLIST, _INNER_PLAYLIST, _DEEP_PLAYLIST],
        "meta": {"total": 3},
    }


def test_playlist_list_paginates(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_PLAYLISTS}?limit=1&offset=1")
    assert status == 200
    assert body == {
        "data": [_INNER_PLAYLIST],
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
        "data": [
            {
                "id": f"p.pl{i}",
                "type": "library-playlists",
                "href": f"/v1/me/library/playlists/{f'p.pl{i}'}",
                "attributes": {
                    "name": f"Playlist {i}",
                    "canEdit": True,
                    "isPublic": False,
                    "dateAdded": "2024-01-01T00:00:00Z",
                    "lastModifiedDate": "2024-01-02T00:00:00Z",
                    "hasCatalog": False,
                    "playParams": {
                        "id": f"p.pl{i}",
                        "kind": "playlist",
                        "isLibrary": True,
                    },
                },
            }
            for i in range(25)
        ],
        "meta": {"total": 26},
        "next": f"{_PLAYLISTS}?offset=25",
    }


def test_playlist_list_next_keeps_only_language_tag(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_PLAYLISTS}?l=en-US&include=parent&limit=1")
    assert status == 200
    assert body == {
        "data": [
            {
                **_TOP_PLAYLIST,
                "relationships": {
                    "parent": {
                        "href": "/v1/me/library/playlists/p.pl1/parent",
                        "data": [_ROOT_REF],
                        "meta": {"total": 1},
                    }
                },
            }
        ],
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
        ("offset=-1", "offset", "Value must be an integer greater than or equal to 0"),
        ("offset=abc", "offset", "Value must be an integer"),
    ],
)
def test_playlist_list_invalid_pagination_400(
    mock: MusicKitApiMock, query: str, parameter: str, detail: str
) -> None:
    status, body = _get(mock, f"{_PLAYLISTS}?{query}")
    assert status == 400
    assert body == {
        "errors": [
            {
                "id": ERROR_ID,
                "title": "Invalid Parameter Value",
                "detail": detail,
                "status": "400",
                "code": "40005",
                "source": {"parameter": parameter},
            }
        ]
    }


def test_playlist_list_include_parent(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_PLAYLISTS}?include=parent")
    assert status == 200
    assert body == {
        "data": [
            {
                **_TOP_PLAYLIST,
                "relationships": {
                    "parent": {
                        "href": "/v1/me/library/playlists/p.pl1/parent",
                        "data": [_ROOT_REF],
                        "meta": {"total": 1},
                    }
                },
            },
            {
                **_INNER_PLAYLIST,
                "relationships": {
                    "parent": {
                        "href": "/v1/me/library/playlists/p.pl2/parent",
                        "data": [_F1],
                        "meta": {"total": 1},
                    }
                },
            },
            {
                **_DEEP_PLAYLIST,
                "relationships": {
                    "parent": {
                        "href": "/v1/me/library/playlists/p.pl3/parent",
                        "data": [_F2],
                        "meta": {"total": 1},
                    }
                },
            },
        ],
        "meta": {"total": 3},
    }


def test_playlist_list_include_parent_paginates(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_PLAYLISTS}?include=parent&limit=1&offset=1")
    assert status == 200
    assert body == {
        "data": [
            {
                **_INNER_PLAYLIST,
                "relationships": {
                    "parent": {
                        "href": "/v1/me/library/playlists/p.pl2/parent",
                        "data": [_F1],
                        "meta": {"total": 1},
                    }
                },
            }
        ],
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
    catalog_resource = {
        "id": "pl.1",
        "type": "playlists",
        "href": "/v1/catalog/us/playlists/pl.1",
        "attributes": {
            **PLAYLIST_ATTRIBUTES,
            "playParams": {"id": "pl.1", "kind": "playlist"},
        },
    }
    status, body = _get(mock, f"{_PLAYLISTS}?include=catalog")
    assert status == 200
    assert body == {
        "data": [
            {
                "id": "p.pl1",
                "type": "library-playlists",
                "href": "/v1/me/library/playlists/p.pl1",
                "attributes": {
                    **_TOP_PLAYLIST_ATTRIBUTES,
                    "playParams": {
                        "id": "p.pl1",
                        "kind": "playlist",
                        "isLibrary": True,
                        "globalId": "pl.1",
                    },
                },
                "relationships": {
                    "catalog": {
                        "href": f"{_PLAYLISTS}/p.pl1/catalog",
                        "data": [catalog_resource],
                    }
                },
            },
            {
                **_INNER_PLAYLIST,
                "relationships": {
                    "catalog": {"href": f"{_PLAYLISTS}/p.pl2/catalog", "data": []}
                },
            },
        ],
        "meta": {"total": 2},
    }


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
            {
                **_TOP_PLAYLIST,
                "relationships": {
                    "tracks": {
                        "href": "/v1/me/library/playlists/p.pl1/tracks",
                        "data": [
                            LIBRARY_SONG,
                            {
                                "id": "i.s2",
                                "type": "library-songs",
                                "href": "/v1/me/library/songs/i.s2",
                                "attributes": {
                                    **LIBRARY_SONG_ATTRIBUTES,
                                    "playParams": {
                                        "id": "i.s2",
                                        "kind": "song",
                                        "isLibrary": True,
                                        "reporting": True,
                                        "reportingId": "1",
                                        "catalogId": "1",
                                    },
                                },
                            },
                        ],
                        "meta": {"total": 2},
                    }
                },
            }
        ],
        "meta": {"total": 3},
        "next": f"{_PLAYLISTS}?offset=1",
    }


def test_playlist_list_include_tracks_last_resource(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_PLAYLISTS}?include=tracks&offset=2&limit=2")
    assert status == 200
    assert body == {
        "data": [
            {
                **_DEEP_PLAYLIST,
                "relationships": {
                    "tracks": {
                        "href": "/v1/me/library/playlists/p.pl3/tracks",
                        "data": [],
                        "meta": {"total": 0},
                    }
                },
            }
        ],
        "meta": {"total": 3},
    }


def test_playlist_list_include_tracks_multiple_resources_400(
    mock: MusicKitApiMock,
) -> None:
    status, body = _get(mock, f"{_PLAYLISTS}?include=tracks&limit=2")
    assert status == 400
    assert body == {
        "errors": [
            {
                "id": ERROR_ID,
                "title": "Invalid Parameter Value",
                "detail": "The 'tracks' relationship may only be activated with a single resource fetch",
                "status": "400",
                "code": "40005",
                "source": {"parameter": "include"},
            }
        ]
    }


def test_playlist_list_ignores_unknown_include(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_PLAYLISTS}?include=foo&limit=1")
    assert status == 200
    assert body == {
        "data": [_TOP_PLAYLIST],
        "meta": {"total": 3},
        "next": f"{_PLAYLISTS}?offset=1",
    }


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
            _INNER_PLAYLIST,
            {
                "id": "p.missing",
                "type": "library-playlists",
                "href": "/v1/me/library/playlists/p.missing",
                "attributes": {
                    "canEdit": False,
                    "isPublic": False,
                    "lastModifiedDate": "1970-01-01T00:00:00Z",
                    "hasCatalog": False,
                    "playParams": {
                        "id": "p.missing",
                        "kind": "playlist",
                        "isLibrary": True,
                    },
                },
            },
            _TOP_PLAYLIST,
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
            {
                **_INNER_PLAYLIST,
                "relationships": {
                    "parent": {
                        "href": "/v1/me/library/playlists/p.pl2/parent",
                        "data": [_F1],
                        "meta": {"total": 1},
                    },
                    "catalog": {"href": f"{_PLAYLISTS}/p.pl2/catalog", "data": []},
                },
            },
            {
                "id": "p.missing",
                "type": "library-playlists",
                "href": "/v1/me/library/playlists/p.missing",
                "attributes": {
                    "canEdit": False,
                    "isPublic": False,
                    "lastModifiedDate": "1970-01-01T00:00:00Z",
                    "hasCatalog": False,
                    "playParams": {
                        "id": "p.missing",
                        "kind": "playlist",
                        "isLibrary": True,
                    },
                },
                "relationships": {
                    "parent": {
                        "href": "/v1/me/library/playlists/p.missing/parent",
                        "data": [_ROOT_REF],
                        "meta": {"total": 1},
                    },
                    "catalog": catalog,
                },
            },
        ]
    }


def test_playlist_ids_folder(mock_with_folder_dates: MusicKitApiMock) -> None:
    status, body = _get(mock_with_folder_dates, f"{_PLAYLISTS}?ids=p.f2,p.missing")
    assert status == 200
    assert body == {
        "data": [
            {
                "id": "p.f2",
                "type": "library-playlists",
                "href": "/v1/me/library/playlists/p.f2",
                "attributes": {
                    "canEdit": False,
                    "isPublic": False,
                    "lastModifiedDate": "2023-04-01T00:00:00Z",
                    "hasCatalog": False,
                    "playParams": {"id": "p.f2", "kind": "playlist", "isLibrary": True},
                    "name": "Nested",
                    "dateAdded": "2023-02-01T00:00:00Z",
                },
            },
            {
                "id": "p.missing",
                "type": "library-playlists",
                "href": "/v1/me/library/playlists/p.missing",
                "attributes": {
                    "canEdit": False,
                    "isPublic": False,
                    "lastModifiedDate": "1970-01-01T00:00:00Z",
                    "hasCatalog": False,
                    "playParams": {
                        "id": "p.missing",
                        "kind": "playlist",
                        "isLibrary": True,
                    },
                },
            },
        ]
    }


def test_single_playlist_for_folder_id(mock_with_folder_dates: MusicKitApiMock) -> None:
    status, body = _get(
        mock_with_folder_dates, f"{_PLAYLISTS}/p.f2?include=tracks,parent,catalog"
    )
    assert status == 200
    assert body == {
        "data": [
            {
                "id": "p.f2",
                "type": "library-playlists",
                "href": "/v1/me/library/playlists/p.f2",
                "attributes": {
                    "canEdit": False,
                    "isPublic": False,
                    "lastModifiedDate": "2023-04-01T00:00:00Z",
                    "hasCatalog": False,
                    "playParams": {"id": "p.f2", "kind": "playlist", "isLibrary": True},
                    "name": "Nested",
                    "dateAdded": "2023-02-01T00:00:00Z",
                },
                "relationships": {
                    "tracks": {
                        "href": "/v1/me/library/playlists/p.f2/tracks",
                        "data": [],
                        "meta": {"total": 0},
                    },
                    "parent": {
                        "href": "/v1/me/library/playlists/p.f2/parent",
                        "data": [_F1],
                        "meta": {"total": 1},
                    },
                    "catalog": {"href": f"{_PLAYLISTS}/p.f2/catalog", "data": []},
                },
            }
        ]
    }


def test_single_playlist_default_has_no_relationships(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_PLAYLISTS}/p.pl1")
    assert status == 200
    assert body == {"data": [_TOP_PLAYLIST]}


def test_single_playlist_include_catalog_without_match(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_PLAYLISTS}/p.pl2?include=catalog")
    assert status == 200
    assert body == {
        "data": [
            {
                **_INNER_PLAYLIST,
                "relationships": {
                    "catalog": {"href": f"{_PLAYLISTS}/p.pl2/catalog", "data": []}
                },
            }
        ]
    }


def test_single_playlist_not_found_404(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_PLAYLISTS}/p.missing")
    assert status == 404
    assert body == {
        "errors": [
            {
                "id": ERROR_ID,
                "title": "Resource Not Found",
                "detail": "Resource with requested id was not found",
                "status": "404",
                "code": "40400",
            }
        ]
    }


@pytest.fixture
def mock_without_folders(storefront: Storefront) -> MusicKitApiMock:
    m = MusicKitApiMock()
    m.endpoints.storefront = StorefrontResponseSuccess(storefront=storefront)
    m.data.library_playlists = {"p.pl1": _library_playlist("Top")}
    return m


def test_single_playlist_not_found_without_folders_404(
    mock_without_folders: MusicKitApiMock,
) -> None:
    status, body = _get(mock_without_folders, f"{_PLAYLISTS}/p.missing")
    assert status == 404
    assert body == {
        "errors": [
            {
                "id": ERROR_ID,
                "title": "Resource Not Found",
                "detail": "Resource with requested id was not found",
                "status": "404",
                "code": "40400",
            }
        ]
    }


def test_playlist_ids_without_folders(mock_without_folders: MusicKitApiMock) -> None:
    status, body = _get(mock_without_folders, f"{_PLAYLISTS}?ids=p.pl1,p.missing")
    assert status == 200
    assert body == {
        "data": [
            _TOP_PLAYLIST,
            {
                "id": "p.missing",
                "type": "library-playlists",
                "href": "/v1/me/library/playlists/p.missing",
                "attributes": {
                    "canEdit": False,
                    "isPublic": False,
                    "lastModifiedDate": "1970-01-01T00:00:00Z",
                    "hasCatalog": False,
                    "playParams": {
                        "id": "p.missing",
                        "kind": "playlist",
                        "isLibrary": True,
                    },
                },
            },
        ]
    }


def test_playlist_description(mock: MusicKitApiMock) -> None:
    mock.data.library_playlists = {
        "p.pl1": replace(_library_playlist("Top"), description=Description(standard=""))
    }
    status, body = _get(mock, f"{_PLAYLISTS}/p.pl1")
    expected = {
        **_TOP_PLAYLIST,
        "attributes": {**_TOP_PLAYLIST_ATTRIBUTES, "description": {"standard": ""}},
    }
    assert status == 200
    assert body == {"data": [expected]}


def test_playlist_ids_include_parent(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, f"{_PLAYLISTS}?ids=p.pl2&include=parent")
    assert status == 200
    assert body == {
        "data": [
            {
                **_INNER_PLAYLIST,
                "relationships": {
                    "parent": {
                        "href": "/v1/me/library/playlists/p.pl2/parent",
                        "data": [_F1],
                        "meta": {"total": 1},
                    }
                },
            }
        ]
    }


def test_playlist_ids_include_tracks(mock_with_tracks: MusicKitApiMock) -> None:
    status, body = _get(
        mock_with_tracks, f"{_PLAYLISTS}?ids=p.pl1,p.pl1&include=tracks&limit[tracks]=1"
    )
    assert status == 200
    assert body == {
        "data": [
            {
                **_TOP_PLAYLIST,
                "relationships": {
                    "tracks": {
                        "href": "/v1/me/library/playlists/p.pl1/tracks",
                        "data": [LIBRARY_SONG],
                        "meta": {"total": 2},
                        "next": "/v1/me/library/playlists/p.pl1/tracks?offset=1",
                    }
                },
            }
        ]
    }


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        (
            "ids=",
            {
                "errors": [
                    {
                        "id": ERROR_ID,
                        "title": "Invalid Parameter Value",
                        "detail": "No id(s) supplied in the 'ids' query parameter",
                        "status": "400",
                        "code": "40005",
                        "source": {"parameter": "ids"},
                    }
                ]
            },
        ),
        (
            "ids=p.pl1,p.pl2&include=tracks",
            {
                "errors": [
                    {
                        "id": ERROR_ID,
                        "title": "Invalid Parameter Value",
                        "detail": "The 'tracks' relationship may only be activated with a single resource fetch",
                        "status": "400",
                        "code": "40005",
                        "source": {"parameter": "include"},
                    }
                ]
            },
        ),
        (
            "ids=p.pl1&limit=1",
            {
                "errors": [
                    {
                        "id": ERROR_ID,
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
