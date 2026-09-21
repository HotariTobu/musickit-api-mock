"""Recursive JSON value type alias used across schema builders."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

type _JSONValue = (
    bool
    | int
    | float
    | str
    | Sequence["_JSONValue"]
    | Mapping[str, "_JSONValue"]
    | None
)
