"""Expected JSON fragments for the resources built by the shared fixtures.

Response tests compare the whole decoded body against a literal
(``assert body == {...}``). The conftest fixtures show up in many of those
bodies, so each fixture resource's reference block (``id`` / ``type`` /
``href``) and attribute block live here once instead of being repeated in
every test. Envelopes, relationship blocks and pagination keys stay at the
assertion site: those are what an individual test is about.

Every value here is a literal transcription of what the mock emits for the
matching fixture — nothing is derived from the schema layer, so a change in
emitted output still has to be reflected here by hand.
"""

from __future__ import annotations


class _AnyErrorId:
    """Matches any error id: the mock emits a fresh random one per response."""

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, str)
            and len(other) == 32
            and all(c in "0123456789ABCDEF" for c in other)
        )

    def __repr__(self) -> str:
        return "<any error id>"


ERROR_ID = _AnyErrorId()

ARTWORK_CATALOG = {
    "url": "https://example.com/cover.jpg",
    "width": 640,
    "height": 640,
    "bgColor": "000000",
    "textColor1": "ffffff",
    "textColor2": "cccccc",
    "textColor3": "999999",
    "textColor4": "666666",
    "hasP3": False,
}

ARTWORK_LIBRARY = {
    "url": "https://example.com/lib.jpg",
    "width": 300,
    "height": 300,
}

SONG_REF = {"id": "1", "type": "songs", "href": "/v1/catalog/us/songs/1"}

SONG_ATTRIBUTES = {
    "name": "Test Song",
    "artistName": "Test Artist",
    "albumName": "Test Album",
    "artwork": ARTWORK_CATALOG,
    "durationInMillis": 180000,
    "genreNames": ["Pop"],
    "releaseDate": "2020-01-01",
    "trackNumber": 1,
    "discNumber": 1,
    "composerName": "Test Composer",
    "hasLyrics": False,
    "isAppleDigitalMaster": True,
    "isrc": "USABC1234567",
    "playParams": {"id": "1", "kind": "song"},
    "previews": [{"url": "https://audio-ssl.itunes.apple.com/preview/1.m4a"}],
    "url": "https://music.apple.com/us/song/1",
}

SONG = {**SONG_REF, "attributes": SONG_ATTRIBUTES}

ALBUM_REF = {"id": "a1", "type": "albums", "href": "/v1/catalog/us/albums/a1"}

ALBUM_ATTRIBUTES = {
    "name": "Test Album",
    "artistName": "Test Artist",
    "artwork": ARTWORK_CATALOG,
    "audioTraits": ["lossless"],
    "copyright": "(c) 2020",
    "genreNames": ["Pop"],
    "isCompilation": False,
    "isComplete": True,
    "isMasteredForItunes": True,
    "isPrerelease": False,
    "isSingle": False,
    "playParams": {"id": "a1", "kind": "album"},
    "recordLabel": "Indie",
    "releaseDate": "2020-01-01",
    "trackCount": 1,
    "upc": "000000000001",
    "url": "https://music.apple.com/us/album/a1",
}

ALBUM = {**ALBUM_REF, "attributes": ALBUM_ATTRIBUTES}

ALBUM_EDITORIAL_ARTWORK = {
    "superHeroTall": {
        "url": "https://example.com/edit-tall.jpg",
        "width": 1680,
        "height": 2240,
        "bgColor": "111111",
    }
}

ARTIST_REF = {"id": "ar1", "type": "artists", "href": "/v1/catalog/us/artists/ar1"}

ARTIST_ATTRIBUTES = {
    "name": "Test Artist",
    "artwork": ARTWORK_CATALOG,
    "genreNames": ["Pop"],
    "url": "https://music.apple.com/us/artist/ar1",
}

ARTIST = {**ARTIST_REF, "attributes": ARTIST_ATTRIBUTES}

MUSIC_VIDEO_REF = {
    "id": "mv1",
    "type": "music-videos",
    "href": "/v1/catalog/us/music-videos/mv1",
}

MUSIC_VIDEO_ATTRIBUTES = {
    "name": "Test MV",
    "artistName": "Test Artist",
    "artwork": ARTWORK_CATALOG,
    "durationInMillis": 210000,
    "genreNames": ["Pop"],
    "has4K": False,
    "hasHDR": False,
    "isrc": "USABC0000001",
    "playParams": {"id": "mv1", "kind": "musicVideo"},
    "previews": [{"url": "https://example.com/preview.mp4"}],
    "releaseDate": "2020-01-01",
    "url": "https://music.apple.com/us/music-video/mv1",
    "videoTraits": ["hdr"],
}

MUSIC_VIDEO = {**MUSIC_VIDEO_REF, "attributes": MUSIC_VIDEO_ATTRIBUTES}

