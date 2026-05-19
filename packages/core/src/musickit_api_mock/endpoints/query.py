"""Query string parsing helpers: ``?ids``, ``?l``, bracketed and CSV params."""

import re
from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse

# Apple validates `?l=` against a curated whitelist of primary subtags
# (a strict ISO 639-1 subset; e.g. `yi`/`nn`/`ab` are valid ISO 639-1
# but Apple rejects them). Once the primary is whitelisted, additional
# subtags pass with very loose shape rules — script, region, length,
# and grammar variants all silent-accept. Inputs containing `_` or an
# empty value are silently treated as absent (Apple's parser bails on
# the non-BCP 47 character). Whitespace, leading hyphen, primary that
# isn't exactly 2 alphabetic characters, or primary not in the
# whitelist 400.
_LANGUAGE_TAG_PRIMARY_WHITELIST: frozenset[str] = frozenset(
    {
        "af",
        "ar",
        "bg",
        "bn",
        "ca",
        "cs",
        "da",
        "de",
        "el",
        "en",
        "es",
        "et",
        "fa",
        "fi",
        "fr",
        "ga",
        "gu",
        "he",
        "hi",
        "hr",
        "ht",
        "hu",
        "id",
        "is",
        "it",
        "ja",
        "kk",
        "kn",
        "ko",
        "la",
        "lo",
        "lt",
        "lv",
        "ml",
        "mr",
        "ms",
        "nb",
        "nl",
        "no",
        "or",
        "pa",
        "pl",
        "pt",
        "ro",
        "ru",
        "sa",
        "sk",
        "sl",
        "sv",
        "ta",
        "te",
        "th",
        "tl",
        "tr",
        "uk",
        "ur",
        "vi",
        "zh",
        "zu",
    }
)

_BRACKETED_RE = re.compile(r"^([a-zA-Z][a-zA-Z0-9_]*)\[([^\]]+)\]$")


def _parse_query(url: str) -> dict[str, list[str]]:
    return parse_qs(urlparse(url).query, keep_blank_values=True)


@dataclass(frozen=True)
class _LanguageTagAbsent:
    """``?l=`` is not present on the URL."""


@dataclass(frozen=True)
class _LanguageTagValid:
    """``?l=`` is well-formed; ``locale`` carries the validated tag."""

    locale: str


@dataclass(frozen=True)
class _LanguageTagInvalid:
    """``?l=`` is malformed; ``raw`` carries the bad input for the 400 envelope."""

    raw: str


type _LanguageTag = _LanguageTagAbsent | _LanguageTagValid | _LanguageTagInvalid


def _parse_language_tag(url: str) -> _LanguageTag:
    """Parse ``?l=`` into a tagged result so callers must branch on the kind.

    Three outcomes — absent, well-formed, malformed — are surfaced as distinct
    types so the caller cannot consume the locale without first rejecting the
    invalid case. Empty `?l=` value and inputs containing `_` are folded into
    Absent (matches Apple's silent-accept treatment).
    """
    raw = _parse_query(url).get("l", [None])[-1]
    if raw is None or raw == "" or "_" in raw:
        return _LanguageTagAbsent()
    if raw.startswith("-") or any(c.isspace() for c in raw):
        return _LanguageTagInvalid(raw)
    primary = raw.split("-", 1)[0]
    if len(primary) != 2 or not primary.isalpha():
        return _LanguageTagInvalid(raw)
    if primary.lower() not in _LANGUAGE_TAG_PRIMARY_WHITELIST:
        return _LanguageTagInvalid(raw)
    return _LanguageTagValid(raw)


def _parse_ids(url: str) -> tuple[bool, list[str]]:
    """Return (has_ids_param, parsed_ids).

    Accepts both ?ids=a&ids=b (repeat) and ?ids=a,b,c (comma).
    has_ids_param distinguishes "missing ids parameter" from "empty value".
    """
    q = _parse_query(url)
    if "ids" not in q:
        return False, []
    parts: list[str] = []
    for raw in q["ids"]:
        if raw == "":
            continue
        parts.extend(piece for piece in raw.split(",") if piece)
    return True, parts


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in items:
        if x in seen:
            continue
        seen.add(x)
        out.append(x)
    return out


def _parse_csv_param(url: str, name: str) -> set[str]:
    """Parse a comma-separated query param (e.g. ``?include=tracks,artists``)."""
    out: set[str] = set()
    for raw in _parse_query(url).get(name, []):
        for piece in raw.split(","):
            piece = piece.strip()
            if piece:
                out.add(piece)
    return out


def _parse_bracketed_param(url: str, name: str) -> dict[str, str]:
    """Parse ``?<name>[<key>]=<value>`` into ``{key: value}`` (last value wins).

    Used for inline pagination (``?limit[tracks]=2``) and similar bracketed
    relationship-keyed parameters.
    """
    out: dict[str, str] = {}
    for k, v in _parse_query(url).items():
        m = _BRACKETED_RE.match(k)
        if m is None or m.group(1) != name:
            continue
        rel = m.group(2)
        if v:
            out[rel] = v[-1]
    return out
