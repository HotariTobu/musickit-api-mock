from __future__ import annotations

import json
from typing import TYPE_CHECKING, cast

from musickit_api_mock import MusicKitApiMock, Request, Song

if TYPE_CHECKING:
    from tests._apple_response import _AppleArtwork, _AppleResponse


def _get(mock: MusicKitApiMock, url: str) -> tuple[int, _AppleResponse]:
    resp = mock.handle_request(Request(method="GET", url=url, headers={}, body=None))
    assert resp is not None
    return resp.status, json.loads(resp.body)


def test_q01_song_batch_valid(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/songs?ids=1")
    assert status == 200
    assert body["data"][0]["id"] == "1"
    assert body["data"][0]["type"] == "songs"
    assert body["data"][0]["attributes"]["name"] == "Test Song"


def test_q01_missing_id_resolves_to_empty(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/songs?ids=999")
    assert status == 200
    assert body == {"data": []}


def test_q01_mixed_valid_missing(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs?ids=1&ids=999"
    )
    assert status == 200
    assert [x["id"] for x in body["data"]] == ["1"]
    assert "errors" not in body


def test_q01_repeat_and_comma_ids_equivalent(mock: MusicKitApiMock) -> None:
    a_status, a_body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs?ids=1&ids=999"
    )
    b_status, b_body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs?ids=1,999"
    )
    assert a_status == b_status == 200
    assert [x["id"] for x in a_body["data"]] == [x["id"] for x in b_body["data"]]


def test_q01_dedupe(mock: MusicKitApiMock, song: Song) -> None:
    mock.data.songs = {"1": song, "2": song}
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs?ids=2,1,2"
    )
    assert status == 200
    assert [x["id"] for x in body["data"]] == ["2", "1"]


def test_q01_empty_ids_400(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/songs?ids=")
    assert status == 400
    err = body["errors"][0]
    assert err["code"] == "40005"
    assert err["title"] == "Invalid Parameter Value"
    assert err["detail"] == "No id(s) supplied in the 'ids' query parameter"


def test_q01_all_empty_ids_400(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/songs?ids=,,,")
    assert status == 400
    assert body["errors"][0]["code"] == "40005"


def test_q01_no_ids_param_400(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/songs")
    assert status == 400
    err = body["errors"][0]
    assert err["code"] == "40003"
    assert err["title"] == "Missing Parameter"
    assert err["detail"] == "No id(s) supplied on the request"


def test_q02_album_with_relationships(mock: MusicKitApiMock) -> None:
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/albums?ids=a1")
    assert status == 200
    rel = body["data"][0]["relationships"]
    assert len(rel["tracks"]["data"]) == 1
    assert rel["tracks"]["data"][0]["id"] == "1"
    assert len(rel["artists"]["data"]) == 1
    assert rel["artists"]["data"][0]["id"] == "ar1"


def test_q03_playlist_with_has_collaboration(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/playlists?ids=pl1"
    )
    assert status == 200
    attrs = body["data"][0]["attributes"]
    assert attrs["hasCollaboration"] is False
    rel = body["data"][0]["relationships"]
    assert rel["tracks"]["data"][0]["id"] == "1"


def test_q04_artist_with_albums(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/artists?ids=ar1"
    )
    assert status == 200
    rel = body["data"][0]["relationships"]
    assert rel["albums"]["data"][0]["id"] == "a1"


def test_q05_music_video_with_relationships(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/music-videos?ids=mv1"
    )
    assert status == 200
    rels = body["data"][0]["relationships"]
    assert [x["id"] for x in rels["albums"]["data"]] == ["a1"]
    assert [x["id"] for x in rels["artists"]["data"]] == ["ar1"]


def test_q06_station(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/stations?ids=ra.978194965"
    )
    assert status == 200
    attrs = body["data"][0]["attributes"]
    assert attrs["name"] == "Apple Music 1"
    assert attrs["mediaKind"] == "audio"


def test_unsupported_kind_404(mock: MusicKitApiMock) -> None:
    status, _body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/audio-books?ids=x"
    )
    assert status == 404


def test_album_tracks_standalone(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/albums/a1/tracks"
    )
    assert status == 200
    assert [x["id"] for x in body["data"]] == ["1"]
    assert "next" not in body


def test_invalid_language_tag_400(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/jp/albums?ids=a1&l=invalid-XX",
    )
    assert status == 400
    err = body["errors"][0]
    assert err["code"] == "40005"
    assert err["source"] == {"parameter": "l"}
    assert "invalid-XX" in err["detail"]


def test_valid_language_tag_passes(mock: MusicKitApiMock) -> None:
    status, _body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/jp/albums?ids=a1&l=ja-JP",
    )
    assert status == 200


def test_empty_language_tag_treated_as_absent(mock: MusicKitApiMock) -> None:
    """``?l=`` with empty value matches Apple's silent-absent treatment."""
    status, _body = _get(
        mock, "https://api.music.apple.com/v1/catalog/jp/albums?ids=a1&l="
    )
    assert status == 200


def test_trailing_hyphen_language_tag_passes(mock: MusicKitApiMock) -> None:
    """``?l=ja-`` (trailing hyphen, empty subtag) is silently accepted by Apple."""
    status, _body = _get(
        mock, "https://api.music.apple.com/v1/catalog/jp/albums?ids=a1&l=ja-"
    )
    assert status == 200


def test_three_letter_primary_language_tag_400(mock: MusicKitApiMock) -> None:
    """``?l=jpn`` (3-letter primary) is rejected — Apple whitelists 2-alpha only."""
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/jp/albums?ids=a1&l=jpn"
    )
    assert status == 400
    assert body["errors"][0]["code"] == "40005"