PLAYLIST_REF = {
    "id": "pl1",
    "type": "playlists",
    "href": "/v1/catalog/us/playlists/pl1",
}

PLAYLIST_ATTRIBUTES = {
    "name": "Test Playlist",
    "artwork": ARTWORK_CATALOG,
    "audioTraits": [],
    "curatorName": "Test Curator",
    "hasCollaboration": False,
    "isChart": False,
    "lastModifiedDate": "2024-01-01",
    "playParams": {"id": "pl1", "kind": "playlist"},
    "playlistType": "user-shared",
    "supportsSing": False,
    "url": "https://music.apple.com/us/playlist/pl1",
}

PLAYLIST = {**PLAYLIST_REF, "attributes": PLAYLIST_ATTRIBUTES}

STATION_REF = {
    "id": "ra.978194965",
    "type": "stations",
    "href": "/v1/catalog/us/stations/ra.978194965",
}

STATION_ATTRIBUTES = {
    "name": "Apple Music 1",
    "artwork": ARTWORK_CATALOG,
    "isLive": True,
    "kind": "radio",
    "mediaKind": "audio",
    "playParams": {
        "id": "ra.978194965",
        "kind": "radioStation",
        "mediaType": "audio",
        "hasDrm": True,
        "stationHash": "39833ee1431faa2b",
    },
    "radioUrl": "https://itsliveradio.apple.com/gl/ra.978194965/index-cmaf.m3u8",
    "requiresSubscription": True,
    "supportedDrms": ["fairplay", "playready", "widevine"],
    "url": "https://music.apple.com/us/station/ra.978194965",
}

STATION = {**STATION_REF, "attributes": STATION_ATTRIBUTES}

CURATOR_REF = {
    "id": "cu1",
    "type": "apple-curators",
    "href": "/v1/catalog/us/apple-curators/cu1",
}

CURATOR_ATTRIBUTES = {
    "name": "Apple Music Pop",
    "artwork": ARTWORK_CATALOG,
    "kind": "Genre",
    "shortName": "Pop",
    "url": "https://music.apple.com/us/curator/apple-music-pop/cu1",
}

CURATOR = {**CURATOR_REF, "attributes": CURATOR_ATTRIBUTES}

NON_APPLE_CURATOR_REF = {
    "id": "cu2",
    "type": "curators",
    "href": "/v1/catalog/us/curators/cu2",
}

NON_APPLE_CURATOR_ATTRIBUTES = {
    "name": "Third Party Curator",
    "artwork": ARTWORK_CATALOG,
    "url": "https://music.apple.com/us/curator/third-party/cu2",
}

NON_APPLE_CURATOR = {
    **NON_APPLE_CURATOR_REF,
    "attributes": NON_APPLE_CURATOR_ATTRIBUTES,
}

GENRE_REF = {"id": "20", "type": "genres", "href": "/v1/catalog/us/genres/20"}

GENRE_ATTRIBUTES = {
    "name": "Pop",
    "parentId": "34",
    "parentName": "Music",
    "url": "https://music.apple.com/us/genre/20",
}

GENRE = {**GENRE_REF, "attributes": GENRE_ATTRIBUTES}

RECORD_LABEL_REF = {
    "id": "rl1",
    "type": "record-labels",
    "href": "/v1/catalog/us/record-labels/rl1",
}

RECORD_LABEL_ATTRIBUTES = {
    "name": "Indie",
    "url": "https://music.apple.com/us/record-label/rl1",
}

RECORD_LABEL = {**RECORD_LABEL_REF, "attributes": RECORD_LABEL_ATTRIBUTES}

GROUPING_REF = {
    "id": "gp1",
    "type": "groupings",
    "href": "/v1/catalog/us/groupings/gp1",
}

GROUPING_ATTRIBUTES = {
    "name": "Curators",
    "url": "https://music.apple.com/us/grouping/gp1",
}

GROUPING = {**GROUPING_REF, "attributes": GROUPING_ATTRIBUTES}

LIBRARY_SONG_REF = {
    "id": "i.s1",
    "type": "library-songs",
    "href": "/v1/me/library/songs/i.s1",
}

LIBRARY_SONG_ATTRIBUTES = {
    "name": "Lib Song",
    "artistName": "Lib Artist",
    "albumName": "Lib Album",
    "artwork": ARTWORK_LIBRARY,
    "discNumber": 1,
    "durationInMillis": 180000,
    "genreNames": ["Pop"],
    "hasLyrics": False,
    "playParams": {
        "id": "i.s1",
        "kind": "song",
        "isLibrary": True,
        "reporting": True,
        "reportingId": "1",
        "catalogId": "1",
    },
    "trackNumber": 1,
}

