"""Responses for the FairPlay certificate fetch endpoint."""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class FairPlayCertResponseSuccess:
    """Success carrying the FairPlay certificate bytes.

    Attributes:
        cert: Raw FairPlay certificate bytes.
    """

    cert: bytes


@dataclass
class FairPlayCertResponseFailure:
    """Cert fetch failure.

    MusicKit reads the body bytes only; an HTTP non-OK status is enough to
    signal failure.
    """


FairPlayCertResponse = FairPlayCertResponseSuccess | FairPlayCertResponseFailure


type FairPlayCertSetter = (
    FairPlayCertResponse | Callable[[], FairPlayCertResponse] | None
)
