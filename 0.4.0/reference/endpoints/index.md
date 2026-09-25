# `mock.endpoints` — HTTP response overrides

Response variants you assign to `mock.endpoints.<field>`. See each field's type for accepted shape.

## Configuration surface

## EndpointResponses

```python
EndpointResponses(storefront: StorefrontSetter = None, account: AccountSetter = None, station_next_tracks: StationNextTracksSetter = None, continuous_stations: ContinuousStationsSetter = None, license_catalog_song: LicenseCatalogSongSetter = None, license_hls_offers: LicenseHlsOffersSetter = None, license_live_radio: LicenseLiveRadioSetter = None, web_playback: WebPlaybackSetter = None, play_assets_catalog_song: PlayAssetsCatalogSongSetter = None, play_assets_live_audio: PlayAssetsLiveAudioSetter = None, play_assets_live_video: PlayAssetsLiveVideoSetter = None, play_assets_broadcast: PlayAssetsBroadcastSetter = None, widevine_cert: WidevineCertSetter = None, fairplay_cert: FairPlayCertSetter = None, webplayer_logout: LogoutSetter = None, play_activity: PlayActivitySetter = None, renew_music_token: RenewTokenSetter = None)
```

Per-endpoint response overrides and endpoint-only state.

Each setter overrides or parametrizes one specific endpoint's response. Fields default to `None`; reading an unset setter raises `ValueError`. Each setter's accepted shape (static value, callable arity, mapping keying) is on its type alias.

Attributes:

| Name                       | Type                          | Description                                                                                                                                                                                                                                             |
| -------------------------- | ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `storefront`               | `StorefrontSetter`            | Override for /v1/me/storefront.                                                                                                                                                                                                                         |
| `account`                  | `AccountSetter`               | Override for /v1/me/account.                                                                                                                                                                                                                            |
| `station_next_tracks`      | `StationNextTracksSetter`     | Override for the station next-tracks endpoint. Keyed by station id; value is the list of follow-up track ids.                                                                                                                                           |
| `continuous_stations`      | `ContinuousStationsSetter`    | Override for the continuous-stations endpoint.                                                                                                                                                                                                          |
| `license_catalog_song`     | `LicenseCatalogSongSetter`    | Override for the catalog-song license acquisition endpoint, keyed by adam id.                                                                                                                                                                           |
| `license_hls_offers`       | `LicenseHlsOffersSetter`      | Override for the HLS-offers license acquisition endpoint, keyed by adam id.                                                                                                                                                                             |
| `license_live_radio`       | `LicenseLiveRadioSetter`      | Override for the live-radio license acquisition endpoint, keyed by station id.                                                                                                                                                                          |
| `web_playback`             | `WebPlaybackSetter`           | Override for the web-playback endpoint, keyed by the id MusicKit plays: the salable adam id of a catalog item, or the universal library id of a library item. The mapping form raises for a library item whose request carries no universal library id. |
| `play_assets_catalog_song` | `PlayAssetsCatalogSongSetter` | Override for catalog-song play-assets, keyed by adam id.                                                                                                                                                                                                |
| `play_assets_live_audio`   | `PlayAssetsLiveAudioSetter`   | Override for live-audio play-assets, keyed by station id.                                                                                                                                                                                               |
| `play_assets_live_video`   | `PlayAssetsLiveVideoSetter`   | Override for live-video play-assets, keyed by station id.                                                                                                                                                                                               |
| `play_assets_broadcast`    | `PlayAssetsBroadcastSetter`   | Override for broadcast play-assets, keyed by station id.                                                                                                                                                                                                |
| `widevine_cert`            | `WidevineCertSetter`          | Override for the Widevine certificate fetch endpoint.                                                                                                                                                                                                   |
| `fairplay_cert`            | `FairPlayCertSetter`          | Override for the FairPlay certificate fetch endpoint.                                                                                                                                                                                                   |
| `webplayer_logout`         | `LogoutSetter`                | Override for the web-player logout endpoint.                                                                                                                                                                                                            |
| `play_activity`            | `PlayActivitySetter`          | Override for the play-activity reporting endpoint.                                                                                                                                                                                                      |
| `renew_music_token`        | `RenewTokenSetter`            | Override for the music-token renewal endpoint.                                                                                                                                                                                                          |

## Account

## Account

```python
Account(subscription_active: bool, subscription_storefront: str)
```

Apple Music subscriber account state.

Attributes:

| Name                      | Type   | Description                                                 |
| ------------------------- | ------ | ----------------------------------------------------------- |
| `subscription_active`     | `bool` | Whether the account has an active Apple Music subscription. |
| `subscription_storefront` | `str`  | Storefront identifier the subscription is scoped to.        |

## AccountResponse

```python
AccountResponse = AccountResponseSuccess | AccountResponseSessionExpired | AccountResponseFailure
```

## AccountResponseSuccess

```python
AccountResponseSuccess(account: Account)
```

