"""Responses for the Widevine certificate fetch endpoint."""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class WidevineCertResponseSuccess:
    """Success carrying the Widevine cert bytes."""

    cert: bytes


@dataclass
class WidevineCertResponseFailure:
    """Cert fetch failure (MusicKit reads body bytes only; status alone signals !ok)."""


WidevineCertResponse = WidevineCertResponseSuccess | WidevineCertResponseFailure


type WidevineCertSetter = (
    WidevineCertResponse | Callable[[], WidevineCertResponse] | None
)
