# `mock.endpoints` — HTTP response overrides

Response variants you assign to `mock.endpoints.<field>`. See each field's type for accepted shape.

## Configuration surface

::: musickit_api_mock.surfaces.EndpointResponses

## Account

::: musickit_api_mock.Account
::: musickit_api_mock.AccountResponse
::: musickit_api_mock.AccountResponseSuccess
::: musickit_api_mock.AccountResponseFailure
::: musickit_api_mock.AccountResponseSessionExpired

## Storefront

::: musickit_api_mock.Storefront
::: musickit_api_mock.StorefrontResponse
::: musickit_api_mock.StorefrontResponseSuccess
::: musickit_api_mock.StorefrontResponseFailure
::: musickit_api_mock.StorefrontResponseSessionExpired

## Renew token

::: musickit_api_mock.RenewTokenResponse
::: musickit_api_mock.RenewTokenResponseSuccess
::: musickit_api_mock.RenewTokenResponseUnauthorized

## Logout

::: musickit_api_mock.LogoutResponse
::: musickit_api_mock.LogoutResponseSuccess

## Play activity

::: musickit_api_mock.PlayActivityResponse
::: musickit_api_mock.PlayActivityResponseSuccess

## Web playback

::: musickit_api_mock.WebPlaybackContext
::: musickit_api_mock.WebPlaybackSong
::: musickit_api_mock.WebPlaybackAsset
::: musickit_api_mock.WebPlaybackResponse
::: musickit_api_mock.WebPlaybackResponseSuccess
::: musickit_api_mock.WebPlaybackResponseAuthorizationError
::: musickit_api_mock.WebPlaybackResponseContentRestricted
::: musickit_api_mock.WebPlaybackResponseContentUnavailable
::: musickit_api_mock.WebPlaybackResponseDeviceLimit
::: musickit_api_mock.WebPlaybackResponseGeoBlock
::: musickit_api_mock.WebPlaybackResponseMediaLicense
::: musickit_api_mock.WebPlaybackResponseNotFound
::: musickit_api_mock.WebPlaybackResponsePlayReadyCbcEncryptionError
::: musickit_api_mock.WebPlaybackResponseServerError
::: musickit_api_mock.WebPlaybackResponseStreamUpsell
::: musickit_api_mock.WebPlaybackResponseSubscriptionError
::: musickit_api_mock.WebPlaybackResponseTokenExpired
::: musickit_api_mock.WebPlaybackResponseUnsupportedError
::: musickit_api_mock.WebPlaybackResponseWidevineCdmExpired

## License (DRM)

::: musickit_api_mock.LicenseCatalogSongContext
::: musickit_api_mock.LicenseHlsOffersContext
::: musickit_api_mock.LicenseLiveRadioContext
::: musickit_api_mock.LicenseResponse
::: musickit_api_mock.LicenseResponseSuccess
::: musickit_api_mock.LicenseResponseAuthorizationError
::: musickit_api_mock.LicenseResponseContentRestricted
::: musickit_api_mock.LicenseResponseContentUnavailable
::: musickit_api_mock.LicenseResponseDeviceLimit
::: musickit_api_mock.LicenseResponseGeoBlock
::: musickit_api_mock.LicenseResponseMediaLicense
::: musickit_api_mock.LicenseResponseNotFound
::: musickit_api_mock.LicenseResponsePlayReadyCbcEncryptionError
::: musickit_api_mock.LicenseResponseServerError
::: musickit_api_mock.LicenseResponseStreamUpsell
::: musickit_api_mock.LicenseResponseSubscriptionError
::: musickit_api_mock.LicenseResponseTokenExpired
::: musickit_api_mock.LicenseResponseWidevineCdmExpired

## DRM certificates

::: musickit_api_mock.FairPlayCertResponse
::: musickit_api_mock.FairPlayCertResponseSuccess
::: musickit_api_mock.FairPlayCertResponseFailure
::: musickit_api_mock.WidevineCertResponse
::: musickit_api_mock.WidevineCertResponseSuccess
::: musickit_api_mock.WidevineCertResponseFailure

## Play assets — catalog song

::: musickit_api_mock.PlayAssetsCatalogSongContext
::: musickit_api_mock.PlayAssetsCatalogSongAsset
::: musickit_api_mock.PlayAssetsCatalogSongResponse
::: musickit_api_mock.PlayAssetsCatalogSongResponseSuccess
::: musickit_api_mock.PlayAssetsCatalogSongResponseContentUnavailable

## Play assets — live audio

::: musickit_api_mock.PlayAssetsLiveAudioContext
::: musickit_api_mock.PlayAssetsLiveAudioAsset
::: musickit_api_mock.PlayAssetsLiveAudioResponse
::: musickit_api_mock.PlayAssetsLiveAudioResponseSuccess
::: musickit_api_mock.PlayAssetsLiveAudioResponseAccessDenied
::: musickit_api_mock.PlayAssetsLiveAudioResponseContentUnavailable
::: musickit_api_mock.PlayAssetsLiveAudioResponseEmptyAssets
::: musickit_api_mock.PlayAssetsLiveAudioResponseServerError
::: musickit_api_mock.PlayAssetsLiveAudioResponseSubscriptionError

## Play assets — live video

::: musickit_api_mock.PlayAssetsLiveVideoContext
::: musickit_api_mock.PlayAssetsLiveVideoAsset
::: musickit_api_mock.PlayAssetsLiveVideoResponse
::: musickit_api_mock.PlayAssetsLiveVideoResponseSuccess
::: musickit_api_mock.PlayAssetsLiveVideoResponseAccessDenied
::: musickit_api_mock.PlayAssetsLiveVideoResponseContentUnavailable
::: musickit_api_mock.PlayAssetsLiveVideoResponseEmptyAssets
::: musickit_api_mock.PlayAssetsLiveVideoResponseServerError
::: musickit_api_mock.PlayAssetsLiveVideoResponseSubscriptionError

## Play assets — broadcast

::: musickit_api_mock.PlayAssetsBroadcastContext
::: musickit_api_mock.PlayAssetsBroadcastAsset
::: musickit_api_mock.PlayAssetsBroadcastResponse
::: musickit_api_mock.PlayAssetsBroadcastResponseSuccess
::: musickit_api_mock.PlayAssetsBroadcastResponseAccessDenied
::: musickit_api_mock.PlayAssetsBroadcastResponseContentUnavailable
::: musickit_api_mock.PlayAssetsBroadcastResponseEmptyAssets
::: musickit_api_mock.PlayAssetsBroadcastResponseServerError
::: musickit_api_mock.PlayAssetsBroadcastResponseSubscriptionError

## Continuous stations

::: musickit_api_mock.ContinuousStation
::: musickit_api_mock.ContinuousStationsContext
::: musickit_api_mock.StationContextPlayAsset
::: musickit_api_mock.StationNextTracksContext
::: musickit_api_mock.StationSeed
::: musickit_api_mock.ContinuousStationsResponse
::: musickit_api_mock.ContinuousStationsResponseSuccess
::: musickit_api_mock.ContinuousStationsResponseContentUnsupported
::: musickit_api_mock.ContinuousStationsResponseNoStation

## Error envelope

::: musickit_api_mock.ErrorEnvelope