200 success carrying the active account.

Attributes:

| Name      | Type      | Description                                |
| --------- | --------- | ------------------------------------------ |
| `account` | `Account` | The active account returned to the caller. |

## AccountResponseFailure

```python
AccountResponseFailure()
```

Generic non-2xx failure that MusicKit rejects without state change.

## AccountResponseSessionExpired

```python
AccountResponseSessionExpired()
```

Auth-rejected response that triggers MusicKit's session reset.

## Storefront

## Storefront

```python
Storefront(id: str, name: str, default_language_tag: str, supported_language_tags: list[str], explicit_content_policy: Literal['allowed', 'opt-in', 'opt-out'])
```

One Apple Music storefront's identity and language config.

Attributes:

| Name                      | Type                                      | Description                                                                    |
| ------------------------- | ----------------------------------------- | ------------------------------------------------------------------------------ |
| `id`                      | `str`                                     | Storefront identifier (typically a two-letter country code).                   |
| `name`                    | `str`                                     | Display name of the storefront.                                                |
| `default_language_tag`    | `str`                                     | BCP-47 default language for the storefront.                                    |
| `supported_language_tags` | `list[str]`                               | BCP-47 language tags the storefront serves.                                    |
| `explicit_content_policy` | `Literal['allowed', 'opt-in', 'opt-out']` | Storefront-level explicit-content policy — one of allowed, opt-in, or opt-out. |

## StorefrontResponse

```python
StorefrontResponse = StorefrontResponseSuccess | StorefrontResponseSessionExpired | StorefrontResponseFailure
```

## StorefrontResponseSuccess

```python
StorefrontResponseSuccess(storefront: Storefront)
```

200 success carrying the active storefront.

Attributes:

| Name         | Type         | Description                                   |
| ------------ | ------------ | --------------------------------------------- |
| `storefront` | `Storefront` | The active storefront returned to the caller. |

## StorefrontResponseFailure

```python
StorefrontResponseFailure()
```

Generic non-2xx failure that MusicKit rejects without state change.

## StorefrontResponseSessionExpired

```python
StorefrontResponseSessionExpired()
```

Auth-rejected response that triggers MusicKit's session reset.

## Renew token

## RenewTokenResponse

```python
RenewTokenResponse = RenewTokenResponseSuccess | RenewTokenResponseUnauthorized
```

## RenewTokenResponseSuccess

```python
RenewTokenResponseSuccess(music_token: str | None = None)
```

200 success carrying the renewed music token.

Attributes:

