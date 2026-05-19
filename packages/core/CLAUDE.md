# packages/core CLAUDE.md

Guidance for the `musickit_api_mock` core package.

## Response building

Handlers must build response JSON via the schema layer, not inline.

## Browser shim environment scope

The shim must work across **all browser environments MusicKit JS targets**. Don't narrow to one runtime just because the test harness only installs one browser.

## Setter signatures

Context callables take a single named-context dataclass (`Callable[[SomeContext], T]`), never positional primitives.

## No implicit defaults

Any configuration field the user can supply defaults to `None`;
`None` *is* the unset sentinel. The unset check lives in the
resolver — reading a `None` field through a resolver raises
`ValueError`. Handlers must not invent fallback values for any
unset configuration field.

## Surface separation

Domain data (per-resource, shared across endpoints) and endpoint
response overrides (HTTP shaping per endpoint) belong on separate
surfaces. Don't mix them: per-resource data sources never hold HTTP
error factories, and endpoint overrides never hold reusable resource
lookups. The library composes Apple Music API responses from domain
data; endpoint overrides shape the HTTP response itself.
