"""Description building block shared across resource types."""

from dataclasses import dataclass


@dataclass
class Description:
    """Free-form long/short description text."""

    standard: str
    short: str | None = None
