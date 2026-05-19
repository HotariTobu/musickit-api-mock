.PHONY: test\:chromium test\:firefox test\:webkit test

test\:chromium:
	uv run pytest --browser chromium

# webkit and firefox slow down substantially when sync_playwright and
# async_playwright tests share one pytest session; chromium is unaffected.
# Splitting the slow browsers into separate invocations bypasses the cause.
test\:firefox:
	uv run pytest --browser firefox -m sync_test
	uv run pytest --browser firefox -m async_test

test\:webkit:
	uv run pytest --browser webkit -m sync_test
	uv run pytest --browser webkit -m async_test

test:
	$(MAKE) -j3 test\:chromium test\:firefox test\:webkit
