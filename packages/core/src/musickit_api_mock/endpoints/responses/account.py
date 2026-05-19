"""Responses for the account (``/v1/me/account``) endpoint."""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class Account:
    """Apple Music subscriber account state."""

    subscription_active: bool
    subscription_storefront: str


@dataclass
class AccountResponseSuccess:
    """200 success carrying the active account."""

    account: Account


@dataclass
class AccountResponseSessionExpired:
    """Auth-rejected response that triggers MusicKit's session reset."""


@dataclass
class AccountResponseFailure:
    """Generic non-2xx failure that MusicKit rejects without state change."""


AccountResponse = (
    AccountResponseSuccess | AccountResponseSessionExpired | AccountResponseFailure
)


type AccountSetter = AccountResponse | Callable[[], AccountResponse] | None
