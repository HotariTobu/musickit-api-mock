"""Playwright host adapter for musickit-api-mock."""

from musickit_api_mock_playwright.async_adapter import intercept_async
from musickit_api_mock_playwright.sync_adapter import intercept

__all__ = ["intercept", "intercept_async"]
