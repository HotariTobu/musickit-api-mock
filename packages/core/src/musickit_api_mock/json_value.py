"""Recursive JSON value type alias used across schema builders."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

type _JSONValue = (
    None
    | bool
    | int
    | float
    | str
    | Sequence["_JSONValue"]
    | Mapping[str, "_JSONValue"]
)