def test_non_whitelisted_two_alpha_primary_language_tag_400(
    mock: MusicKitApiMock,
) -> None:
    """``?l=ab`` (valid ISO 639-1 but outside Apple's whitelist) is rejected."""
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/jp/albums?ids=a1&l=ab"
    )
    assert status == 400
    assert body["errors"][0]["code"] == "40005"


def test_three_segment_non_whitelisted_primary_language_tag_400(
    mock: MusicKitApiMock,
) -> None:
    """``?l=ab-cd-ef`` is rejected because ``ab`` isn't whitelisted, not for grammar."""
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/jp/albums?ids=a1&l=ab-cd-ef"
    )
    assert status == 400
    assert body["errors"][0]["code"] == "40005"


def test_underscore_language_tag_treated_as_absent(mock: MusicKitApiMock) -> None:
    """``?l=ja_jp`` (underscore) is silently treated as absent by Apple."""
    status, _body = _get(
        mock, "https://api.music.apple.com/v1/catalog/jp/albums?ids=a1&l=ja_jp"
    )
    assert status == 200


def test_uppercase_primary_language_tag_passes(mock: MusicKitApiMock) -> None:
    """Primary subtag whitelist lookup is case-insensitive."""
    status, _body = _get(
        mock, "https://api.music.apple.com/v1/catalog/jp/albums?ids=a1&l=JA-JP"
    )
    assert status == 200


def test_script_subtag_language_tag_passes(mock: MusicKitApiMock) -> None:
    """Subtags after a whitelisted primary pass regardless of shape (script/region/length)."""
    status, _body = _get(
        mock, "https://api.music.apple.com/v1/catalog/jp/albums?ids=a1&l=zh-Hans-CN"
    )
    assert status == 200


def test_song_singular_default_relationships(mock: MusicKitApiMock) -> None:
    """Catalog song singular endpoint emits relationships.albums + .artists by default."""
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/songs/1")
    assert status == 200
    assert len(body["data"]) == 1
    assert body["data"][0]["id"] == "1"
    rels = body["data"][0]["relationships"]
    assert "albums" in rels
    assert "artists" in rels
    assert "composers" not in rels
    assert rels["albums"]["data"][0]["id"] == "a1"
    assert rels["artists"]["data"][0]["id"] == "ar1"


def test_song_singular_include_composers(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs/1?include=composers"
    )
    assert status == 200
    rels = body["data"][0]["relationships"]
    assert "composers" in rels
    assert rels["composers"]["data"][0]["id"] == "ar1"
    assert "attributes" in rels["composers"]["data"][0]


def test_song_batch_include_albums_deep_emit(mock: MusicKitApiMock) -> None:
    """``?include=albums`` on song output emits full Album attrs inline."""
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs?ids=1&include=albums"
    )
    assert status == 200
    rel_album = body["data"][0]["relationships"]["albums"]["data"][0]
    assert rel_album["id"] == "a1"
    assert "attributes" in rel_album
    assert rel_album["attributes"]["name"] == "Test Album"


def test_song_relationship_albums_endpoint(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs/1/albums"
    )
    assert status == 200
    assert body["data"][0]["id"] == "a1"


def test_song_relationship_artists_endpoint(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs/1/artists"
    )
    assert status == 200
    assert body["data"][0]["id"] == "ar1"


