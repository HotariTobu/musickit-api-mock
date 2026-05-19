"""Responses for the web-player logout endpoint."""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class LogoutResponseSuccess:
    """200 success for the logout endpoint (caller swallows the body)."""


LogoutResponse = LogoutResponseSuccess


type LogoutSetter = LogoutResponseSuccess | Callable[[], LogoutResponseSuccess] | None
