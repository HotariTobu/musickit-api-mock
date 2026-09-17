# Play an uploaded library song

A song the user uploaded to their library has no Apple Music catalog counterpart. Apple returns it as a `library-songs` resource without `playParams.catalogId`, and MusicKit plays it from a raw audio file instead of a DRM stream. The mock models it as `UploadedLibrarySong` in `mock.data.library_songs` and `WebPlaybackUploadedLibrarySong` in `mock.endpoints.web_playback`.

## Register the song and its audio

```python
from musickit_api_mock import (
    MusicKitApiMock,
    UploadedLibrarySong,
    UploadedLibrarySongMetadataFallback,
)

mock = MusicKitApiMock()

mock.data.library_songs = {
    "i.abc123": UploadedLibrarySong.from_file(
        "path/to/upload.m4a",
        UploadedLibrarySongMetadataFallback(has_lyrics=False),
    ),
}
```

`from_file` reads the title, artist, album, genre, track / disc numbers, duration, and embedded artwork from the file and keeps the file bytes as the served audio. Anything the file lacks comes from the fallback; a required field missing from both raises `ValueError`.

## Answer the web-playback request

When MusicKit plays the song it posts `{"universalLibraryId": "i.abc123"}` to the web-playback endpoint, so key the setter by the library id and point the asset at a `blobstore.apple.com` URL whose second path segment is the library id:

```python
from musickit_api_mock import (
    WebPlaybackResponseSuccess,
    WebPlaybackUploadedLibraryAsset,
    WebPlaybackUploadedLibraryAssetMetadata,
    WebPlaybackUploadedLibrarySong,
)

mock.endpoints.web_playback = {
    "i.abc123": WebPlaybackResponseSuccess(
        song_list=[
            WebPlaybackUploadedLibrarySong(
                asset=WebPlaybackUploadedLibraryAsset(
                    url="https://store-001.blobstore.apple.com/uploads/i.abc123/audio",
                    metadata=WebPlaybackUploadedLibraryAssetMetadata(
                        item_name="Home Recording",
                        artist_name="Me",
                        playlist_name="Demos",
                        duration=128_373,
                        kind="song",
                    ),
                ),
            )
        ]
    ),
}
```

The mock serves `https://<store>.blobstore.apple.com/<bucket>/<library song id>/audio` from the registered song's audio bytes with `Content-Type: audio/mp4`; the store label and bucket segment are free-form, and a signing query string is ignored.
