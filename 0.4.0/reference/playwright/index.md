# Playwright adapter

Entry points for wiring the mock into a Playwright session.

## Sync

## intercept

```python
intercept(mock: MusicKitApiMock, target: Page | BrowserContext) -> None
```

Wire the mock into a sync Playwright page or browser context.

Installs the in-page shim init script and routes every request through the mock. Unmatched requests fall through to the network; the mock handles MusicKit JS HTTP traffic and the browser-side shim covers in-page interactions (e.g. the authorize popup, EME flavor reporting). If the mock raises (e.g. an unset setter), the adapter logs the error and aborts the request at the network layer.

Parameters:

| Name     | Type              | Description                | Default                                                                                                                                               |
| -------- | ----------------- | -------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `mock`   | `MusicKitApiMock` | The mock instance to bind. | *required*                                                                                                                                            |
| `target` | \`Page            | BrowserContext\`           | Either a sync page (binds to that single page) or a sync browser context (covers every page in the context, including popups and pages opened later). |

## Async

## intercept_async

```python
intercept_async(mock: MusicKitApiMock, target: Page | BrowserContext) -> None
```

Wire the mock into an async Playwright page or browser context.

Installs the in-page shim init script and routes every request through the mock. Unmatched requests fall through to the network; the mock handles MusicKit JS HTTP traffic and the browser-side shim covers in-page interactions (e.g. the authorize popup, EME flavor reporting). If the mock raises (e.g. an unset setter), the adapter logs the error and aborts the request at the network layer.

Parameters:

| Name     | Type              | Description                | Default                                                                                                                                                   |
| -------- | ----------------- | -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `mock`   | `MusicKitApiMock` | The mock instance to bind. | *required*                                                                                                                                                |
| `target` | \`Page            | BrowserContext\`           | Either an async page (binds to that single page) or an async browser context (covers every page in the context, including popups and pages opened later). |
