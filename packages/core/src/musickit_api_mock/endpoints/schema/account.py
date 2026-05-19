"""Account and storefront response body builders."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.endpoints.schema.builders import _strip_none

if TYPE_CHECKING:
    from musickit_api_mock.endpoints.responses.account import Account
    from musickit_api_mock.endpoints.responses.storefront import Storefront
    from musickit_api_mock.json_value import _JSONValue


def _storefront_resource(sf: Storefront) -> dict[str, _JSONValue]:
    return {
        "id": sf.id,
        "type": "storefronts",
        "href": f"/v1/storefronts/{sf.id}",
        "attributes": {
            "name": sf.name,
            "defaultLanguageTag": sf.default_language_tag,
            "supportedLanguageTags": sf.supported_language_tags,
            "explicitContentPolicy": sf.explicit_content_policy,
        },
    }


def _account_envelope(
    account: Account,
    *,
    emit_subscription: bool = False,
    subscription_capabilities: list[str] | None = None,
) -> dict[str, _JSONValue]:
    out: dict[str, _JSONValue] = {
        "data": [
            {
                "id": "me",
                "type": "accounts",
                "href": "/v1/me/account",
                "attributes": {"restrictions": {}},
            }
        ]
    }
    meta = _strip_none(
        {
            "challenge": (
                {"subscriptionCapabilities": subscription_capabilities}
                if subscription_capabilities is not None
                else None
            ),
            "subscription": (
                {
                    "active": account.subscription_active,
                    "storefront": account.subscription_storefront,
                }
                if emit_subscription
                else None
            ),
        }
    )
    if meta:
        out["meta"] = meta
    return out


def _storefront_envelope(sf: Storefront) -> dict[str, _JSONValue]:
    return {"data": [_storefront_resource(sf)]}
