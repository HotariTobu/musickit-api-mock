# CLAUDE.md

This file contains docs-site rules for library-user documentation. Root `CLAUDE.md` owns project-wide principles; this file owns the external docs layer.

## External docs layers

- **Docstrings** — source-of-truth API documentation consumed by `mkdocstrings` and rendered into `docs/reference/`.
- **`docs/reference/`** — reference entry pages that organize `mkdocstrings` output.
- **`docs/guide/`** — hand-written walkthroughs.
- **`docs/recipes/`** — hand-written task-oriented snippets.

Pick the layer matching the change. Don't duplicate the same contract across layers.

## API reference

`docs/reference/*.md` files are mostly `mkdocstrings` entry points plus short section introductions. They are not the place to correct or override API contracts.

If reference content is wrong, fix one of these instead:

- the public type definition,
- the public docstring,
- the export surface,
- or the `mkdocstrings` / `mkdocs` configuration.

Manual edits under `docs/reference/` are acceptable only for page structure, navigation, section grouping, or brief orientation prose that does not restate a detailed API contract.

## Docstrings

Docstrings serve a third-party developer consuming the public API. Apply them to user-facing surfaces: the main mock class, configuration surfaces, dataclasses users construct, response variants users assign, callback contexts users receive, and Playwright adapter functions.

Document external behavior, usage, parameters, return values, and exceptions. Explaining **what** the public API does is the point. Internal helpers belong to the code-comment layer unless their behavior is part of the public surface.

Use Google style (`Args:` / `Returns:` / `Raises:` / `Attributes:`). This matches the project's pydocstyle convention and the `mkdocstrings-python` parser configuration.

Avoid brittle symbol references in prose. Use plain language unless the text is a user-typed surface path like `mock.data.<field>` or `mock.endpoints.<field>`.

## Guide and recipes

Guide and recipe pages are hand-written library-user docs. Keep them practical and scenario-focused.

The **replicate, don't invent** design axis is load-bearing in snippets: every field, response variant, endpoint, or behavior shown must be verified against source or a live probe before publication. A snippet with one wrong field name ships as a half-broken example that erodes user trust.

Snippet rules:

- Include required imports when the snippet is meant to stand alone.
- Prefer real public field names over `...` placeholders.
- Use `...` only for intentionally omitted app/test harness code or large data that is not relevant to the API being demonstrated.
- If a snippet cannot be directly executable, make the omitted dependency obvious and keep the API calls themselves accurate.
