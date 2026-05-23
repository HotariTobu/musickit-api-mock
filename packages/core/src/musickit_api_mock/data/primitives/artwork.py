"""Artwork building block shared across resource types."""

from dataclasses import dataclass


@dataclass
class Artwork:
    """Image asset metadata attached to most catalog and library resources.

    Attributes:
        url: Image asset URL; the mock serves it verbatim. Apple's catalog
            format uses URL templates with ``{w}``, ``{h}``, ``{f}``
            placeholders the consumer substitutes.
        width: Image width in pixels at the template's max size.
        height: Image height in pixels at the template's max size.
        bg_color: Dominant background color as a hex string (without the
            leading ``#``).
        text_color_1: Foreground-text color hint (primary).
        text_color_2: Foreground-text color hint (secondary).
        text_color_3: Foreground-text color hint (tertiary).
        text_color_4: Foreground-text color hint (quaternary).
        has_p3: Whether a Display-P3 wide-gamut variant is available.
    """

    url: str
    width: int
    height: int
    bg_color: str | None = None
    text_color_1: str | None = None
    text_color_2: str | None = None
    text_color_3: str | None = None
    text_color_4: str | None = None
    has_p3: bool | None = None