def test_song_relationship_composers_endpoint(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/songs/1/composers"
    )
    assert status == 200
    assert body["data"][0]["id"] == "ar1"


def test_song_relationship_overflow_400(mock: MusicKitApiMock) -> None:
    """``?limit=999`` on /songs/<id>/albums (cap=10) returns 400 envelope."""
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/songs/1/albums?limit=999",
    )
    assert status == 400
    err = body["errors"][0]
    assert err["code"] == "40005"
    assert err["source"] == {"parameter": "limit"}


def test_album_extend_editorial_artwork(mock: MusicKitApiMock) -> None:
    """``?extend=editorialArtwork`` adds Album.editorial_artwork dict to attrs."""
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/albums?ids=a1&extend=editorialArtwork",
    )
    assert status == 200
    attrs = body["data"][0]["attributes"]
    assert "editorialArtwork" in attrs
    editorial = cast("dict[str, _AppleArtwork]", attrs["editorialArtwork"])
    assert "superHeroTall" in editorial
    assert editorial["superHeroTall"]["width"] == 1680


def test_album_no_extend_no_editorial_artwork(mock: MusicKitApiMock) -> None:
    """Without ``?extend=``, ``editorialArtwork`` is not emitted."""
    status, body = _get(mock, "https://api.music.apple.com/v1/catalog/us/albums?ids=a1")
    assert status == 200
    assert "editorialArtwork" not in body["data"][0]["attributes"]


def test_playlist_curator_auto_emit_shallow(mock: MusicKitApiMock) -> None:
    """Default catalog playlist response auto-emits relationships.curator (shallow)."""
    status, body = _get(
        mock, "https://api.music.apple.com/v1/catalog/us/playlists?ids=pl1"
    )
    assert status == 200
    rels = body["data"][0]["relationships"]
    assert "curator" in rels
    curator_data = rels["curator"]["data"]
    assert len(curator_data) == 1
    assert curator_data[0]["id"] == "cu1"
    assert curator_data[0]["type"] == "apple-curators"
    assert "attributes" not in curator_data[0]


def test_playlist_include_curator_deep_emit(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/playlists?ids=pl1&include=curator",
    )
    assert status == 200
    rels = body["data"][0]["relationships"]
    curator_data = rels["curator"]["data"][0]
    assert curator_data["id"] == "cu1"
    assert "attributes" in curator_data
    assert curator_data["attributes"]["name"] == "Apple Music Pop"
    assert curator_data["attributes"]["kind"] == "Genre"


def test_inline_limit_tracks_slices_relationships(mock: MusicKitApiMock) -> None:
    """``?limit[tracks]=N`` controls inline relationship slice size."""
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/albums?ids=a1&limit[tracks]=1",
    )
    assert status == 200
    rel = body["data"][0]["relationships"]
    assert len(rel["tracks"]["data"]) == 1


def test_inline_limit_overflow_400(mock: MusicKitApiMock) -> None:
    """``?limit[tracks]=N`` past cap → 400 with source.parameter='limit'."""
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/albums?ids=a1&limit[tracks]=99999",
    )
    assert status == 400
    err = body["errors"][0]
    assert err["code"] == "40005"
    assert err["source"] == {"parameter": "limit"}
    assert "300" in err["detail"]


def test_inline_limit_zero_400(mock: MusicKitApiMock) -> None:
    """``?limit[tracks]=0`` → 400 with source.parameter='limit[tracks]'."""
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/albums?ids=a1&limit[tracks]=0",
    )
    assert status == 400
    err = body["errors"][0]
    assert err["source"] == {"parameter": "limit[tracks]"}
    assert "greater than or equal to 1" in err["detail"]


def test_inline_limit_non_integer_400(mock: MusicKitApiMock) -> None:
    status, body = _get(
        mock,
        "https://api.music.apple.com/v1/catalog/us/albums?ids=a1&limit[tracks]=abc",
    )
    assert status == 400
    err = body["errors"][0]
    assert err["source"] == {"parameter": "limit[tracks]"}
    assert err["detail"] == "Value must be an integer"


def _bare_mock_with_storefront() -> MusicKitApiMock:
    from musickit_api_mock import (
        Account,
        AccountResponseSuccess,
        MusicKitApiMock,
        Storefront,
        StorefrontResponseSuccess,
    )

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


