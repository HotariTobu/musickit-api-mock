# `mock.browser` — in-page shim state

State the in-page JS shim consumes inside the browser's JavaScript runtime. These are **not HTTP responses** — they configure what the page sees from MusicKit JS's browser integrations.

## Configuration surface

## BrowserBehavior

```python
BrowserBehavior(authorize_response: AuthorizeResponseSetter = None, eme_flavor: EmeFlavorSetter = None)
```

State that lives inside the page; the browser-side shim consumes it.

Configures the in-page shim's runtime behavior, not HTTP responses. Fields default to `None`; reading an unset value raises `ValueError`.

Attributes:

| Name                 | Type                      | Description                                                                                                                                                                                                                                                              |
| -------------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `authorize_response` | `AuthorizeResponseSetter` | Response the shim returns from the authorize flow MusicKit JS opens on sign-in. Accepts either a static response variant or a zero-argument callable returning one (the callable is re-evaluated on each authorize attempt, so a fresh value can be returned per popup). |
| `eme_flavor`         | `EmeFlavorSetter`         | DRM key system the shim reports as supported when MusicKit JS probes Encrypted Media Extensions. Use one of the three key-system identifier strings.                                                                                                                     |

## Authorize popup

## AuthorizeResponse

```python
AuthorizeResponse = AuthorizeSuccess | AuthorizeDecline | AuthorizeClose | AuthorizeSwitchUserId | AuthorizeUnavailable
```

## AuthorizeSuccess

```python
AuthorizeSuccess(user_token: str, cid: str, restricted: int | None = None)
```

User accepted the authorize prompt; carries the issued user token.

Attributes:

| Name         | Type  | Description                                                                                                |
| ------------ | ----- | ---------------------------------------------------------------------------------------------------------- |
| `user_token` | `str` | Apple Music user token MusicKit JS stores and sends as the music-user-token header on subsequent requests. |
| `cid`        | `str` | The cid Apple's authorize service issues alongside the token.                                              |
| `restricted` | \`int | None\`                                                                                                     |

## AuthorizeDecline

```python
AuthorizeDecline()
```

User declined the authorize prompt.

## AuthorizeClose

```python
AuthorizeClose()
```

User closed the authorize prompt without choosing.

## AuthorizeSwitchUserId

```python
AuthorizeSwitchUserId()
```

User switched Apple ID mid-flow; MusicKit JS retries authorization.

## AuthorizeUnavailable

```python
AuthorizeUnavailable()
```

Authorize flow is not available (e.g. service unavailable).

## EME key system

## KeySystem

```python
KeySystem = Literal['com.apple.fps', 'com.microsoft.playready', 'com.widevine.alpha']
```