| Name          | Type  | Description |
| ------------- | ----- | ----------- |
| `music_token` | \`str | None\`      |

## RenewTokenResponseUnauthorized

```python
RenewTokenResponseUnauthorized()
```

401 response that triggers MusicKit's user-token revoke.

## Logout

## LogoutResponse

```python
LogoutResponse = LogoutResponseSuccess
```

## LogoutResponseSuccess

```python
LogoutResponseSuccess()
```

200 success for the logout endpoint.

The caller swallows the body, so the response carries no fields.

## Play activity

## PlayActivityResponse

```python
PlayActivityResponse = PlayActivityResponseSuccess
```

## PlayActivityResponseSuccess

```python
PlayActivityResponseSuccess()
```

200 success for the fire-and-forget play-activity endpoint.

The endpoint is fire-and-forget, so the response carries no fields.

## Web playback

## WebPlaybackContext

```python
WebPlaybackContext = WebPlaybackCatalogItemContext | WebPlaybackLibraryItemContext
```

## WebPlaybackCatalogItemContext

```python
WebPlaybackCatalogItemContext(salable_adam_id: str)
```

Context for a web-playback request MusicKit makes for a catalog item.

Attributes:

| Name              | Type  | Description                                      |
| ----------------- | ----- | ------------------------------------------------ |
| `salable_adam_id` | `str` | Salable adam id the web-playback request is for. |

## WebPlaybackLibraryItemContext

```python
WebPlaybackLibraryItemContext(subscription_adam_id: str | None, universal_library_id: str | None, purchase_adam_id: str | None)
```

Context for a web-playback request MusicKit makes for a library item.

MusicKit omits each field from the request body when the library item has no value for it.

Attributes:

| Name                   | Type  | Description |
| ---------------------- | ----- | ----------- |
| `subscription_adam_id` | \`str | None\`      |
| `universal_library_id` | \`str | None\`      |
| `purchase_adam_id`     | \`str | None\`      |

## WebPlaybackSong

```python
WebPlaybackSong = WebPlaybackCatalogSong | WebPlaybackCatalogLibrarySong | WebPlaybackUploadedLibrarySong
```

## WebPlaybackCatalogLibrarySong

```python
WebPlaybackCatalogLibrarySong(hls_key_cert_url: str, hls_key_server_url: str, widevine_cert_url: str, assets: list[WebPlaybackAsset], song_id: str, hls_playlist_url: str | None = None)
```

Web-playback payload for a library song that plays through its catalog song.

Carries the catalog song's DRM URLs and assets; the mock marks the payload as needing playback reporting, as Apple does for library items.

Attributes:

| Name                 | Type                     | Description                                     |
| -------------------- | ------------------------ | ----------------------------------------------- |
| `hls_key_cert_url`   | `str`                    | FairPlay certificate endpoint for HLS playback. |
| `hls_key_server_url` | `str`                    | License-acquisition endpoint for HLS playback.  |
| `widevine_cert_url`  | `str`                    | Widevine certificate endpoint.                  |
| `assets`             | `list[WebPlaybackAsset]` | Per-variant playback assets for the song.       |
| `song_id`            | `str`                    | Catalog song id the library song plays through. |
| `hls_playlist_url`   | \`str                    | None\`                                          |

## WebPlaybackUploadedLibrarySong

```python
WebPlaybackUploadedLibrarySong(asset: WebPlaybackUploadedLibraryAsset, artwork_url: str | None = None)
```

Web-playback payload for an uploaded library song (raw file, no DRM).

The mock emits `songId: -1` and marks the payload as not needing playback reporting, as Apple does for uploads.

Attributes:

| Name          | Type                              | Description                |
| ------------- | --------------------------------- | -------------------------- |
| `asset`       | `WebPlaybackUploadedLibraryAsset` | The song's raw-file asset. |
| `artwork_url` | \`str                             | None\`                     |

## WebPlaybackUploadedLibraryAsset

```python
WebPlaybackUploadedLibraryAsset(url: str, metadata: WebPlaybackUploadedLibraryAssetMetadata)
```

The single raw-file asset of an uploaded library song.

Attributes:

| Name       | Type                                      | Description                |
| ---------- | ----------------------------------------- | -------------------------- |
| `url`      | `str`                                     | URL of the audio file.     |
| `metadata` | `WebPlaybackUploadedLibraryAssetMetadata` | Tag metadata for the file. |

## WebPlaybackUploadedLibraryAssetMetadata

```python
WebPlaybackUploadedLibraryAssetMetadata(item_name: str, artist_name: str, playlist_name: str, duration: int, kind: str, track_number: int | None = None, disc_number: int | None = None, genre: str | None = None, composer_name: str | None = None, explicit: int | None = None, release_date: str | None = None, cloud_id: int | None = None, xid: str | None = None)
```

Tag metadata Apple attaches to an uploaded library song's asset.

MusicKit copies these onto the playing media item.

Attributes:

| Name            | Type  | Description               |
| --------------- | ----- | ------------------------- |
| `item_name`     | `str` | Song title.               |
| `artist_name`   | `str` | Primary artist name.      |
| `playlist_name` | `str` | Album name.               |
| `duration`      | `int` | Duration in milliseconds. |
| `kind`          | `str` | Media kind (song).        |
| `track_number`  | \`int | None\`                    |
| `disc_number`   | \`int | None\`                    |
| `genre`         | \`str | None\`                    |
| `composer_name` | \`str | None\`                    |
| `explicit`      | \`int | None\`                    |
| `release_date`  | \`str | None\`                    |
| `cloud_id`      | \`int | None\`                    |
| `xid`           | \`str | None\`                    |

## WebPlaybackCatalogSong

```python
WebPlaybackCatalogSong(hls_key_cert_url: str, hls_key_server_url: str, widevine_cert_url: str, assets: list[WebPlaybackAsset], song_id: str, hls_playlist_url: str | None = None)
```

Web-playback payload for a catalog song (DRM URLs, asset list, optional HLS).

Attributes:

| Name                 | Type                     | Description                                     |
| -------------------- | ------------------------ | ----------------------------------------------- |
| `hls_key_cert_url`   | `str`                    | FairPlay certificate endpoint for HLS playback. |
| `hls_key_server_url` | `str`                    | License-acquisition endpoint for HLS playback.  |
| `widevine_cert_url`  | `str`                    | Widevine certificate endpoint.                  |
| `assets`             | `list[WebPlaybackAsset]` | Per-variant playback assets for the song.       |
| `song_id`            | `str`                    | Catalog song id the payload is for.             |
| `hls_playlist_url`   | \`str                    | None\`                                          |

## WebPlaybackAsset

```python
WebPlaybackAsset(flavor: str, url: str, metadata: dict[str, _JSONValue] | None = None, artwork_url: str | None = None)
```

One playback asset variant (URL plus optional metadata).

Attributes:

| Name          | Type                     | Description                                                                       |
| ------------- | ------------------------ | --------------------------------------------------------------------------------- |
| `flavor`      | `str`                    | Apple-defined flavor tag describing the asset bitrate or codec (e.g. 28:ctrp256). |
| `url`         | `str`                    | URL of the asset media.                                                           |
| `metadata`    | \`dict[str, \_JSONValue] | None\`                                                                            |
| `artwork_url` | \`str                    | None\`                                                                            |

## WebPlaybackResponse

```python
WebPlaybackResponse = WebPlaybackResponseSuccess | WebPlaybackResponseUnsupportedError | WebPlaybackResponseMediaLicense | WebPlaybackResponseDeviceLimit | WebPlaybackResponseGeoBlock | WebPlaybackResponseNotFound | WebPlaybackResponseAuthorizationError | WebPlaybackResponseTokenExpired | WebPlaybackResponseSubscriptionError | WebPlaybackResponseContentUnavailable | WebPlaybackResponseContentRestricted | WebPlaybackResponseStreamUpsell | WebPlaybackResponseServerError | WebPlaybackResponsePlayReadyCbcEncryptionError | WebPlaybackResponseWidevineCdmExpired
```

## WebPlaybackResponseSuccess

```python
WebPlaybackResponseSuccess(song_list: list[WebPlaybackSong])
```

200 response carrying one or more song payloads.

Attributes:

| Name        | Type                    | Description                                            |
| ----------- | ----------------------- | ------------------------------------------------------ |
| `song_list` | `list[WebPlaybackSong]` | Per-song web-playback payloads returned to the caller. |

## WebPlaybackResponseAuthorizationError

```python
WebPlaybackResponseAuthorizationError()
```

`failureType=2002` body that triggers AUTHORIZATION_ERROR (revoke).

## WebPlaybackResponseContentRestricted

```python
WebPlaybackResponseContentRestricted()
```

`failureType=3082` body that triggers CONTENT_RESTRICTED.

## WebPlaybackResponseContentUnavailable

```python
WebPlaybackResponseContentUnavailable()
```

`failureType=3076` body that triggers CONTENT_UNAVAILABLE.

## WebPlaybackResponseDeviceLimit

```python
WebPlaybackResponseDeviceLimit()
```

`failureType` body that triggers DEVICE_LIMIT (mock emits the canonical code).

## WebPlaybackResponseGeoBlock

```python
WebPlaybackResponseGeoBlock()
```

`failureType=-1017` body that triggers GEO_BLOCK.

## WebPlaybackResponseMediaLicense

```python
WebPlaybackResponseMediaLicense()
```

`failureType=-1003` body that triggers MEDIA_LICENSE.

## WebPlaybackResponseNotFound

```python
WebPlaybackResponseNotFound()
```

`failureType=1010` body that triggers NOT_FOUND.

## WebPlaybackResponsePlayReadyCbcEncryptionError

```python
WebPlaybackResponsePlayReadyCbcEncryptionError()
```

`failureType=180202` body for PlayReady CBC encryption error.

## WebPlaybackResponseServerError

```python
WebPlaybackResponseServerError()
```

`failureType=5002` body that triggers SERVER_ERROR.

## WebPlaybackResponseStreamUpsell

```python
WebPlaybackResponseStreamUpsell()
```

`failureType=3084` body that triggers STREAM_UPSELL.

## WebPlaybackResponseSubscriptionError

```python
WebPlaybackResponseSubscriptionError()
```

`failureType=3063` body that triggers SUBSCRIPTION_ERROR.

## WebPlaybackResponseTokenExpired

```python
WebPlaybackResponseTokenExpired()
```

`failureType=2034` body that triggers TOKEN_EXPIRED (renew + retry).

## WebPlaybackResponseUnsupportedError

```python
WebPlaybackResponseUnsupportedError()
```

Empty `songList` body that triggers UNSUPPORTED_ERROR.

## WebPlaybackResponseWidevineCdmExpired

```python
WebPlaybackResponseWidevineCdmExpired()
```

`failureType=190121` body for Widevine CDM expired.

## License (DRM)

## LicenseCatalogSongContext

```python
LicenseCatalogSongContext(adam_id: str, key_system: KeySystem, is_library: bool)
```

Context for the catalog-song license setter.

Attributes:

| Name         | Type        | Description                                                                          |
| ------------ | ----------- | ------------------------------------------------------------------------------------ |
| `adam_id`    | `str`       | Catalog song id the license is being acquired for.                                   |
| `key_system` | `KeySystem` | DRM key-system identifier of the requesting CDM.                                     |
| `is_library` | `bool`      | Whether the licensed playback is for the library counterpart (vs. the catalog song). |

## LicenseHlsOffersContext

```python
LicenseHlsOffersContext(adam_id: str, key_system: KeySystem)
```

Context for the HLS-offers license setter.

Attributes:

| Name         | Type        | Description                                      |
| ------------ | ----------- | ------------------------------------------------ |
| `adam_id`    | `str`       | Catalog song id the HLS-offers license is for.   |
| `key_system` | `KeySystem` | DRM key-system identifier of the requesting CDM. |

## LicenseLiveRadioContext

```python
LicenseLiveRadioContext(station_id: str, key_system: KeySystem)
```

Context for the live-radio license setter.

Attributes:

| Name         | Type        | Description                                       |
| ------------ | ----------- | ------------------------------------------------- |
| `station_id` | `str`       | Catalog station id the live-radio license is for. |
| `key_system` | `KeySystem` | DRM key-system identifier of the requesting CDM.  |

## LicenseResponse

```python
LicenseResponse = LicenseResponseSuccess | LicenseResponseMediaLicense | LicenseResponseDeviceLimit | LicenseResponseGeoBlock | LicenseResponseNotFound | LicenseResponseAuthorizationError | LicenseResponseTokenExpired | LicenseResponseSubscriptionError | LicenseResponseContentUnavailable | LicenseResponseContentRestricted | LicenseResponseStreamUpsell | LicenseResponseServerError | LicenseResponsePlayReadyCbcEncryptionError | LicenseResponseWidevineCdmExpired
```

## LicenseResponseSuccess

```python
LicenseResponseSuccess(license: bytes, renew_after: int | None = None, stkn: str | None = None)
```

200 success carrying the license blob and optional renewal/session token.

Attributes:

| Name          | Type    | Description                             |
| ------------- | ------- | --------------------------------------- |
| `license`     | `bytes` | License blob bytes returned to the CDM. |
| `renew_after` | \`int   | None\`                                  |
| `stkn`        | \`str   | None\`                                  |

## LicenseResponseAuthorizationError

```python
LicenseResponseAuthorizationError()
```

Body `status=2002` that triggers AUTHORIZATION_ERROR (user-token revoke).

## LicenseResponseContentRestricted

```python
LicenseResponseContentRestricted()
```

Body `status=3082` that triggers CONTENT_RESTRICTED.

## LicenseResponseContentUnavailable

```python
LicenseResponseContentUnavailable()
```

Body `status=3076` that triggers CONTENT_UNAVAILABLE.

## LicenseResponseDeviceLimit

```python
LicenseResponseDeviceLimit()
```

Body status that triggers DEVICE_LIMIT (mock emits the canonical code).

## LicenseResponseGeoBlock

```python
LicenseResponseGeoBlock()
```

Body `status=-1017` that triggers GEO_BLOCK.

## LicenseResponseMediaLicense

```python
LicenseResponseMediaLicense()
```

Body `status=-1003` that triggers MEDIA_LICENSE.

## LicenseResponseNotFound

```python
LicenseResponseNotFound()
```

Body `status=1010` that triggers NOT_FOUND.

## LicenseResponsePlayReadyCbcEncryptionError

```python
LicenseResponsePlayReadyCbcEncryptionError()
```

Body `status=180202` that triggers PLAYREADY_CBC_ENCRYPTION_ERROR.

## LicenseResponseServerError

```python
LicenseResponseServerError()
```

Body `status=5002` that triggers SERVER_ERROR.

## LicenseResponseStreamUpsell

```python
LicenseResponseStreamUpsell()
```

Body `status=3084` that triggers STREAM_UPSELL.

## LicenseResponseSubscriptionError

```python
LicenseResponseSubscriptionError()
```

Body `status=3063` that triggers SUBSCRIPTION_ERROR.

## LicenseResponseTokenExpired

```python
LicenseResponseTokenExpired()
```

Body `status=2034` that triggers TOKEN_EXPIRED (token renew + retry).

## LicenseResponseWidevineCdmExpired

```python
LicenseResponseWidevineCdmExpired()
```

Body `status=190121` that triggers WIDEVINE_CDM_EXPIRED.

MusicKit also rewrites body `status=-1021` to `190121` before dispatch; the mock emits `190121` directly.

## DRM certificates

## FairPlayCertResponse

```python
FairPlayCertResponse = FairPlayCertResponseSuccess | FairPlayCertResponseFailure
```

## FairPlayCertResponseSuccess

```python
FairPlayCertResponseSuccess(cert: bytes)
```

Success carrying the FairPlay certificate bytes.

Attributes:

| Name   | Type    | Description                     |
| ------ | ------- | ------------------------------- |
| `cert` | `bytes` | Raw FairPlay certificate bytes. |

## FairPlayCertResponseFailure

```python
FairPlayCertResponseFailure()
```

Cert fetch failure.

MusicKit reads the body bytes only; an HTTP non-OK status is enough to signal failure.

## WidevineCertResponse

```python
WidevineCertResponse = WidevineCertResponseSuccess | WidevineCertResponseFailure
```

## WidevineCertResponseSuccess

```python
WidevineCertResponseSuccess(cert: bytes)
```

Success carrying the Widevine certificate bytes.

Attributes:

| Name   | Type    | Description                     |
| ------ | ------- | ------------------------------- |
| `cert` | `bytes` | Raw Widevine certificate bytes. |

## WidevineCertResponseFailure

```python
WidevineCertResponseFailure()
```

Cert fetch failure.

MusicKit reads the body bytes only; an HTTP non-OK status is enough to signal failure.

## Play assets — catalog song

## PlayAssetsCatalogSongContext

```python
PlayAssetsCatalogSongContext(adam_id: str)
```

Context for the catalog-song play-assets setter.

Attributes:

| Name      | Type  | Description                            |
| --------- | ----- | -------------------------------------- |
| `adam_id` | `str` | Catalog song id the play-asset is for. |

## PlayAssetsCatalogSongAsset

```python
PlayAssetsCatalogSongAsset(url: str, fair_play_key_certificate_url: str, key_server_url: str, widevine_key_certificate_url: str)
```

One catalog-song play-asset (URL plus DRM endpoints).

Attributes:

| Name                            | Type  | Description                    |
| ------------------------------- | ----- | ------------------------------ |
| `url`                           | `str` | URL of the catalog-song media. |
| `fair_play_key_certificate_url` | `str` | FairPlay certificate endpoint. |
| `key_server_url`                | `str` | License-acquisition endpoint.  |
| `widevine_key_certificate_url`  | `str` | Widevine certificate endpoint. |

## PlayAssetsCatalogSongResponse

```python
PlayAssetsCatalogSongResponse = PlayAssetsCatalogSongResponseSuccess | PlayAssetsCatalogSongResponseContentUnavailable
```

## PlayAssetsCatalogSongResponseSuccess

```python
PlayAssetsCatalogSongResponseSuccess(assets: list[PlayAssetsCatalogSongAsset])
```

200 response carrying catalog-song assets.

Attributes:

| Name     | Type                               | Description                                      |
| -------- | ---------------------------------- | ------------------------------------------------ |
| `assets` | `list[PlayAssetsCatalogSongAsset]` | Catalog-song play-assets returned to the caller. |

## PlayAssetsCatalogSongResponseContentUnavailable

```python
PlayAssetsCatalogSongResponseContentUnavailable()
```

Any outcome MusicKit lumps into CONTENT_UNAVAILABLE.

For the catalog-song path MusicKit does not branch on HTTP status: empty assets, missing `results`, or any non-2xx body that parses as JSON all surface as CONTENT_UNAVAILABLE. The mock emits an empty assets body.

## Play assets — live audio

## PlayAssetsLiveAudioContext

```python
PlayAssetsLiveAudioContext(station_id: str)
```

Context for the live-audio play-assets setter.

Attributes:

| Name         | Type  | Description                                          |
| ------------ | ----- | ---------------------------------------------------- |
| `station_id` | `str` | Catalog station id the live-audio play-asset is for. |

## PlayAssetsLiveAudioAsset

```python
PlayAssetsLiveAudioAsset(url: str, fair_play_key_certificate_url: str, key_server_url: str, widevine_key_certificate_url: str)
```

One live-audio play-asset (URL plus DRM endpoints).

Attributes:

| Name                            | Type  | Description                    |
| ------------------------------- | ----- | ------------------------------ |
| `url`                           | `str` | URL of the live-audio media.   |
| `fair_play_key_certificate_url` | `str` | FairPlay certificate endpoint. |
| `key_server_url`                | `str` | License-acquisition endpoint.  |
| `widevine_key_certificate_url`  | `str` | Widevine certificate endpoint. |

## PlayAssetsLiveAudioResponse

```python
PlayAssetsLiveAudioResponse = PlayAssetsLiveAudioResponseSuccess | PlayAssetsLiveAudioResponseEmptyAssets | PlayAssetsLiveAudioResponseServerError | PlayAssetsLiveAudioResponseSubscriptionError | PlayAssetsLiveAudioResponseAccessDenied | PlayAssetsLiveAudioResponseContentUnavailable
```

## PlayAssetsLiveAudioResponseSuccess

```python
PlayAssetsLiveAudioResponseSuccess(assets: list[PlayAssetsLiveAudioAsset])
```

200 response carrying live-audio assets.

Attributes:

| Name     | Type                             | Description                                    |
| -------- | -------------------------------- | ---------------------------------------------- |
| `assets` | `list[PlayAssetsLiveAudioAsset]` | Live-audio play-assets returned to the caller. |

## PlayAssetsLiveAudioResponseAccessDenied

```python
PlayAssetsLiveAudioResponseAccessDenied()
```

403 with body `errors[0].code != "40303"` that triggers ACCESS_DENIED.

## PlayAssetsLiveAudioResponseContentUnavailable

```python
PlayAssetsLiveAudioResponseContentUnavailable()
```

Other non-2xx response, lumped by MusicKit as CONTENT_UNAVAILABLE.

## PlayAssetsLiveAudioResponseEmptyAssets

```python
PlayAssetsLiveAudioResponseEmptyAssets()
```

200 with an empty asset list that triggers CONTENT_UNAVAILABLE.

## PlayAssetsLiveAudioResponseServerError

```python
PlayAssetsLiveAudioResponseServerError()
```

500 response that triggers SERVER_ERROR.

## PlayAssetsLiveAudioResponseSubscriptionError

```python
PlayAssetsLiveAudioResponseSubscriptionError()
```

403 with body `errors[0].code = "40303"` that triggers SUBSCRIPTION_ERROR.

## Play assets — live video

## PlayAssetsLiveVideoContext

```python
PlayAssetsLiveVideoContext(station_id: str)
```

Context for the live-video play-assets setter.

Attributes:

| Name         | Type  | Description                                          |
| ------------ | ----- | ---------------------------------------------------- |
| `station_id` | `str` | Catalog station id the live-video play-asset is for. |

## PlayAssetsLiveVideoAsset

```python
PlayAssetsLiveVideoAsset(url: str, fair_play_key_certificate_url: str, key_server_url: str, widevine_key_certificate_url: str)
```

One live-video play-asset (URL plus DRM endpoints).

Attributes:

| Name                            | Type  | Description                    |
| ------------------------------- | ----- | ------------------------------ |
| `url`                           | `str` | URL of the live-video media.   |
| `fair_play_key_certificate_url` | `str` | FairPlay certificate endpoint. |
| `key_server_url`                | `str` | License-acquisition endpoint.  |
| `widevine_key_certificate_url`  | `str` | Widevine certificate endpoint. |

## PlayAssetsLiveVideoResponse

```python
PlayAssetsLiveVideoResponse = PlayAssetsLiveVideoResponseSuccess | PlayAssetsLiveVideoResponseEmptyAssets | PlayAssetsLiveVideoResponseServerError | PlayAssetsLiveVideoResponseSubscriptionError | PlayAssetsLiveVideoResponseAccessDenied | PlayAssetsLiveVideoResponseContentUnavailable
```

## PlayAssetsLiveVideoResponseSuccess

```python
PlayAssetsLiveVideoResponseSuccess(assets: list[PlayAssetsLiveVideoAsset])
```

200 response carrying live-video assets.

Attributes:

| Name     | Type                             | Description                                    |
| -------- | -------------------------------- | ---------------------------------------------- |
| `assets` | `list[PlayAssetsLiveVideoAsset]` | Live-video play-assets returned to the caller. |

## PlayAssetsLiveVideoResponseAccessDenied

```python
PlayAssetsLiveVideoResponseAccessDenied()
```

403 with body `errors[0].code != "40303"` that triggers ACCESS_DENIED.

## PlayAssetsLiveVideoResponseContentUnavailable

```python
PlayAssetsLiveVideoResponseContentUnavailable()
```

Other non-2xx response, lumped by MusicKit as CONTENT_UNAVAILABLE.

## PlayAssetsLiveVideoResponseEmptyAssets

```python
PlayAssetsLiveVideoResponseEmptyAssets()
```

200 with an empty asset list that triggers CONTENT_UNAVAILABLE.

## PlayAssetsLiveVideoResponseServerError

```python
PlayAssetsLiveVideoResponseServerError()
```

500 response that triggers SERVER_ERROR.

## PlayAssetsLiveVideoResponseSubscriptionError

```python
PlayAssetsLiveVideoResponseSubscriptionError()
```

403 with body `errors[0].code = "40303"` that triggers SUBSCRIPTION_ERROR.

## Play assets — broadcast

## PlayAssetsBroadcastContext

```python
PlayAssetsBroadcastContext(station_id: str)
```

Context for the broadcast play-assets setter.

Attributes:

| Name         | Type  | Description                                         |
| ------------ | ----- | --------------------------------------------------- |
| `station_id` | `str` | Catalog station id the broadcast play-asset is for. |

## PlayAssetsBroadcastAsset

```python
PlayAssetsBroadcastAsset(url: str)
```

One broadcast play-asset (URL only; broadcast plays unencrypted).

Attributes:

| Name  | Type  | Description                 |
| ----- | ----- | --------------------------- |
| `url` | `str` | URL of the broadcast media. |

## PlayAssetsBroadcastResponse

```python
PlayAssetsBroadcastResponse = PlayAssetsBroadcastResponseSuccess | PlayAssetsBroadcastResponseEmptyAssets | PlayAssetsBroadcastResponseServerError | PlayAssetsBroadcastResponseSubscriptionError | PlayAssetsBroadcastResponseAccessDenied | PlayAssetsBroadcastResponseContentUnavailable
```

## PlayAssetsBroadcastResponseSuccess

```python
PlayAssetsBroadcastResponseSuccess(assets: list[PlayAssetsBroadcastAsset], track_info: dict[str, _JSONValue] | None = None)
```

200 response carrying broadcast assets and optional track-info payload.

Attributes:

| Name         | Type                             | Description                                   |
| ------------ | -------------------------------- | --------------------------------------------- |
| `assets`     | `list[PlayAssetsBroadcastAsset]` | Broadcast play-assets returned to the caller. |
| `track_info` | \`dict[str, \_JSONValue]         | None\`                                        |

## PlayAssetsBroadcastResponseAccessDenied

```python
PlayAssetsBroadcastResponseAccessDenied()
```

403 with body `errors[0].code != "40303"` that triggers ACCESS_DENIED.

## PlayAssetsBroadcastResponseContentUnavailable

```python
PlayAssetsBroadcastResponseContentUnavailable()
```

Other non-2xx response, lumped by MusicKit as CONTENT_UNAVAILABLE.

## PlayAssetsBroadcastResponseEmptyAssets

```python
PlayAssetsBroadcastResponseEmptyAssets()
```

200 with an empty asset list that triggers CONTENT_UNAVAILABLE.

## PlayAssetsBroadcastResponseServerError

```python
PlayAssetsBroadcastResponseServerError()
```

500 response that triggers SERVER_ERROR.

## PlayAssetsBroadcastResponseSubscriptionError

```python
PlayAssetsBroadcastResponseSubscriptionError()
```

403 with body `errors[0].code = "40303"` that triggers SUBSCRIPTION_ERROR.

## Continuous stations

## ContinuousStation

```python
ContinuousStation(station: Station, tracks: list[str] | None = None)
```

Result a continuous-stations setter returns.

Attributes:

| Name      | Type        | Description           |
| --------- | ----------- | --------------------- |
| `station` | `Station`   | The resolved station. |
| `tracks`  | \`list[str] | None\`                |

## ContinuousStationsContext

```python
ContinuousStationsContext(seeds: list[StationSeed] | None = None)
```

Context for the continuous-stations setter.

Attributes:

| Name    | Type                | Description |
| ------- | ------------------- | ----------- |
| `seeds` | \`list[StationSeed] | None\`      |

## StationContextPlayAsset

```python
StationContextPlayAsset(bit_rate: int, url: str)
```

One bit-rate variant of a station's play asset.

Attributes:

| Name       | Type  | Description                                    |
| ---------- | ----- | ---------------------------------------------- |
| `bit_rate` | `int` | Bitrate of the variant in kilobits per second. |
| `url`      | `str` | URL of the variant's media.                    |

## StationNextTracksContext

```python
StationNextTracksContext(station_id: str, limit: int)
```

Context for the station next-tracks setter.

Attributes:

| Name         | Type  | Description                                               |
| ------------ | ----- | --------------------------------------------------------- |
| `station_id` | `str` | Catalog station id the next-tracks request is for.        |
| `limit`      | `int` | Maximum number of follow-up tracks the request asked for. |

## StationSeed

```python
StationSeed(id: str, type: Literal['songs', 'library-songs', 'music-videos'], container_id: str | None = None)
```

Seed item passed to the continuous-stations endpoint.

Attributes:

| Name           | Type                                                | Description                                                        |
| -------------- | --------------------------------------------------- | ------------------------------------------------------------------ |
| `id`           | `str`                                               | Catalog or library id of the seed resource.                        |
| `type`         | `Literal['songs', 'library-songs', 'music-videos']` | Seed resource type — one of songs, library-songs, or music-videos. |
| `container_id` | \`str                                               | None\`                                                             |

## ContinuousStationsResponse

```python
ContinuousStationsResponse = ContinuousStationsResponseSuccess | ContinuousStationsResponseContentUnsupported | ContinuousStationsResponseNoStation
```

## ContinuousStationsResponseSuccess

```python
ContinuousStationsResponseSuccess(continuous_station: ContinuousStation)
```

200 response carrying the resolved continuous station.

Attributes:

| Name                 | Type                | Description                                   |
| -------------------- | ------------------- | --------------------------------------------- |
| `continuous_station` | `ContinuousStation` | The resolved station with optional track ids. |

## ContinuousStationsResponseContentUnsupported

```python
ContinuousStationsResponseContentUnsupported(errors: list[ErrorEnvelope])
```

Non-empty `body.errors[]` that triggers CONTENT_UNSUPPORTED.

Attributes:

| Name     | Type                  | Description                                   |
| -------- | --------------------- | --------------------------------------------- |
| `errors` | `list[ErrorEnvelope]` | Error envelopes carried in the response body. |

## ContinuousStationsResponseNoStation

```python
ContinuousStationsResponseNoStation()
```

`results.station` missing that triggers CONTENT_UNAVAILABLE.

## Error envelope

## ErrorEnvelope

```python
ErrorEnvelope(code: str, title: str, status: str, detail: str | None = None, source: dict[str, _JSONValue] | None = None)
```

One entry in the Apple errors envelope (`body.errors[]`).

Attributes:

| Name     | Type                     | Description                                           |
| -------- | ------------------------ | ----------------------------------------------------- |
| `code`   | `str`                    | Apple error code string.                              |
| `title`  | `str`                    | Short error title.                                    |
| `status` | `str`                    | HTTP status code carried in the envelope as a string. |
| `detail` | \`str                    | None\`                                                |
| `source` | \`dict[str, \_JSONValue] | None\`                                                |
