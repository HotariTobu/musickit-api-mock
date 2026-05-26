"""Description building block shared across resource types."""

from dataclasses import dataclass


@dataclass
class Description:
    """Free-form long and short description text.

    Attributes:
        standard: Long-form description.
        short: Short-form summary.
    """

    standard: str
    short: str | None = None
