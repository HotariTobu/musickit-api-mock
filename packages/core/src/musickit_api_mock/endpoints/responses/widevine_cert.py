"""Responses for the Widevine certificate fetch endpoint."""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class WidevineCertResponseSuccess:
    """Success carrying the Widevine certificate bytes.

    Attributes:
        cert: Raw Widevine certificate bytes.
    """

    cert: bytes


@dataclass
class WidevineCertResponseFailure:
    """Cert fetch failure.

    MusicKit reads the body bytes only; an HTTP non-OK status is enough to
    signal failure.
    """


WidevineCertResponse = WidevineCertResponseSuccess | WidevineCertResponseFailure


type WidevineCertSetter = (
    WidevineCertResponse | Callable[[], WidevineCertResponse] | None
)
