"""Responses for the FairPlay certificate fetch endpoint."""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class FairPlayCertResponseSuccess:
    """Success carrying the FairPlay cert bytes."""

    cert: bytes


@dataclass
class FairPlayCertResponseFailure:
    """Cert fetch failure (MusicKit reads body bytes only; status alone signals !ok)."""


FairPlayCertResponse = FairPlayCertResponseSuccess | FairPlayCertResponseFailure


type FairPlayCertSetter = (
    FairPlayCertResponse | Callable[[], FairPlayCertResponse] | None
)