LIBRARY_SONG = {**LIBRARY_SONG_REF, "attributes": LIBRARY_SONG_ATTRIBUTES}

LIBRARY_ALBUM_REF = {
    "id": "l.a1",
    "type": "library-albums",
    "href": "/v1/me/library/albums/l.a1",
}

LIBRARY_ALBUM_ATTRIBUTES = {
    "name": "Lib Album",
    "artistName": "Lib Artist",
    "artwork": ARTWORK_LIBRARY,
    "dateAdded": "2024-01-01",
    "genreNames": ["Pop"],
    "playParams": {
        "id": "l.a1",
        "kind": "album",
        "isLibrary": True,
        "reporting": False,
        "reportingId": "587fae15d89d3ff1",
    },
    "trackCount": 1,
}

LIBRARY_ALBUM = {**LIBRARY_ALBUM_REF, "attributes": LIBRARY_ALBUM_ATTRIBUTES}

LIBRARY_ARTIST_REF = {
    "id": "r.ar1",
    "type": "library-artists",
    "href": "/v1/me/library/artists/r.ar1",
}

LIBRARY_ARTIST_ATTRIBUTES = {"name": "Lib Artist"}

LIBRARY_ARTIST = {**LIBRARY_ARTIST_REF, "attributes": LIBRARY_ARTIST_ATTRIBUTES}

LIBRARY_PLAYLIST_REF = {
    "id": "p.pl1",
    "type": "library-playlists",
    "href": "/v1/me/library/playlists/p.pl1",
}

LIBRARY_PLAYLIST_ATTRIBUTES = {
    "name": "Lib Playlist",
    "canDelete": True,
    "canEdit": True,
    "dateAdded": "2024-01-01",
    "hasCatalog": False,
    "hasCollaboration": False,
    "isPublic": False,
    "lastModifiedDate": "2024-01-02",
    "playParams": {
        "id": "p.pl1",
        "kind": "playlist",
        "isLibrary": True,
        "reporting": False,
        "reportingId": "9e55d62727073344",
    },
}

LIBRARY_PLAYLIST = {**LIBRARY_PLAYLIST_REF, "attributes": LIBRARY_PLAYLIST_ATTRIBUTES}

LIBRARY_MUSIC_VIDEO_REF = {
    "id": "i.mv1",
    "type": "library-music-videos",
    "href": "/v1/me/library/music-videos/i.mv1",
}

LIBRARY_MUSIC_VIDEO_ATTRIBUTES = {
    "name": "Lib MV",
    "artistName": "Lib Artist",
    "artwork": ARTWORK_LIBRARY,
    "durationInMillis": 200000,
    "genreNames": ["Pop"],
    "playParams": {
        "id": "i.mv1",
        "kind": "musicVideo",
        "isLibrary": True,
        "reporting": False,
        "reportingId": "7d2df265a3e56e30",
    },
    "releaseDate": "2020-01-01",
    "trackNumber": 1,
}

LIBRARY_MUSIC_VIDEO = {
    **LIBRARY_MUSIC_VIDEO_REF,
    "attributes": LIBRARY_MUSIC_VIDEO_ATTRIBUTES,
}

PERSONAL_RECOMMENDATION_REF = {
    "id": "rec1",
    "type": "personal-recommendation",
    "href": "/v1/me/recommendations/rec1",
}

PERSONAL_RECOMMENDATION_ATTRIBUTES = {
    "title": {"stringForDisplay": "Recommended Playlists"},
    "display": {"kind": "MusicCoverShelf", "decorations": []},
    "hasSeeAll": False,
    "isGroupRecommendation": False,
    "kind": "music-recommendations",
    "nextUpdateDate": "2026-05-25T00:00:00Z",
    "resourceTypes": ["playlists"],
    "version": 2,
}

PERSONAL_RECOMMENDATION = {
    **PERSONAL_RECOMMENDATION_REF,
    "attributes": PERSONAL_RECOMMENDATION_ATTRIBUTES,
}

STOREFRONT_REF = {"id": "us", "type": "storefronts", "href": "/v1/storefronts/us"}

STOREFRONT_ATTRIBUTES = {
    "name": "United States",
    "defaultLanguageTag": "en-US",
    "explicitContentPolicy": "allowed",
    "supportedLanguageTags": ["en-US"],
}

STOREFRONT = {**STOREFRONT_REF, "attributes": STOREFRONT_ATTRIBUTES}

ACCOUNT_REF = {"id": "me", "type": "accounts", "href": "/v1/me/account"}

ACCOUNT_ATTRIBUTES = {"restrictions": {}}

ACCOUNT = {**ACCOUNT_REF, "attributes": ACCOUNT_ATTRIBUTES}
