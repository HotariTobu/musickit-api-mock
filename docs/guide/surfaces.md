# Surfaces overview

A `MusicKitApiMock` instance exposes three configuration surfaces. The split is load-bearing — each surface has a distinct semantic role, and mixing them defeats the purpose.

| Surface | Holds | When to use |
|---|---|---|
| `mock.data.*` | Shared resource sources (songs, albums, playlists, artists, library items, ...) | When multiple endpoints should read the same resource (e.g. `/songs/<id>` and `/me/library/songs` both serve the same `Song`). |
| `mock.endpoints.*` | Per-endpoint HTTP response overrides (storefront, account, license, web playback, ...) | When you need to shape the HTTP response itself — status, error variants, success body. |
| `mock.browser.*` | State consumed by the in-page JS shim (authorize response, EME key-system flavor) | When you need to control what the page sees from MusicKit JS's browser integrations — not the network. |

## `mock.data.*` — shared resource data

Each field accepts:

- a **`dict[str, T]` keyed by id** — looked up on demand, or
- a **`Callable[[LookupContext], T | None]`** — for dynamic resolution (e.g. load a `Song` for any id matching a pattern, or return `None` for not found).

```python
# dict form
mock.data.songs = {
    "1000000001": Song.from_file("path/to/song.m4a"),
}

# callable form
def resolve_song(ctx: LookupContext) -> Song | None:
    if not ctx.id.startswith("test-"):
        return None
    return Song.from_file(f"path/to/songs/{ctx.id}.m4a")

mock.data.songs = resolve_song
```

Endpoints that read the same resource compose their response from this shared source. Configure once, reach from multiple endpoints.

## `mock.endpoints.*` — per-endpoint HTTP responses

Accepted shapes vary by field — some accept only a response value or callable; others also accept a `dict` keyed by id. See each field's type in the [reference](../reference/endpoints.md) for the exact union.

Use these to drive error scenarios (subscription expired, DRM failure, content unavailable, ...) or to override success-body details that aren't derivable from `mock.data`. Common forms:

```python
# success
mock.endpoints.account = AccountResponseSuccess(account=Account(...))

# error variant
mock.endpoints.account = AccountResponseSessionExpired()

# per-id variation
mock.endpoints.web_playback = {
    "1000000001": WebPlaybackResponseSuccess(...),
    "1000000002": WebPlaybackResponseGeoBlock(),
}
```

## `mock.browser.*` — in-page shim state

The page-side shim replaces MusicKit JS's browser integrations:

- `mock.browser.authorize_response` — what gets delivered when the page calls `music.authorize()` (success / decline / close / switch-user / unavailable variants).
- `mock.browser.eme_flavor` — the EME key system flavor the shim exposes (FairPlay / Widevine / PlayReady).

These are **not HTTP responses**. They configure how the shim behaves inside the page's JavaScript runtime.

## Unset is not "default"

All fields default to `None`. **Reading an unset field at request time raises `ValueError`** — the mock does not invent fallback values for fields you didn't configure. This is intentional: silent fallbacks make broken tests look healthy.
