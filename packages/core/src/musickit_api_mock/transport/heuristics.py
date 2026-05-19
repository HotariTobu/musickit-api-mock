"""Heuristic for classifying whether a request looks MusicKit-related."""

from urllib.parse import urlparse

from musickit_api_mock.transport.http import Request

# Apple-suffix hosts that never carry MusicKit API traffic. Tuned for low
# miss rate — extend only on confirmed misclassification, not preemptively.
_UNRELATED_HOSTS = frozenset(
    {
        "iforgot.apple.com",
        "appleid.apple.com",
        "idmsa.apple.com",
        "init.itunes.apple.com",
        "js-cdn.music.apple.com",
    }
)
_APPLE_SUFFIXES = (".music.apple.com", ".itunes.apple.com", ".mzstatic.com")


def _is_musickit_related(req: Request) -> bool:
    host = (urlparse(req.url).hostname or "").lower()
    if host in _UNRELATED_HOSTS:
        return False
    if "Music-User-Token" in req.headers or "X-Apple-Music-User-Token" in req.headers:
        return True
    return any(host.endswith(s) for s in _APPLE_SUFFIXES)
