"""Editorial-notes building block shared across resource types."""

from dataclasses import dataclass


@dataclass
class EditorialNotes:
    """Editorial copy shown next to a resource."""

    name: str | None = None
    short: str | None = None
    standard: str | None = None
    tagline: str | None = None
