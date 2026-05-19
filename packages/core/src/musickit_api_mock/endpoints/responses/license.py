"""Responses and contexts for license-acquisition endpoints.

License responses use the same numeric failure-code table as web-playback
(MKError dispatch via ``v[failureType] || v[status]``). MusicKit accepts the
code in either ``errorCode`` or ``status`` body field — the parser auto-copies
``errorCode`` into ``status`` before dispatch. The body code ``-1021`` is
rewritten to ``190121`` (WIDEVINE_CDM_EXPIRED) by MusicKit before dispatch.
HTTP status is checked only as a guard: ``!response.ok`` triggers JSON-body
error parsing equivalent to the body-status path, so the mock emits HTTP 200
with the failure code in the body and MusicKit's reaction is identical.
"""

from collections.abc import Callable
from dataclasses import dataclass

from musickit_api_mock.key_system import KeySystem


@dataclass
class LicenseResponseSuccess:
    """200 with body ``status=0`` plus license blob and optional renewal/session token."""

    license: bytes
    renew_after: int | None = None
    stkn: str | None = None


@dataclass
class LicenseResponseMediaLicense:
    """Body ``status=-1003`` → MEDIA_LICENSE."""


@dataclass
class LicenseResponseDeviceLimit:
    """Body status → DEVICE_LIMIT (mock emits the canonical code)."""


@dataclass
class LicenseResponseGeoBlock:
    """Body ``status=-1017`` → GEO_BLOCK."""


@dataclass
class LicenseResponseNotFound:
    """Body ``status=1010`` → NOT_FOUND."""


@dataclass
class LicenseResponseAuthorizationError:
    """Body ``status=2002`` → AUTHORIZATION_ERROR (triggers user-token revoke)."""


@dataclass
class LicenseResponseTokenExpired:
    """Body ``status=2034`` → TOKEN_EXPIRED (triggers token renew + retry)."""


@dataclass
class LicenseResponseSubscriptionError:
    """Body ``status=3063`` → SUBSCRIPTION_ERROR."""


@dataclass
class LicenseResponseContentUnavailable:
    """Body ``status=3076`` → CONTENT_UNAVAILABLE."""


@dataclass
class LicenseResponseContentRestricted:
    """Body ``status=3082`` → CONTENT_RESTRICTED."""


@dataclass
class LicenseResponseStreamUpsell:
    """Body ``status=3084`` → STREAM_UPSELL."""


@dataclass
class LicenseResponseServerError:
    """Body ``status=5002`` → SERVER_ERROR."""


@dataclass
class LicenseResponsePlayReadyCbcEncryptionError:
    """Body ``status=180202`` → PLAYREADY_CBC_ENCRYPTION_ERROR."""


@dataclass
class LicenseResponseWidevineCdmExpired:
    """Body ``status=190121`` → WIDEVINE_CDM_EXPIRED.

    MusicKit also rewrites body ``status=-1021`` to ``190121`` before dispatch;
    the mock emits ``190121`` directly.
    """


LicenseResponse = (
    LicenseResponseSuccess
    | LicenseResponseMediaLicense
    | LicenseResponseDeviceLimit
    | LicenseResponseGeoBlock
    | LicenseResponseNotFound
    | LicenseResponseAuthorizationError
    | LicenseResponseTokenExpired
    | LicenseResponseSubscriptionError
    | LicenseResponseContentUnavailable
    | LicenseResponseContentRestricted
    | LicenseResponseStreamUpsell
    | LicenseResponseServerError
    | LicenseResponsePlayReadyCbcEncryptionError
    | LicenseResponseWidevineCdmExpired
)


@dataclass
class LicenseCatalogSongContext:
    """Context for the catalog-song license setter."""

    adam_id: str
    key_system: KeySystem
    is_library: bool


@dataclass
class LicenseHlsOffersContext:
    """Context for the HLS-offers license setter."""

    adam_id: str
    key_system: KeySystem


@dataclass
class LicenseLiveRadioContext:
    """Context for the live-radio license setter."""

    station_id: str
    key_system: KeySystem


type LicenseCatalogSongSetter = (
    LicenseResponse
    | dict[str, LicenseResponse]
    | Callable[[LicenseCatalogSongContext], LicenseResponse]
    | None
)
type LicenseHlsOffersSetter = (
    LicenseResponse
    | dict[str, LicenseResponse]
    | Callable[[LicenseHlsOffersContext], LicenseResponse]
    | None
)
type LicenseLiveRadioSetter = (
    LicenseResponse
    | dict[str, LicenseResponse]
    | Callable[[LicenseLiveRadioContext], LicenseResponse]
    | None
)
