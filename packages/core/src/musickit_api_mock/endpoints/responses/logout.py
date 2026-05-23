"""Responses for the web-player logout endpoint."""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class LogoutResponseSuccess:
    """200 success for the logout endpoint.

    The caller swallows the body, so the response carries no fields.
    """


LogoutResponse = LogoutResponseSuccess


type LogoutSetter = LogoutResponseSuccess | Callable[[], LogoutResponseSuccess] | None
