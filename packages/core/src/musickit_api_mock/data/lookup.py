"""Shared lookup helper for the per-resource resolvers in this package.

Each per-resource module owns a source type alias and a sub-resolver class.
They share the lookup helper here: it raises ``ValueError`` when the source
is ``None`` (design principle 1, "no implicit defaults"), reads from a dict
on key, or invokes a Callable with the lookup context for dynamic sources.

The lookup context carries the resource id plus the request-level locale
tag when one is present in the URL (``?l=`` value). It is ``None`` when
``?l=`` is absent — the mock does not fabricate a locale from the
storefront slug or any other source. Dict sources ignore the locale (an
id-only mapping is the simplest contract).
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar, cast

_T = TypeVar("_T")


@dataclass(frozen=True)
class LookupContext:
    """Per-request resource lookup input: id + optional request locale tag."""

    id: str
    locale: str | None


def _lookup_source(
    source: dict[str, _T] | Callable[[LookupContext], _T | None] | None,
    name: str,
    context: LookupContext,
) -> _T | None:
    if source is None:
        raise ValueError(f"{name} is not set")
    if isinstance(source, dict):
        d = cast("dict[str, _T]", source)
        return d.get(context.id)
    fn = cast("Callable[[LookupContext], _T | None]", source)
    return fn(context)


def _list_source_ids(
    source: dict[str, _T] | Callable[[LookupContext], _T | None] | None,
    name: str,
) -> list[str]:
    """Return all ids when the source is a dict.

    Callable sources cannot be enumerated by design — they're per-id lookup
    functions. Use a dict source when an endpoint needs the full id list
    (e.g. the genres or recommendations batch endpoint without ``?ids=``).
    """
    if source is None:
        raise ValueError(f"{name} is not set")
    if isinstance(source, dict):
        d = cast("dict[str, _T]", source)
        return list(d.keys())
    raise ValueError(
        f"{name} is a callable source; list-all batch endpoints require a dict source"
    )
