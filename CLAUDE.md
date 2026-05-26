# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Language

All documentation, code comments, commit messages, and issues must be written in **English**.

## Documentation

### Layers

Documentation in this repo splits into three scopes; each piece belongs to exactly one layer:

- **File comments / docstrings** — fine-grained design decisions scoped to a single module / class / function.
- **Directory CLAUDE.md** (e.g. `packages/core/CLAUDE.md`, `docs/CLAUDE.md`) — mid-scope decisions and conventions that span multiple files within that directory.
- **Root CLAUDE.md** (this file) — project-wide rules, the high-level architecture map, and design axes that hold across all layers.

When adding documentation, pick the layer matching the scope of the content. Don't duplicate across layers.

Docstrings are external API documentation rendered into the reference site by `mkdocstrings`. Detailed docstring rules live in `docs/CLAUDE.md`; follow that file when changing docstrings or anything under `docs/`. If API reference content is wrong, fix the source docstring, type definition, or generation config rather than patching `docs/reference/*.md` to restate the contract.

### Code comments

Default to no comments. The reader is Claude — documented external API conventions and standard library semantics are in its training data, so don't explain what Claude already knows. Write a comment only when the **why** is non-obvious even to Claude: a hidden constraint, subtle invariant, workaround for a specific bug, or behavior that would surprise the reader. Don't explain what the code does, and don't reference the current task / fix / callers. Don't carry investigation history in source (probe dates, "verified by HAR", observation-log narration) — that history belongs in commit messages, PR descriptions, or spec docs.

Don't reference other symbols by name in backticks (`` `SomeClass` ``, `` `helper_fn()` ``) — references go stale on rename / removal, silently breaking the comment. Describe behavior in plain words ("the resolver", "the helper") instead. The only safe reference is the symbol the comment is attached to (self-reference); cross-class / cross-file / cross-module symbol references are out.

## Overview

This library mocks Apple Music API requests issued by MusicKit JS. It runs as an **in-process request interceptor**.

## Repository layout

uv workspace with a thin core / adapter split:

- `packages/core` (`musickit_api_mock`) — transport-agnostic mock engine.
- `packages/playwright` (`musickit_api_mock_playwright`) — host adapter for Playwright.

## Common commands

@Makefile

## Design axes (apply when changing the public surface)

- **Replicate, don't invent.** URL hosts / paths / shapes / naming are Apple's; verify from MusicKit JS source or live observation, never invent or "design" them. The mock's value is in faithful replication — invented endpoints or shapes break the boundary that user code observes.

- **Mock target = default MusicKit JS config user.** "Default config" means a third-party developer calling `MusicKit.configure(...)` without Apple-internal overrides. Apple's own web player ships overrides (e.g. `amp-api.music.apple.com` API host) that third-party users can't reach — those are out of scope.

- **Intercepted paths come from what `api.music.apple.com` emits within MusicKit JS's resource set, not from MusicKit JS's internal URL templates.** MusicKit JS scopes the *resources* (songs, albums, artists, library-*, me/*, etc. — not `/v1/finance`); within those resources, the mock intercepts any path the default-config host emits, verified by live probe on `api.music.apple.com`. Don't narrow by MusicKit JS's internal-construction subset: if Apple emits `/songs/<id>/genres` standalone but MusicKit JS internally fetches the same data via `?include=genres`, both forms reach the mock at the HTTP boundary and both are in-scope. Don't broaden by Apple docs alone, either: a documented path with no positive probe evidence on `api.music.apple.com` is unverified, not in-scope by default — resolve by probing.

- **Classify scope by positive evidence on `api.music.apple.com`.** A path or relationship is in scope when there's positive evidence the default-config host emits it — MusicKit JS source grep, or a live probe against `api.music.apple.com`. Observations on `amp-api.music.apple.com` (Apple's own web-player host) are *silent*, not negative: Apple commonly emits the same surface on both hosts, so "observed only on amp-api" means "untested on api", not "absent on api". Resolve such gaps by probing `api.music.apple.com` directly. Apple developer docs enumerate the full Apple Music API surface across hosts — treat them as a *candidate* set to probe, not authoritative for what default-config callers actually receive. A relationship listed in Apple's docs but observed neither in MusicKit JS source nor in a live `api.music.apple.com` probe is *unverified*, not in-scope by default; the resolution is to probe, not to assume in either direction.

- **Within an intercepted path, scope is the full boundary surface — not a MusicKit JS subset.** Asymmetric from the previous axis: MusicKit JS emission narrows the *path set*, but does **not** narrow what each intercepted path accepts or returns. A query form like `?include=artists` that MusicKit JS never sends must still be handled if the path can receive it; user code or other clients may send it, and a half-handled path is a half-broken mock. Inputs: any form the path can receive (not just what MusicKit JS sends). Outputs: any field user code can observe via Apple's public API (not just what MusicKit reads internally). Environments: every runtime path the target implements (not just what your test harness installs).

- **Field scope: only fields with a real consumer.** A field exists in the mock's API surface (data dataclass fields, response attributes, callback contexts) only when consumed by MusicKit JS (which reads response fields directly or via attribute-spread that exposes them to user code) or by user code (which supplies fields as input or observes them in output). Apple-documented attributes with no actual consumer don't belong here — Apple docs are not authoritative for what the mock emits; the real consumer is.

## `typing.Any`

`typing.Any` is disallowed, including via bare generics (`dict`, `list`, `tuple` without type arguments). Reach for a stricter alternative first — `object`, `Protocol`, `TypeVar`, a union, or a recursive type alias. When a case is genuinely unavoidable, document it here with the rationale before introducing it. There are currently no accepted cases.

## Lint suppressions

Don't add or expand lint suppressions without explicit user approval. This covers:

- `[tool.ruff.lint] ignore` / `extend-ignore`
- `[tool.ruff.lint.per-file-ignores]` (new entries, expanded rule lists, new file globs)
- `# noqa: <code>` inline comments
- `# type: ignore` / `# ty: ignore` inline comments
- `[tool.ty.rules]` severity downgrades

Resolving a lint violation by suppression vs. by fixing code is a user judgment call. Surface the violation and wait for direction.

## Test suppressions

Don't add or expand test suppressions without explicit user approval. This covers:

- `pytest.skip(...)` / `pytest.xfail(...)` calls
- `@pytest.mark.skip` / `@pytest.mark.skipif` / `@pytest.mark.xfail` decorators
- Conditional gates on `browser_name`, OS, environment, etc. that route around a failing case
- Deleting or commenting out a failing test case
- Pytest config-level skip / deselect / `--ignore` entries

Resolving a test failure by suppression vs. by fixing code (or fixing the code under test) is a user judgment call. Surface the failure and wait for direction.
