# MusicKitApiMock

The library entry point. Instantiate once per test and configure the surfaces, then hand it to the host adapter.

## MusicKitApiMock

```python
MusicKitApiMock()
```

In-process Apple Music API mock for MusicKit JS.

Configuration is split into surfaces with distinct semantics, not just distinct fields. The split is load-bearing:

- `mock.data` — shared resource sources read by multiple endpoints.
- `mock.endpoints` — per-endpoint response overrides and endpoint-only state.
- `mock.browser` — state consumed by the in-page shim.

Field-level design axes for each surface live on the surface objects.

Attributes:

| Name        | Type                | Description                                                                                                                 |
| ----------- | ------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `data`      | `DataSources`       | Shared resource sources (catalog and library) read by multiple endpoints. Assign per-resource sources as mock.data.<field>. |
| `endpoints` | `EndpointResponses` | Per-endpoint response overrides and endpoint-only state. Assign per-endpoint setters as mock.endpoints.<field>.             |
| `browser`   | `BrowserBehavior`   | State consumed by the in-page shim. Assign per-field behavior as mock.browser.<field>.                                      |

Initialize all three surfaces with empty defaults and build the URL map.

### handle_request

```python
handle_request(req: Request) -> Response | None
```

Match a request against the mock and return a response, or pass through.

Host adapters call this with each intercepted request. The mock matches on host, path, and method; for matched requests it produces a response, for unmatched requests it returns nothing so the adapter can let the request continue to the network.

Parameters:

| Name  | Type      | Description                   | Default    |
| ----- | --------- | ----------------------------- | ---------- |
| `req` | `Request` | The intercepted HTTP request. | *required* |

Returns:

| Type       | Description |
| ---------- | ----------- |
| \`Response | None\`      |
| \`Response | None\`      |
| \`Response | None\`      |

### is_musickit_related

```python
is_musickit_related(req: Request) -> bool
```

Report whether a request looks MusicKit-related.

Used by host adapters to decide which requests to log or surface as "possibly should have been mocked" when no handler matched.

Parameters:

| Name  | Type      | Description              | Default    |
| ----- | --------- | ------------------------ | ---------- |
| `req` | `Request` | The request to classify. | *required* |

Returns:

| Type   | Description                                                 |
| ------ | ----------------------------------------------------------- |
| `bool` | True if the request targets a MusicKit-recognized host or   |
| `bool` | carries the MusicKit authorization header, False otherwise. |

### get_shim_script

```python
get_shim_script() -> str
```

Return the JS init script the host adapter must inject into the page.

Prepends a synchronous snapshot of any browser-state field whose current value is static (non-callable). Sync legacy paths in the shim install before the async fetch resolves when a snapshot is present; callable forms are evaluated per-probe via the internal endpoint and are not snapshotted.

Returns:

| Type  | Description                                                     |
| ----- | --------------------------------------------------------------- |
| `str` | JavaScript source ready to be added as a page init script (e.g. |
| `str` | via Playwright's add_init_script).                              |

## HTTP transport types

## Request

```python
Request(method: str, url: str, headers: dict[str, str], body: bytes | None)
```

HTTP request the host adapter forwards into the mock.

Attributes:

| Name      | Type             | Description                                                   |
| --------- | ---------------- | ------------------------------------------------------------- |
| `method`  | `str`            | HTTP method (e.g. GET, POST, OPTIONS).                        |
| `url`     | `str`            | Absolute request URL including scheme, host, path, and query. |
| `headers` | `dict[str, str]` | Request headers as a flat name/value mapping.                 |
| `body`    | \`bytes          | None\`                                                        |

## Response

```python
Response(status: int, headers: dict[str, str], body: bytes)
```

HTTP response the mock asks the host adapter to fulfill.

Attributes:

| Name      | Type             | Description                                    |
| --------- | ---------------- | ---------------------------------------------- |
| `status`  | `int`            | HTTP status code.                              |
| `headers` | `dict[str, str]` | Response headers as a flat name/value mapping. |
| `body`    | `bytes`          | Raw response body bytes.                       |
