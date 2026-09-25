# musickit-api-mock

Apple Music API mock for [MusicKit JS](https://developer.apple.com/musickit/). Runs as an **in-process request interceptor** inside browser-automation tests, so the page hits the mock instead of `api.music.apple.com`.

Useful for testing web apps that embed MusicKit JS without depending on Apple's servers, a developer token, or a signed-in Apple Music subscription.

## Where to start

- :material-rocket-launch: **[Getting started](https://hotaritobu.github.io/musickit-api-mock/0.4.0/guide/getting-started/index.md)** — install, minimum example, and how the pieces fit together.
- :material-book-open-variant: **[Surfaces overview](https://hotaritobu.github.io/musickit-api-mock/0.4.0/guide/surfaces/index.md)** — what `mock.data` / `mock.endpoints` / `mock.browser` are for.
- :material-puzzle: **[Playwright integration](https://hotaritobu.github.io/musickit-api-mock/0.4.0/guide/playwright/index.md)** — sync / async, page vs. context binding.
- :material-api: **[Reference](https://hotaritobu.github.io/musickit-api-mock/0.4.0/reference/index.md)** — auto-generated API documentation for every public class and function.
- :material-chef-hat: **[Recipes](https://hotaritobu.github.io/musickit-api-mock/0.4.0/recipes/index.md)** — task-oriented snippets ("simulate a subscription error", "trigger DRM failure", ...).

## Packages

- **`musickit-api-mock`** — transport-agnostic mock engine. Routes HTTP requests, composes Apple Music API response bodies, and ships the in-page JS shim that replaces MusicKit JS's browser integrations.
- **`musickit-api-mock-playwright`** — Playwright host adapter. Bridges the engine to `page.route` for both sync and async Playwright APIs.

## Scope

- **Target audience**: third-party developers using the default MusicKit JS configuration, i.e. calling `MusicKit.configure(...)` without Apple-internal overrides.
- **Intercepted host**: `api.music.apple.com`. Apple's own web-player override hosts (e.g. `amp-api.music.apple.com`) are out of scope.
- **Intercepted paths**: every path the default-config host emits within MusicKit JS's resource set (songs, albums, artists, library-\*, me/\*, ...). Within an intercepted path, every form the path can accept is handled — not just the subset MusicKit JS happens to send.

## Supported environments

- Python ≥ 3.12
- Playwright (sync and async) on Chromium, Firefox, and WebKit
- Linux, macOS, Windows

## License

[CC0 1.0 Universal](https://github.com/HotariTobu/musickit-api-mock/blob/main/LICENSE.txt) — public domain dedication.
