.PHONY: autofix inspection typecheck preflight test\:core test\:playwright\:chromium test\:playwright\:firefox test\:playwright\:webkit test\:playwright test docs\:serve docs\:build

autofix:
	uv run ruff check --fix
	uv run ruff format

inspection:
	uv run ruff check
	uv run ruff format --check

typecheck:
	uv run ty check

preflight: inspection typecheck

test\:core:
	$(MAKE) -C packages/core test

test\:playwright\:chromium:
	$(MAKE) -C packages/playwright test:chromium

test\:playwright\:firefox:
	$(MAKE) -C packages/playwright test:firefox

test\:playwright\:webkit:
	$(MAKE) -C packages/playwright test:webkit

test\:playwright:
	$(MAKE) -C packages/playwright test

test:
	$(MAKE) test:core test:playwright

docs\:serve:
	uv run --group docs mkdocs serve

docs\:build:
	uv run --group docs mkdocs build --strict
