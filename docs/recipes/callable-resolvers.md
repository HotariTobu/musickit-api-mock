# Generate dynamic catalog responses from a pattern

Every `mock.data.*` field accepts either a `dict[str, T]` keyed by id or a `Callable[[LookupContext], T | None]`. The callable form lets you generate a resource on demand instead of enumerating every id up front — useful when the test sweeps over hundreds of ids or when ids carry pattern-encoded metadata.

## Per-id factory

```python
from musickit_api_mock import (
    Artwork,
    HlsChunk,
    HlsLayout,
    LookupContext,
    MusicKitApiMock,
    Song,
)

mock = MusicKitApiMock()


def make_song(song_id: str, *, title: str) -> Song:
    media_segment = b"mock media segment"
    return Song(
        title=title,
        artist="Test Artist",
        album="Test Album",
        duration_ms=180_000,
        artwork=Artwork(
            url="https://example.test/artwork/{w}x{h}.{f}",
            width=1200,
            height=1200,
        ),
        bitrate=256,
        sample_rate=44_100,
        file_size=0,
        genres=[],
        has_lyrics=False,
        audio_locale="en-US",
        audio_traits=[],
        has_time_synced_lyrics=False,
        is_apple_digital_master=False,
        is_mastered_for_itunes=False,
        is_vocal_attenuation_allowed=False,
        url=f"https://music.apple.com/us/song/{song_id}",
        hls_layout=HlsLayout(
            target_duration_sec=6,
            init_byte_offset=0,
            init_byte_length=0,
            chunks=(
                HlsChunk(
                    duration_sec=6.0,
                    byte_offset=0,
                    byte_length=len(media_segment),
                ),
            ),
        ),
        hls_segment=media_segment,
        preview_audio=media_segment,
    )


def resolve_song(ctx: LookupContext) -> Song | None:
    if not ctx.id.startswith("test-"):
        return None
    return make_song(ctx.id, title=f"Track {ctx.id}")


mock.data.songs = resolve_song
```

Returning `None` from the resolver signals "no such id" — the endpoint reading the source then produces the same not-found response it would for an unknown dict key.

## Locale-aware resolution

The lookup context carries the request's `?l=` value when one was present in the URL. Use it when your test asserts locale-specific behavior:

```python
def resolve_song(ctx: LookupContext) -> Song | None:
    title = f"Track {ctx.id}"
    if ctx.locale == "ja":
        title = f"トラック {ctx.id}"
    return make_song(ctx.id, title=title)
```

The mock does not fabricate a locale from the storefront slug; `ctx.locale` is `None` when the URL did not include `?l=`. Dict sources ignore the locale entirely.

## Don't reach across resources

A callable for `mock.data.songs` should resolve only the song. If the song's album / artist / genre relationships matter, populate the matching `mock.data.albums` / `mock.data.artists` / `mock.data.genres` sources too — each resource has its own source, by design. Cross-resource synthesis inside one resolver is a sign the wrong source is being asked to do the work.

## Batch endpoints need a dict

Some endpoints enumerate the full id set (e.g. the `/v1/catalog/<storefront>/genres` listing). Those require a `dict` source — callable sources can't be enumerated by design. The mock raises a descriptive `ValueError` if a batch endpoint hits a callable source; switch that specific resource to a dict.
