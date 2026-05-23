"""Editorial-notes building block shared across resource types."""

from dataclasses import dataclass


@dataclass
class EditorialNotes:
    """Editorial copy shown next to a resource.

    Attributes:
        name: Editorial display name override.
        short: Short-form editorial summary.
        standard: Long-form editorial copy.
        tagline: One-line editorial tagline.
    """

    name: str | None = None
    short: str | None = None
    standard: str | None = None
    tagline: str | None = None
