"""Endpoint response overrides DTO + library-internal lookup wrapper.

The DTO carries user-assigned overrides for endpoint responses and
endpoint-only state. The resolver is the library-internal lookup interface;
reading an unset (default ``None``) setter raises ``ValueError``.

The resolver receives the DTO via a callback so user re-assignment of
``mock.endpoints.<field>`` after construction is reflected on the next
lookup.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar, cast

from musickit_api_mock.endpoints.responses.account import (
    AccountResponse,
    AccountSetter,
)
from musickit_api_mock.endpoints.responses.continuous_stations import (
    ContinuousStationsContext,
    ContinuousStationsResponse,
    ContinuousStationsSetter,
)
from musickit_api_mock.endpoints.responses.fairplay_cert import (
    FairPlayCertResponse,
    FairPlayCertSetter,
)
from musickit_api_mock.endpoints.responses.license import (
    LicenseCatalogSongContext,
    LicenseCatalogSongSetter,
    LicenseHlsOffersContext,
    LicenseHlsOffersSetter,
    LicenseLiveRadioContext,
    LicenseLiveRadioSetter,
    LicenseResponse,
)
from musickit_api_mock.endpoints.responses.logout import (
    LogoutResponseSuccess,
    LogoutSetter,
)
from musickit_api_mock.endpoints.responses.play_activity import (
    PlayActivityResponseSuccess,
    PlayActivitySetter,
)
from musickit_api_mock.endpoints.responses.play_assets_broadcast import (
    PlayAssetsBroadcastContext,
    PlayAssetsBroadcastResponse,
    PlayAssetsBroadcastSetter,
)
from musickit_api_mock.endpoints.responses.play_assets_catalog_song import (
    PlayAssetsCatalogSongContext,
    PlayAssetsCatalogSongResponse,
    PlayAssetsCatalogSongSetter,
)
from musickit_api_mock.endpoints.responses.play_assets_live_audio import (
    PlayAssetsLiveAudioContext,
    PlayAssetsLiveAudioResponse,
    PlayAssetsLiveAudioSetter,
)
from musickit_api_mock.endpoints.responses.play_assets_live_video import (
    PlayAssetsLiveVideoContext,
    PlayAssetsLiveVideoResponse,
    PlayAssetsLiveVideoSetter,
)
from musickit_api_mock.endpoints.responses.renew_token import (
    RenewTokenResponse,
    RenewTokenSetter,
)
from musickit_api_mock.endpoints.responses.station_next_tracks import (
    StationNextTracksContext,
    StationNextTracksSetter,
)
from musickit_api_mock.endpoints.responses.storefront import (
    StorefrontResponse,
    StorefrontSetter,
)
from musickit_api_mock.endpoints.responses.web_playback import (
    WebPlaybackContext,
    WebPlaybackResponse,
    WebPlaybackSetter,
)
from musickit_api_mock.endpoints.responses.widevine_cert import (
    WidevineCertResponse,
    WidevineCertSetter,
)


@dataclass
class EndpointResponses:
    """Per-endpoint response overrides and endpoint-only state.

    Pure data holder. Each setter overrides or parametrizes one specific
    endpoint's response. Setters accept a static response value, a callable
    taking the matching context dataclass and returning a response, or (for
    keyed endpoints) an id-keyed mapping of response values. Fields default
    to ``None``; reading an unset setter raises ``ValueError`` rather than
    synthesizing a fallback.

    Attributes:
        storefront: Override for ``/v1/me/storefront``.
        account: Override for ``/v1/me/account``.
        station_next_tracks: Override for the station next-tracks endpoint.
            Keyed by station id; value is the list of follow-up track ids.
        continuous_stations: Override for the continuous-stations endpoint.
        license_catalog_song: Override for the catalog-song license
            acquisition endpoint, keyed by adam id.
        license_hls_offers: Override for the HLS-offers license acquisition
            endpoint, keyed by adam id.
        license_live_radio: Override for the live-radio license acquisition
            endpoint, keyed by station id.
        web_playback: Override for the web-playback endpoint, keyed by
            salable adam id.
        play_assets_catalog_song: Override for catalog-song play-assets,
            keyed by adam id.
        play_assets_live_audio: Override for live-audio play-assets, keyed
            by station id.
        play_assets_live_video: Override for live-video play-assets, keyed
            by station id.
        play_assets_broadcast: Override for broadcast play-assets, keyed by
            station id.
        widevine_cert: Override for the Widevine certificate fetch endpoint.
        fairplay_cert: Override for the FairPlay certificate fetch endpoint.
        webplayer_logout: Override for the web-player logout endpoint.
        play_activity: Override for the play-activity reporting endpoint.
        renew_music_token: Override for the music-token renewal endpoint.
    """

    storefront: StorefrontSetter = None
    account: AccountSetter = None

    station_next_tracks: StationNextTracksSetter = None
    continuous_stations: ContinuousStationsSetter = None

    license_catalog_song: LicenseCatalogSongSetter = None
    license_hls_offers: LicenseHlsOffersSetter = None
    license_live_radio: LicenseLiveRadioSetter = None

    web_playback: WebPlaybackSetter = None

    play_assets_catalog_song: PlayAssetsCatalogSongSetter = None
    play_assets_live_audio: PlayAssetsLiveAudioSetter = None
    play_assets_live_video: PlayAssetsLiveVideoSetter = None
    play_assets_broadcast: PlayAssetsBroadcastSetter = None

    widevine_cert: WidevineCertSetter = None
    fairplay_cert: FairPlayCertSetter = None

    webplayer_logout: LogoutSetter = None
    play_activity: PlayActivitySetter = None
    renew_music_token: RenewTokenSetter = None


_T = TypeVar("_T")
_C = TypeVar("_C")


def _resolve_static(setter: _T | Callable[[], _T] | None, name: str) -> _T:
    if setter is None:
        raise ValueError(f"{name} is not set")
    if callable(setter):
        fn = cast("Callable[[], _T]", setter)
        return fn()
    return cast("_T", setter)


def _resolve_keyed(
    setter: _T | dict[str, _T] | Callable[[_C], _T] | None,
    ctx: _C,
    key: str,
    name: str,
) -> _T:
    if setter is None:
        raise ValueError(f"{name} is not set")
    if isinstance(setter, dict):
        d = cast("dict[str, _T]", setter)
        if key not in d:
            raise ValueError(f"{name}[{key!r}] is not set")
        return d[key]
    if callable(setter):
        fn = cast("Callable[[_C], _T]", setter)
        return fn(ctx)
    return cast("_T", setter)


def _resolve_with_context(
    setter: _T | Callable[[_C], _T] | None,
    ctx: _C,
    name: str,
) -> _T:
    if setter is None:
        raise ValueError(f"{name} is not set")
    if callable(setter):
        fn = cast("Callable[[_C], _T]", setter)
        return fn(ctx)
    return cast("_T", setter)


class _EndpointResolver:
    """Library-internal lookup interface over the endpoint-overrides DTO.

    Receives the DTO via a callback so user re-assignment of
    ``mock.endpoints.<field>`` after construction is reflected on the next
    lookup. Static setters resolve the bare value; keyed setters take the
    matching context dataclass and dispatch on its key.
    """

    def __init__(self, get_endpoints: Callable[[], EndpointResponses]) -> None:
        """Bind to the endpoint-overrides DTO via a callback."""
        self._get_endpoints = get_endpoints

    def storefront(self) -> StorefrontResponse:
        """Resolve the active ``storefront`` setter."""
        return _resolve_static(self._get_endpoints().storefront, "endpoints.storefront")

    def account(self) -> AccountResponse:
        """Resolve the active ``account`` setter."""
        return _resolve_static(self._get_endpoints().account, "endpoints.account")

    def widevine_cert(self) -> WidevineCertResponse:
        """Resolve the active ``widevine_cert`` setter."""
        return _resolve_static(
            self._get_endpoints().widevine_cert, "endpoints.widevine_cert"
        )

    def fairplay_cert(self) -> FairPlayCertResponse:
        """Resolve the active ``fairplay_cert`` setter."""
        return _resolve_static(
            self._get_endpoints().fairplay_cert, "endpoints.fairplay_cert"
        )

    def webplayer_logout(self) -> LogoutResponseSuccess:
        """Resolve the active ``webplayer_logout`` setter."""
        return _resolve_static(
            self._get_endpoints().webplayer_logout, "endpoints.webplayer_logout"
        )

    def play_activity(self) -> PlayActivityResponseSuccess:
        """Resolve the active ``play_activity`` setter."""
        return _resolve_static(
            self._get_endpoints().play_activity, "endpoints.play_activity"
        )

    def renew_music_token(self) -> RenewTokenResponse:
        """Resolve the active ``renew_music_token`` setter."""
        return _resolve_static(
            self._get_endpoints().renew_music_token, "endpoints.renew_music_token"
        )

    def station_next_tracks(self, ctx: StationNextTracksContext) -> list[str]:
        """Resolve the ``station_next_tracks`` setter for the given context."""
        return _resolve_keyed(
            self._get_endpoints().station_next_tracks,
            ctx,
            ctx.station_id,
            "endpoints.station_next_tracks",
        )

    def continuous_stations(
        self, ctx: ContinuousStationsContext
    ) -> ContinuousStationsResponse:
        """Resolve the ``continuous_stations`` setter for the given context."""
        return _resolve_with_context(
            self._get_endpoints().continuous_stations,
            ctx,
            "endpoints.continuous_stations",
        )

    def license_catalog_song(self, ctx: LicenseCatalogSongContext) -> LicenseResponse:
        """Resolve the ``license_catalog_song`` setter for the given context."""
        return _resolve_keyed(
            self._get_endpoints().license_catalog_song,
            ctx,
            ctx.adam_id,
            "endpoints.license_catalog_song",
        )

    def license_hls_offers(self, ctx: LicenseHlsOffersContext) -> LicenseResponse:
        """Resolve the ``license_hls_offers`` setter for the given context."""
        return _resolve_keyed(
            self._get_endpoints().license_hls_offers,
            ctx,
            ctx.adam_id,
            "endpoints.license_hls_offers",
        )

    def license_live_radio(self, ctx: LicenseLiveRadioContext) -> LicenseResponse:
        """Resolve the ``license_live_radio`` setter for the given context."""
        return _resolve_keyed(
            self._get_endpoints().license_live_radio,
            ctx,
            ctx.station_id,
            "endpoints.license_live_radio",
        )

    def web_playback(self, ctx: WebPlaybackContext) -> WebPlaybackResponse:
        """Resolve the ``web_playback`` setter for the given context."""
        return _resolve_keyed(
            self._get_endpoints().web_playback,
            ctx,
            ctx.salable_adam_id,
            "endpoints.web_playback",
        )

    def play_assets_catalog_song(
        self, ctx: PlayAssetsCatalogSongContext
    ) -> PlayAssetsCatalogSongResponse:
        """Resolve the ``play_assets_catalog_song`` setter for the given context."""
        return _resolve_keyed(
            self._get_endpoints().play_assets_catalog_song,
            ctx,
            ctx.adam_id,
            "endpoints.play_assets_catalog_song",
        )

    def play_assets_live_audio(
        self, ctx: PlayAssetsLiveAudioContext
    ) -> PlayAssetsLiveAudioResponse:
        """Resolve the ``play_assets_live_audio`` setter for the given context."""
        return _resolve_keyed(
            self._get_endpoints().play_assets_live_audio,
            ctx,
            ctx.station_id,
            "endpoints.play_assets_live_audio",
        )

    def play_assets_live_video(
        self, ctx: PlayAssetsLiveVideoContext
    ) -> PlayAssetsLiveVideoResponse:
        """Resolve the ``play_assets_live_video`` setter for the given context."""
        return _resolve_keyed(
            self._get_endpoints().play_assets_live_video,
            ctx,
            ctx.station_id,
            "endpoints.play_assets_live_video",
        )

    def play_assets_broadcast(
        self, ctx: PlayAssetsBroadcastContext
    ) -> PlayAssetsBroadcastResponse:
        """Resolve the ``play_assets_broadcast`` setter for the given context."""
        return _resolve_keyed(
            self._get_endpoints().play_assets_broadcast,
            ctx,
            ctx.station_id,
            "endpoints.play_assets_broadcast",
        )
