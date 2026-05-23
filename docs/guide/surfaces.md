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
- a **`Callable[[LookupContext], T]`** — for dynamic resolution (e.g. generate a `Song` for any id matching a pattern).

```python
# dict form
mock.data.songs = {
    "1000000001": Song(id="1000000001", name="Silence", ...),
}

# callable form
def resolve_song(ctx: LookupContext) -> Song:
    return Song(id=ctx.id, name=f"Track {ctx.id}", ...)

mock.data.songs = resolve_song
```

Endpoints that read the same resource compose their response from this shared source. Configure once, reach from multiple endpoints.

## `mock.endpoints.*` — per-endpoint HTTP responses

Each field accepts:

- a **response value** (e.g. `StorefrontResponseSuccess(...)` or `AccountResponseSessionExpired()`),
- a **`dict[str, Response]` keyed by id** — different responses for different ids, or
- a **`Callable[[Context], Response]`** — for dynamic shaping.

Use these to drive error scenarios (subscription expired, DRM failure, content unavailable, ...) or to override success-body details that aren't derivable from `mock.data`.

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

If a test fails with `ValueError: ... is not configured`, configure the field the error names.