def test_data_songs_callable_resolves_per_id() -> None:
    """``data.songs`` accepts ``Callable[[LookupContext], Song | None]``."""
    from musickit_api_mock import (
        Artwork,
        HlsChunk,
        HlsLayout,
        LookupContext,
        Song,
    )

    seen_ids: list[str] = []

    def song_resolver(ctx: LookupContext) -> Song | None:
        seen_ids.append(ctx.id)
        if ctx.id != "song-x":
            return None
        return Song(
            title=f"Title for {ctx.id}",
            artist="A",
            album="Al",
            duration_ms=1,
            artwork=Artwork(url="x", width=1, height=1),
            genres=[],
            release_date="2020-01-01",
            track_number=1,
            disc_number=1,
            composer="C",
            has_lyrics=False,
            audio_locale="en-US",
            audio_traits=[],
            has_time_synced_lyrics=False,
            is_apple_digital_master=False,
            is_mastered_for_itunes=False,
            is_vocal_attenuation_allowed=False,
            url="x",
            hls_layout=HlsLayout(
                target_duration_sec=1,
                init_byte_offset=0,
                init_byte_length=0,
                chunks=(HlsChunk(duration_sec=1.0, byte_offset=0, byte_length=0),),
            ),
            hls_segment=b"",
            preview_audio=b"",
            bitrate=1,
            sample_rate=1,
            file_size=1,
            album_ids=None,
            artist_ids=None,
            composer_ids=None,
        )

    m = _bare_mock_with_storefront()
    m.data.songs = song_resolver

    status, body = _get(m, "https://api.music.apple.com/v1/catalog/us/songs?ids=song-x")
    assert status == 200
    assert body["data"][0]["id"] == "song-x"
    assert body["data"][0]["attributes"]["name"] == "Title for song-x"
    assert "song-x" in seen_ids


def test_data_artists_callable_resolves_per_id() -> None:
    """``data.artists`` accepts ``Callable[[LookupContext], Artist | None]``."""
    from musickit_api_mock import Artist, Artwork, LookupContext

    def artist_resolver(ctx: LookupContext) -> Artist | None:
        if ctx.id != "ar-x":
            return None
        return Artist(
            name=f"Artist {ctx.id}",
            artwork=Artwork(url="x", width=1, height=1),
            genre_names=[],
            url="x",
        )

    m = _bare_mock_with_storefront()
    m.data.artists = artist_resolver

    status, body = _get(m, "https://api.music.apple.com/v1/catalog/us/artists?ids=ar-x")
    assert status == 200
    assert body["data"][0]["id"] == "ar-x"
    assert body["data"][0]["attributes"]["name"] == "Artist ar-x"


def test_locale_callable_resolver_receives_request_locale() -> None:
    """``?l=`` is threaded into ``Callable[[LookupContext], T | None]`` data sources; absent ``?l=`` becomes ``None``."""
    from musickit_api_mock import (
        AccountResponseSuccess,
        Album,
        Artwork,
        LookupContext,
        MusicKitApiMock,
        StorefrontResponseSuccess,
    )

    seen_locales: list[str | None] = []

    def album_resolver(ctx: LookupContext) -> Album | None:
        seen_locales.append(ctx.locale)
        if ctx.id != "a1":
            return None
        name = (
            "Test (en)"
            if ctx.locale is not None and ctx.locale.startswith("en")
            else "Test (default)"
        )
        return Album(
            name=name,
            artist_name="Artist",
            artwork=Artwork(url="x", width=1, height=1),
            genre_names=[],
            track_count=0,
            is_compilation=False,
            is_complete=True,
            is_mastered_for_itunes=False,
            is_single=True,
            is_prerelease=False,
            audio_traits=[],
            url="x",
        )

    m = MusicKitApiMock()
    m.data.albums = album_resolver
    m.endpoints.storefront = StorefrontResponseSuccess(
        storefront=__import__("musickit_api_mock").Storefront(
            id="us",
            name="US",
            default_language_tag="en-US",
            supported_language_tags=["en-US"],
            explicit_content_policy="allowed",
        )
    )
    m.endpoints.account = AccountResponseSuccess(
        account=__import__("musickit_api_mock").Account(
            subscription_active=True, subscription_storefront="us"
        )
    )
    status_default, body_default = _get(
        m, "https://api.music.apple.com/v1/catalog/jp/albums?ids=a1"
    )
    status_en, body_en = _get(
        m, "https://api.music.apple.com/v1/catalog/jp/albums?ids=a1&l=en-US"
    )
    assert status_default == 200
    assert status_en == 200
    assert body_default["data"][0]["attributes"]["name"] == "Test (default)"
    assert body_en["data"][0]["attributes"]["name"] == "Test (en)"
    assert seen_locales[0] is None
    assert seen_locales[1] == "en-US"
