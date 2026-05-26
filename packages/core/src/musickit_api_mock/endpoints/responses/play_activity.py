"""Responses for the play-activity reporting endpoint."""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class PlayActivityResponseSuccess:
    """200 success for the fire-and-forget play-activity endpoint.

    The endpoint is fire-and-forget, so the response carries no fields.
    """


PlayActivityResponse = PlayActivityResponseSuccess


type PlayActivitySetter = (
    PlayActivityResponseSuccess | Callable[[], PlayActivityResponseSuccess] | None
)
