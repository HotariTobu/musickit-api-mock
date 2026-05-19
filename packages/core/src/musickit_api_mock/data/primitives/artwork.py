"""Artwork building block shared across resource types."""

from dataclasses import dataclass


@dataclass
class Artwork:
    """Image asset metadata attached to most catalog/library resources."""

    url: str
    width: int
    height: int
    bg_color: str | None = None
    text_color_1: str | None = None
    text_color_2: str | None = None
    text_color_3: str | None = None
    text_color_4: str | None = None
    has_p3: bool | None = None
