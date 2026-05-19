from musickit_api_mock import MusicKitApiMock, Request


def _req(url: str, headers: dict[str, str] | None = None) -> Request:
    return Request(method="GET", url=url, headers=headers or {}, body=None)


def test_apple_music_host_is_related() -> None:
    m = MusicKitApiMock()
    assert (
        m.is_musickit_related(_req("https://api.music.apple.com/v1/me/storefront"))
        is True
    )


def test_itunes_host_is_related() -> None:
    m = MusicKitApiMock()
    assert m.is_musickit_related(_req("https://play.itunes.apple.com/x")) is True


def test_mzstatic_host_is_related() -> None:
    m = MusicKitApiMock()
    assert (
        m.is_musickit_related(_req("https://is1-ssl.mzstatic.com/image/thumb/abc.jpg"))
        is True
    )


def test_unrelated_auth_hosts_excluded() -> None:
    m = MusicKitApiMock()
    assert m.is_musickit_related(_req("https://idmsa.apple.com/auth")) is False
    assert m.is_musickit_related(_req("https://appleid.apple.com/login")) is False
    assert m.is_musickit_related(_req("https://iforgot.apple.com/password")) is False


def test_init_itunes_excluded_despite_itunes_suffix() -> None:
    """Suffix collision: the unrelated-set check must short-circuit before the suffix match."""
    m = MusicKitApiMock()
    assert (
        m.is_musickit_related(_req("https://init.itunes.apple.com/jingleConfig"))
        is False
    )


def test_js_cdn_excluded_despite_music_suffix() -> None:
    """Suffix collision: the unrelated-set check must short-circuit before the suffix match."""
    m = MusicKitApiMock()
    assert (
        m.is_musickit_related(_req("https://js-cdn.music.apple.com/musickit.js"))
        is False
    )


def test_unrelated_host_overrides_music_token_header() -> None:
    """Unrelated-set check runs before the token-header check; the host wins."""
    m = MusicKitApiMock()
    assert (
        m.is_musickit_related(
            _req("https://idmsa.apple.com/auth", {"Music-User-Token": "abc"})
        )
        is False
    )


def test_host_match_is_case_insensitive() -> None:
    m = MusicKitApiMock()
    assert (
        m.is_musickit_related(_req("https://API.MUSIC.APPLE.COM/v1/me/storefront"))
        is True
    )


def test_suffix_requires_label_boundary() -> None:
    """``xmusic.apple.com`` must not match the ``.music.apple.com`` suffix."""
    m = MusicKitApiMock()
    assert m.is_musickit_related(_req("https://xmusic.apple.com/foo")) is False


def test_bare_music_apple_com_excluded() -> None:
    """``music.apple.com`` is the web player HTML host; MusicKit JS does not emit API requests to it."""
    m = MusicKitApiMock()
    assert (
        m.is_musickit_related(_req("https://music.apple.com/us/album/foo/1")) is False
    )


def test_music_user_token_header_marks_related() -> None:
    m = MusicKitApiMock()
    assert (
        m.is_musickit_related(
            _req("https://example.com/x", {"Music-User-Token": "abc"})
        )
        is True
    )


def test_x_apple_music_user_token_header_marks_related() -> None:
    """``X-Apple-Music-User-Token`` is the alternate header MusicKit emits."""
    m = MusicKitApiMock()
    assert (
        m.is_musickit_related(
            _req("https://example.com/x", {"X-Apple-Music-User-Token": "abc"})
        )
        is True
    )


def test_unrelated_third_party_host() -> None:
    m = MusicKitApiMock()
    assert m.is_musickit_related(_req("https://example.com/")) is False
