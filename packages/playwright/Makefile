.PHONY: test\:chromium test\:firefox test\:webkit test

test\:chromium:
	uv run pytest --browser chromium

test\:firefox:
	uv run pytest --browser firefox

test\:webkit:
	uv run pytest --browser webkit

test:
	$(MAKE) -j3 test\:chromium test\:firefox test\:webkit
