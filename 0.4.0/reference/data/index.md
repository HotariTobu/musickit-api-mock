# `mock.data` — resource data

Shared resource sources and dataclasses used by the data configuration surface.

## Configuration surface

## DataSources

```python
DataSources(songs: SongsSource = None, albums: AlbumsSource = None, playlists: PlaylistsSource = None, artists: ArtistsSource = None, music_videos: MusicVideosSource = None, stations: StationsSource = None, curators: CuratorsSource = None, genres: GenresSource = None, record_labels: RecordLabelsSource = None, groupings: GroupingsSource = None, personal_recommendations: PersonalRecommendationsSource = None, library_songs: LibrarySongsSource = None, library_albums: LibraryAlbumsSource = None, library_playlists: LibraryPlaylistsSource = None, library_playlist_folders: LibraryPlaylistFoldersSource = None, library_playlist_root_children: LibraryPlaylistRootChildrenSource = None, library_artists: LibraryArtistsSource = None, library_music_videos: LibraryMusicVideosSource = None)
```

Shared resource sources read by multiple endpoints.

Each field except `library_playlist_root_children` accepts an id-keyed mapping. Callable lookups are also accepted where per-id resolution is sufficient; `genres`, `record_labels`, and `personal_recommendations` require the mapping form because their endpoints enumerate ids. `library_playlists` accepts a callable for per-id lookups, but listing all library playlists requires the mapping form. The library playlist paths also answer for a folder id, so an id missing from `library_playlists` is looked up in `library_playlist_folders` when that source is set. `library_playlist_folders` accepts a callable for per-id lookups, but listing all folders and looking up the parent of anything other than a direct child of the root require the mapping form. `library_playlist_root_children` takes a list. Fields default to `None`; reading an unset source raises `ValueError`.

Attributes:

| Name                             | Type                                | Description                                                    |
| -------------------------------- | ----------------------------------- | -------------------------------------------------------------- |
| `songs`                          | `SongsSource`                       | Catalog song source.                                           |
| `albums`                         | `AlbumsSource`                      | Catalog album source.                                          |
| `playlists`                      | `PlaylistsSource`                   | Catalog playlist source.                                       |
| `artists`                        | `ArtistsSource`                     | Catalog artist source.                                         |
| `music_videos`                   | `MusicVideosSource`                 | Catalog music-video source.                                    |
| `stations`                       | `StationsSource`                    | Catalog radio-station source.                                  |
| `curators`                       | `CuratorsSource`                    | Catalog curator source (apple-curators and curators).          |
| `genres`                         | `GenresSource`                      | Catalog genre source.                                          |
| `record_labels`                  | `RecordLabelsSource`                | Catalog record-label source.                                   |
| `groupings`                      | `GroupingsSource`                   | Catalog grouping source (editorial categories).                |
| `personal_recommendations`       | `PersonalRecommendationsSource`     | User recommendation row source.                                |
| `library_songs`                  | `LibrarySongsSource`                | User-library song source.                                      |
| `library_albums`                 | `LibraryAlbumsSource`               | User-library album source.                                     |
| `library_playlists`              | `LibraryPlaylistsSource`            | User-library playlist source.                                  |
| `library_playlist_folders`       | `LibraryPlaylistFoldersSource`      | User-library playlist folder source.                           |
| `library_playlist_root_children` | `LibraryPlaylistRootChildrenSource` | Children of the playlist folder tree's root, in library order. |
| `library_artists`                | `LibraryArtistsSource`              | User-library artist source.                                    |
| `library_music_videos`           | `LibraryMusicVideosSource`          | User-library music-video source.                               |

## Catalog resources

## CatalogSong

```python
CatalogSong(title: str, artist: str, album: str, duration_ms: int, artwork: Artwork, genres: list[str], isrc: str, track_number: int, disc_number: int, release_date: str, hls_layout: HlsLayout, hls_segment: bytes, preview_audio: bytes, bitrate: int, sample_rate: int, file_size: int, has_lyrics: bool | None = None, is_apple_digital_master: bool | None = None, url: str | None = None, composer: str | None = None, content_rating: str | None = None, play_assets: list[StationContextPlayAsset] | None = None, album_ids: list[str] | None = None, artist_ids: list[str] | None = None, composer_ids: list[str] | None = None, genre_ids: list[str] | None = None, music_video_ids: list[str] | None = None, station_id: str | None = None, library_song_id: str | None = None)
```

Apple Music catalog song.

Holds the audio bytes the mock returns for HLS playback and preview, plus the layout the mock needs to compose the HLS manifest at serve time. The `from_file` constructor sources these from an audio file on disk, transcoding the audio to AAC as Apple does for its catalog.

Attributes:

| Name                      | Type                            | Description                                            |
| ------------------------- | ------------------------------- | ------------------------------------------------------ |
| `title`                   | `str`                           | Display title of the song.                             |
| `artist`                  | `str`                           | Display name of the primary artist.                    |
| `album`                   | `str`                           | Display name of the album the song belongs to.         |
| `duration_ms`             | `int`                           | Duration in milliseconds.                              |
| `artwork`                 | `Artwork`                       | Cover artwork.                                         |
| `genres`                  | `list[str]`                     | Display names of the song's genres.                    |
| `isrc`                    | `str`                           | International Standard Recording Code.                 |
| `track_number`            | `int`                           | Track number within the album.                         |
| `disc_number`             | `int`                           | Disc number within the album.                          |
| `release_date`            | `str`                           | Original release date of the song as YYYY-MM-DD.       |
| `hls_layout`              | `HlsLayout`                     | fMP4 segment layout for the HLS manifest.              |
| `hls_segment`             | `bytes`                         | Raw bytes of the fMP4 segment served for HLS playback. |
| `preview_audio`           | `bytes`                         | Raw bytes the mock serves as the preview asset.        |
| `bitrate`                 | `int`                           | Bitrate in kilobits per second.                        |
| `sample_rate`             | `int`                           | Sample rate in hertz.                                  |
| `file_size`               | `int`                           | Source file size in bytes.                             |
| `has_lyrics`              | \`bool                          | None\`                                                 |
| `is_apple_digital_master` | \`bool                          | None\`                                                 |
| `url`                     | \`str                           | None\`                                                 |
| `composer`                | \`str                           | None\`                                                 |
| `content_rating`          | \`str                           | None\`                                                 |
| `play_assets`             | \`list[StationContextPlayAsset] | None\`                                                 |
| `album_ids`               | \`list[str]                     | None\`                                                 |
| `artist_ids`              | \`list[str]                     | None\`                                                 |
| `composer_ids`            | \`list[str]                     | None\`                                                 |
| `genre_ids`               | \`list[str]                     | None\`                                                 |
| `music_video_ids`         | \`list[str]                     | None\`                                                 |
| `station_id`              | \`str                           | None\`                                                 |
| `library_song_id`         | \`str                           | None\`                                                 |

### from_file

```python
from_file(audio_path: str, fallback: SongMetadataFallback | None = None, *, preview: PreviewRange | bytes | None = None) -> CatalogSong
```

Build a song by reading metadata and audio bytes from a file on disk.

Each metadata field is taken from the file's tags first and from `fallback` when the tag is absent; an empty tag counts as absent. A required field with neither raises; an optional one is left unset.

Read from tags:

- `title` / `artist` / `album` / `composer`: the tag of the same name.
- `isrc`: the `ISRC` tag.
- `track_number` / `disc_number`: the leading integer of the `track` / `disc` tag, so `"3/12"` gives `3`; a tag with no leading integer counts as absent.
- `genres`: the `genre` tag split on commas.
- `release_date`: the original-release tag (`TDOR` for ID3, `ORIGINALDATE` for Vorbis comments) when present, else the `date` tag; only a `YYYY-MM-DD` value is used, any other form counts as absent.
- `artwork`: the first embedded picture as a data URL, at the picture's own size.

Only from `fallback`, as no tag carries them: `has_lyrics`, `is_apple_digital_master`, `url`, `content_rating`.

From the audio itself: `duration_ms`, `bitrate`, `sample_rate`, `file_size`, the HLS layout and segment (the audio transcoded to AAC), and `preview_audio`.

Parameters:

| Name         | Type                   | Description                               | Default                                                                                                                        |
| ------------ | ---------------------- | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `audio_path` | `str`                  | Filesystem path to the source audio file. | *required*                                                                                                                     |
| `fallback`   | \`SongMetadataFallback | None\`                                    | Metadata defaults applied when tags are missing the corresponding field. Leave unset to take every field from the file's tags. |
| `preview`    | \`PreviewRange         | bytes                                     | None\`                                                                                                                         |

Returns:

| Type          | Description                                 |
| ------------- | ------------------------------------------- |
| `CatalogSong` | A fully-populated song built from the file. |

Raises:

| Type         | Description                                        |
| ------------ | -------------------------------------------------- |
| `ValueError` | A required field has neither a tag nor a fallback. |
| `TypeError`  | A fallback field holds a value of the wrong type.  |

## CatalogAlbum

```python
CatalogAlbum(name: str, artist_name: str, artwork: Artwork, genre_names: list[str], track_count: int, is_compilation: bool, is_complete: bool, is_mastered_for_itunes: bool, is_single: bool, is_prerelease: bool, audio_traits: list[str], url: str, release_date: str | None = None, copyright: str | None = None, record_label: str | None = None, upc: str | None = None, track_ids: list[str] | None = None, artist_ids: list[str] | None = None, content_rating: str | None = None, editorial_notes: EditorialNotes | None = None, editorial_artwork: dict[str, Artwork] | None = None, genre_ids: list[str] | None = None, record_label_ids: list[str] | None = None, library_album_id: str | None = None)
```

Apple Music catalog album.

Attributes:

| Name                     | Type                 | Description                                          |
| ------------------------ | -------------------- | ---------------------------------------------------- |
| `name`                   | `str`                | Display title of the album.                          |
| `artist_name`            | `str`                | Display name of the primary artist.                  |
| `artwork`                | `Artwork`            | Cover artwork.                                       |
| `genre_names`            | `list[str]`          | Display names of the album's genres.                 |
| `track_count`            | `int`                | Number of tracks on the album.                       |
| `is_compilation`         | `bool`               | Whether the album is a compilation.                  |
| `is_complete`            | `bool`               | Whether the album release is complete (vs. partial). |
| `is_mastered_for_itunes` | `bool`               | Apple's "Mastered for iTunes" badge.                 |
| `is_single`              | `bool`               | Whether the release is a single.                     |
| `is_prerelease`          | `bool`               | Whether the release is a pre-release.                |
| `audio_traits`           | `list[str]`          | Audio capability tags (lossless, dolby-atmos, etc.). |
| `url`                    | `str`                | Album landing-page URL on Apple Music.               |
| `release_date`           | \`str                | None\`                                               |
| `copyright`              | \`str                | None\`                                               |
| `record_label`           | \`str                | None\`                                               |
| `upc`                    | \`str                | None\`                                               |
| `track_ids`              | \`list[str]          | None\`                                               |
| `artist_ids`             | \`list[str]          | None\`                                               |
| `content_rating`         | \`str                | None\`                                               |
| `editorial_notes`        | \`EditorialNotes     | None\`                                               |
| `editorial_artwork`      | \`dict[str, Artwork] | None\`                                               |
| `genre_ids`              | \`list[str]          | None\`                                               |
| `record_label_ids`       | \`list[str]          | None\`                                               |
| `library_album_id`       | \`str                | None\`                                               |

## CatalogArtist

```python
CatalogArtist(name: str, genre_names: list[str], url: str, artwork: Artwork | None = None, album_ids: list[str] | None = None, genre_ids: list[str] | None = None, music_video_ids: list[str] | None = None, playlist_ids: list[str] | None = None, station_id: str | None = None)
```

Apple Music catalog artist.

Attributes:

| Name              | Type        | Description                             |
| ----------------- | ----------- | --------------------------------------- |
| `name`            | `str`       | Display name of the artist.             |
| `genre_names`     | `list[str]` | Display names of the artist's genres.   |
| `url`             | `str`       | Artist landing-page URL on Apple Music. |
| `artwork`         | \`Artwork   | None\`                                  |
| `album_ids`       | \`list[str] | None\`                                  |
| `genre_ids`       | \`list[str] | None\`                                  |
| `music_video_ids` | \`list[str] | None\`                                  |
| `playlist_ids`    | \`list[str] | None\`                                  |
| `station_id`      | \`str       | None\`                                  |

## Playlist

```python
Playlist(name: str, playlist_type: Literal['user-shared', 'editorial', 'external', 'personal-mix'], curator_name: str, has_collaboration: bool, is_chart: bool, audio_traits: list[str], supports_sing: bool, url: str, artwork: Artwork | None = None, last_modified: str | None = None, track_ids: list[str] | None = None, description: Description | None = None, editorial_notes: EditorialNotes | None = None, curator_id: str | None = None, library_playlist_id: str | None = None)
```

Apple Music catalog playlist.

Catalog playlists curated by Apple Music's editorial team carry the `apple-curators` curator type — that distinction lives on the curator resource, not here.

Attributes:

| Name                  | Type                                                              | Description                                                                   |
| --------------------- | ----------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `name`                | `str`                                                             | Display name of the playlist.                                                 |
| `playlist_type`       | `Literal['user-shared', 'editorial', 'external', 'personal-mix']` | Playlist category — one of user-shared, editorial, external, or personal-mix. |
| `curator_name`        | `str`                                                             | Display name of the curator.                                                  |
| `has_collaboration`   | `bool`                                                            | Whether collaborative editing is enabled.                                     |
| `is_chart`            | `bool`                                                            | Whether the playlist is a chart playlist.                                     |
| `audio_traits`        | `list[str]`                                                       | Audio capability tags (lossless, dolby-atmos, etc.).                          |
| `supports_sing`       | `bool`                                                            | Whether the playlist supports Apple Music Sing.                               |
| `url`                 | `str`                                                             | Playlist landing-page URL on Apple Music.                                     |
| `artwork`             | \`Artwork                                                         | None\`                                                                        |
| `last_modified`       | \`str                                                             | None\`                                                                        |
| `track_ids`           | \`list[str]                                                       | None\`                                                                        |
| `description`         | \`Description                                                     | None\`                                                                        |
| `editorial_notes`     | \`EditorialNotes                                                  | None\`                                                                        |
| `curator_id`          | \`str                                                             | None\`                                                                        |
| `library_playlist_id` | \`str                                                             | None\`                                                                        |

## MusicVideo

```python
MusicVideo(name: str, artist_name: str, artwork: Artwork, duration_ms: int, genre_names: list[str], has_4k: bool, has_hdr: bool, url: str, previews: list[Preview], video_traits: list[str], isrc: str | None = None, release_date: str | None = None, album_name: str | None = None, content_rating: str | None = None, disc_number: int | None = None, track_number: int | None = None, album_ids: list[str] | None = None, artist_ids: list[str] | None = None, genre_ids: list[str] | None = None, song_ids: list[str] | None = None, library_music_video_id: str | None = None)
```

Apple Music catalog music video.

Attributes:

| Name                     | Type            | Description                                   |
| ------------------------ | --------------- | --------------------------------------------- |
| `name`                   | `str`           | Display title of the music video.             |
| `artist_name`            | `str`           | Display name of the primary artist.           |
| `artwork`                | `Artwork`       | Cover artwork.                                |
| `duration_ms`            | `int`           | Duration in milliseconds.                     |
| `genre_names`            | `list[str]`     | Display names of the video's genres.          |
| `has_4k`                 | `bool`          | Whether a 4K rendition is available.          |
| `has_hdr`                | `bool`          | Whether an HDR rendition is available.        |
| `url`                    | `str`           | Music-video landing-page URL on Apple Music.  |
| `previews`               | `list[Preview]` | Preview clip references.                      |
| `video_traits`           | `list[str]`     | Video capability tags (e.g. atmos, lossless). |
| `isrc`                   | \`str           | None\`                                        |
| `release_date`           | \`str           | None\`                                        |
| `album_name`             | \`str           | None\`                                        |
| `content_rating`         | \`str           | None\`                                        |
| `disc_number`            | \`int           | None\`                                        |
| `track_number`           | \`int           | None\`                                        |
| `album_ids`              | \`list[str]     | None\`                                        |
| `artist_ids`             | \`list[str]     | None\`                                        |
| `genre_ids`              | \`list[str]     | None\`                                        |
| `song_ids`               | \`list[str]     | None\`                                        |
| `library_music_video_id` | \`str           | None\`                                        |

## Station

```python
Station(name: str, artwork: Artwork, is_live: bool, media_kind: Literal['audio', 'video'], url: str, is_tracks_station: bool, has_drm: bool, kind: str, radio_url: str, requires_subscription: bool, editorial_notes: EditorialNotes | None = None, streaming_radio_sub_type: Literal['Episode', 'Shoutcast'] | None = None, station_provider_name: str | None = None, radio_show_id: str | None = None)
```

Apple Music catalog radio station.

Attributes:

| Name                       | Type                              | Description                                            |
| -------------------------- | --------------------------------- | ------------------------------------------------------ |
| `name`                     | `str`                             | Display name of the station.                           |
| `artwork`                  | `Artwork`                         | Hero artwork for the station.                          |
| `is_live`                  | `bool`                            | Whether the station is a live broadcast.               |
| `media_kind`               | `Literal['audio', 'video']`       | Media kind — audio or video.                           |
| `url`                      | `str`                             | Station landing-page URL on Apple Music.               |
| `is_tracks_station`        | `bool`                            | Whether the station plays a track-driven playlist.     |
| `has_drm`                  | `bool`                            | Whether the station's playback is DRM-protected.       |
| `kind`                     | `str`                             | Apple-specific station-kind tag.                       |
| `radio_url`                | `str`                             | HLS URL the station streams from.                      |
| `requires_subscription`    | `bool`                            | Whether playback requires an Apple Music subscription. |
| `editorial_notes`          | \`EditorialNotes                  | None\`                                                 |
| `streaming_radio_sub_type` | \`Literal['Episode', 'Shoutcast'] | None\`                                                 |
| `station_provider_name`    | \`str                             | None\`                                                 |
| `radio_show_id`            | \`str                             | None\`                                                 |

## Curator

```python
Curator(name: str, type: Literal['apple-curators', 'curators'], url: str, artwork: Artwork, short_name: str | None = None, kind: str | None = None, playlist_ids: list[str] | None = None, grouping_id: str | None = None)
```

Apple Music catalog curator (apple-curators or curators type).

Attributes:

| Name           | Type                                    | Description                                                                                  |
| -------------- | --------------------------------------- | -------------------------------------------------------------------------------------------- |
| `name`         | `str`                                   | Display name of the curator.                                                                 |
| `type`         | `Literal['apple-curators', 'curators']` | Curator type — apple-curators for Apple's editorial team, curators for third-party curators. |
| `url`          | `str`                                   | Curator landing-page URL on Apple Music.                                                     |
| `artwork`      | `Artwork`                               | Hero artwork for the curator.                                                                |
| `short_name`   | \`str                                   | None\`                                                                                       |
| `kind`         | \`str                                   | None\`                                                                                       |
| `playlist_ids` | \`list[str]                             | None\`                                                                                       |
| `grouping_id`  | \`str                                   | None\`                                                                                       |

## Library resources

## LibrarySong

```python
LibrarySong = CatalogLibrarySong | UploadedLibrarySong
```

## CatalogLibrarySong

```python
CatalogLibrarySong(name: str, artist_name: str, artwork: Artwork, duration_ms: int, genre_names: list[str], has_lyrics: bool, catalog_id: str, album_name: str | None = None, disc_number: int | None = None, track_number: int | None = None, release_date: str | None = None, album_ids: list[str] | None = None, artist_ids: list[str] | None = None)
```

User-library song linked to an Apple Music catalog song.

Playback streams the linked catalog song, so this variant carries no audio of its own.

Attributes:

| Name           | Type        | Description                                                                                                                                |
| -------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `name`         | `str`       | Display title of the song.                                                                                                                 |
| `artist_name`  | `str`       | Display name of the primary artist.                                                                                                        |
| `artwork`      | `Artwork`   | Cover artwork.                                                                                                                             |
| `duration_ms`  | `int`       | Duration in milliseconds.                                                                                                                  |
| `genre_names`  | `list[str]` | Display names of the song's genres.                                                                                                        |
| `has_lyrics`   | `bool`      | Whether lyrics are available.                                                                                                              |
| `catalog_id`   | `str`       | Catalog song id the library song is linked to. Emitted as playParams.catalogId / playParams.reportingId and resolved for ?include=catalog. |
| `album_name`   | \`str       | None\`                                                                                                                                     |
| `disc_number`  | \`int       | None\`                                                                                                                                     |
| `track_number` | \`int       | None\`                                                                                                                                     |
| `release_date` | \`str       | None\`                                                                                                                                     |
| `album_ids`    | \`list[str] | None\`                                                                                                                                     |
| `artist_ids`   | \`list[str] | None\`                                                                                                                                     |

## UploadedLibrarySong

```python
UploadedLibrarySong(name: str, artist_name: str | None, artwork: Artwork | None, duration_ms: int, genre_names: list[str], has_lyrics: bool, audio: bytes, disc_number: int, track_number: int, album_name: str | None = None, album_ids: list[str] | None = None, artist_ids: list[str] | None = None)
```

User-library song uploaded by the user, with no catalog counterpart.

Playback serves the song's own audio. The `from_file` constructor sources the audio and metadata from an audio file on disk the way a Music.app import does; assign to the fields afterwards to model edits made in Music.app.

Attributes:

| Name           | Type        | Description                                                 |
| -------------- | ----------- | ----------------------------------------------------------- |
| `name`         | `str`       | Display title of the song.                                  |
| `artist_name`  | \`str       | None\`                                                      |
| `artwork`      | \`Artwork   | None\`                                                      |
| `duration_ms`  | `int`       | Duration in milliseconds.                                   |
| `genre_names`  | `list[str]` | Display names of the song's genres.                         |
| `has_lyrics`   | `bool`      | Whether lyrics are available.                               |
| `audio`        | `bytes`     | AAC audio in an M4A container the mock serves for playback. |
| `disc_number`  | `int`       | Disc number, 0 when unset.                                  |
| `track_number` | `int`       | Track number, 0 when unset.                                 |
| `album_name`   | \`str       | None\`                                                      |
| `album_ids`    | \`list[str] | None\`                                                      |
| `artist_ids`   | \`list[str] | None\`                                                      |

### from_file

```python
from_file(audio_path: str) -> UploadedLibrarySong
```

Build an uploaded library song from an audio file.

Reads the file the way a Music.app import does and transcodes the audio to AAC in an M4A container, as Apple does for uploads. No tag is required; an empty tag counts as absent.

- `name`: the title tag, or the file name without its last extension when the tag is absent.
- `artist_name` / `album_name`: the artist / album tag, or `None` when absent.
- `genre_names`: the genre tag as a single element, verbatim, or `[""]` when absent.
- `track_number` / `disc_number`: the tag parsed like C's `strtol` (leading ASCII whitespace, an optional sign, then ASCII digits up to the first other character, so `"3/12"` gives `3`), reduced modulo 65536; `0` when the tag is absent, has no leading integer, or exceeds 32767 after reduction.
- `artwork`: the first embedded picture as a data URL, reported as 1200 by 1200 regardless of the picture's size, or `None` when the file has none.
- `has_lyrics`: always `False`.

Parameters:

| Name         | Type  | Description             | Default    |
| ------------ | ----- | ----------------------- | ---------- |
| `audio_path` | `str` | Path to the audio file. | *required* |

Returns:

| Type                  | Description                |
| --------------------- | -------------------------- |
| `UploadedLibrarySong` | The uploaded library song. |

## LibraryAlbum

```python
LibraryAlbum = CatalogLibraryAlbum | UploadedLibraryAlbum
```

## CatalogLibraryAlbum

```python
CatalogLibraryAlbum(name: str, artist_name: str, artwork: Artwork, genre_names: list[str], track_count: int, catalog_id: str, date_added: str | None = None, track_ids: list[str] | None = None, artist_ids: list[str] | None = None, release_date: str | None = None)
```

User-library album linked to an Apple Music catalog album.

Attributes:

| Name           | Type        | Description                                                                     |
| -------------- | ----------- | ------------------------------------------------------------------------------- |
| `name`         | `str`       | Display title of the album.                                                     |
| `artist_name`  | `str`       | Display name of the primary artist.                                             |
| `artwork`      | `Artwork`   | Cover artwork.                                                                  |
| `genre_names`  | `list[str]` | Display names of the album's genres.                                            |
| `track_count`  | `int`       | Number of tracks on the album.                                                  |
| `catalog_id`   | `str`       | Catalog album id the library album is linked to, resolved for ?include=catalog. |
| `date_added`   | \`str       | None\`                                                                          |
| `track_ids`    | \`list[str] | None\`                                                                          |
| `artist_ids`   | \`list[str] | None\`                                                                          |
| `release_date` | \`str       | None\`                                                                          |

## UploadedLibraryAlbum

```python
UploadedLibraryAlbum(name: str, artist_name: str, artwork: Artwork, genre_names: list[str], track_count: int, date_added: str | None = None, track_ids: list[str] | None = None, artist_ids: list[str] | None = None)
```

User-library album made of uploaded songs, with no catalog counterpart.

Attributes:

| Name          | Type        | Description                          |
| ------------- | ----------- | ------------------------------------ |
| `name`        | `str`       | Display title of the album.          |
| `artist_name` | `str`       | Display name of the primary artist.  |
| `artwork`     | `Artwork`   | Cover artwork.                       |
| `genre_names` | `list[str]` | Display names of the album's genres. |
| `track_count` | `int`       | Number of tracks on the album.       |
| `date_added`  | \`str       | None\`                               |
| `track_ids`   | \`list[str] | None\`                               |
| `artist_ids`  | \`list[str] | None\`                               |

## LibraryArtist

```python
LibraryArtist = CatalogLibraryArtist | UploadedLibraryArtist
```

## CatalogLibraryArtist

```python
CatalogLibraryArtist(name: str, catalog_id: str, album_ids: list[str] | None = None)
```

User-library artist linked to an Apple Music catalog artist.

Attributes:

| Name         | Type        | Description                                                                       |
| ------------ | ----------- | --------------------------------------------------------------------------------- |
| `name`       | `str`       | Display name of the artist.                                                       |
| `catalog_id` | `str`       | Catalog artist id the library artist is linked to, resolved for ?include=catalog. |
| `album_ids`  | \`list[str] | None\`                                                                            |

## UploadedLibraryArtist

```python
UploadedLibraryArtist(name: str, album_ids: list[str] | None = None)
```

User-library artist known only from uploaded songs, with no catalog counterpart.

Attributes:

| Name        | Type        | Description                 |
| ----------- | ----------- | --------------------------- |
| `name`      | `str`       | Display name of the artist. |
| `album_ids` | \`list[str] | None\`                      |

## LibraryMusicVideo

```python
LibraryMusicVideo(name: str, artist_name: str, artwork: Artwork, duration_ms: int, genre_names: list[str], release_date: str | None = None, track_number: int | None = None, album_ids: list[str] | None = None, artist_ids: list[str] | None = None, content_rating: str | None = None, album_name: str | None = None, catalog_id: str | None = None)
```

User-library music video.

Attributes:

| Name             | Type        | Description                         |
| ---------------- | ----------- | ----------------------------------- |
| `name`           | `str`       | Display title of the music video.   |
| `artist_name`    | `str`       | Display name of the primary artist. |
| `artwork`        | `Artwork`   | Cover artwork.                      |
| `duration_ms`    | `int`       | Duration in milliseconds.           |
| `genre_names`    | `list[str]` | Display names of the genres.        |
| `release_date`   | \`str       | None\`                              |
| `track_number`   | \`int       | None\`                              |
| `album_ids`      | \`list[str] | None\`                              |
| `artist_ids`     | \`list[str] | None\`                              |
| `content_rating` | \`str       | None\`                              |
| `album_name`     | \`str       | None\`                              |
| `catalog_id`     | \`str       | None\`                              |

## LibraryPlaylist

```python
LibraryPlaylist(name: str, can_edit: bool, is_public: bool, has_catalog: bool, date_added: str | None = None, last_modified_date: str | None = None, track_ids: list[str] | None = None, artwork: Artwork | None = None, description: Description | None = None, catalog_id: str | None = None)
```

User-library playlist.

Attributes:

| Name                 | Type          | Description                                      |
| -------------------- | ------------- | ------------------------------------------------ |
| `name`               | `str`         | Display name of the playlist.                    |
| `can_edit`           | `bool`        | Whether the user can edit the playlist's tracks. |
| `is_public`          | `bool`        | Whether the playlist is shared publicly.         |
| `has_catalog`        | `bool`        | Whether a corresponding catalog playlist exists. |
| `date_added`         | \`str         | None\`                                           |
| `last_modified_date` | \`str         | None\`                                           |
| `track_ids`          | \`list[str]   | None\`                                           |
| `artwork`            | \`Artwork     | None\`                                           |
| `description`        | \`Description | None\`                                           |
| `catalog_id`         | \`str         | None\`                                           |

## LibraryPlaylistFolder

```python
LibraryPlaylistFolder(name: str, date_added: str | None = None, last_modified_date: str | None = None, children: list[LibraryPlaylistFolderChild] | None = None)
```

User-library playlist folder.

Attributes:

| Name                 | Type                               | Description                 |
| -------------------- | ---------------------------------- | --------------------------- |
| `name`               | `str`                              | Display name of the folder. |
| `date_added`         | \`str                              | None\`                      |
| `last_modified_date` | \`str                              | None\`                      |
| `children`           | \`list[LibraryPlaylistFolderChild] | None\`                      |

## LibraryPlaylistFolderChild

```python
LibraryPlaylistFolderChild(type: LibraryPlaylistFolderChildKind, id: str)
```

A single child reference within a playlist folder.

Attributes:

| Name   | Type                             | Description                                 |
| ------ | -------------------------------- | ------------------------------------------- |
| `type` | `LibraryPlaylistFolderChildKind` | Resource type of the child.                 |
| `id`   | `str`                            | Library id of the child folder or playlist. |

## Personal recommendations

## PersonalRecommendation

```python
PersonalRecommendation(title: str, is_group_recommendation: bool, kind: PersonalRecommendationKind, next_update_date: str | None = None, reason: str | None = None, resource_types: list[str] | None = None, contents: list[PersonalRecommendationContent] | None = None, display: PersonalRecommendationDisplay | None = None, has_see_all: bool | None = None, version: int | None = None)
```

A single user-recommendation row.

Attributes:

| Name                      | Type                                  | Description                                                                                                                |
| ------------------------- | ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `title`                   | `str`                                 | Editorial display name shown above the row in the UI.                                                                      |
| `is_group_recommendation` | `bool`                                | Whether the row is a group recommendation.                                                                                 |
| `kind`                    | `PersonalRecommendationKind`          | Editorial category of the row (generic music recommendation, playlist-specific recommendation, recently-played row, etc.). |
| `next_update_date`        | \`str                                 | None\`                                                                                                                     |
| `reason`                  | \`str                                 | None\`                                                                                                                     |
| `resource_types`          | \`list[str]                           | None\`                                                                                                                     |
| `contents`                | \`list[PersonalRecommendationContent] | None\`                                                                                                                     |
| `display`                 | \`PersonalRecommendationDisplay       | None\`                                                                                                                     |
| `has_see_all`             | \`bool                                | None\`                                                                                                                     |
| `version`                 | \`int                                 | None\`                                                                                                                     |

## PersonalRecommendationContent

```python
PersonalRecommendationContent(type: PersonalRecommendationContentKind, id: str)
```

A single content reference within a recommendation row.

A recommendation's contents can be heterogeneous (playlists, albums, stations, music videos mixed in one row), so each entry carries its own type alongside the catalog id.

Attributes:

| Name   | Type                                | Description                                   |
| ------ | ----------------------------------- | --------------------------------------------- |
| `type` | `PersonalRecommendationContentKind` | Resource type of the linked catalog resource. |
| `id`   | `str`                               | Catalog id of the linked resource.            |

## PersonalRecommendationDisplay

```python
PersonalRecommendationDisplay(kind: str, decorations: list[str] | None = None)
```

Editorial-shelf display hint for a recommendation row.

Apple emits these values alongside the row attributes; user code can observe them via the response passthrough.

Attributes:

| Name          | Type        | Description                             |
| ------------- | ----------- | --------------------------------------- |
| `kind`        | `str`       | Apple-defined display style identifier. |
| `decorations` | \`list[str] | None\`                                  |

## Supporting types

## Artwork

```python
Artwork(url: str, width: int, height: int, bg_color: str | None = None, text_color_1: str | None = None, text_color_2: str | None = None, text_color_3: str | None = None, text_color_4: str | None = None, has_p3: bool | None = None)
```

Image asset metadata attached to most catalog and library resources.

Attributes:

| Name           | Type   | Description                                                                                                                                       |
| -------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `url`          | `str`  | Image asset URL; the mock serves it verbatim. Apple's catalog format uses URL templates with {w}, {h}, {f} placeholders the consumer substitutes. |
| `width`        | `int`  | Image width in pixels at the template's max size.                                                                                                 |
| `height`       | `int`  | Image height in pixels at the template's max size.                                                                                                |
| `bg_color`     | \`str  | None\`                                                                                                                                            |
| `text_color_1` | \`str  | None\`                                                                                                                                            |
| `text_color_2` | \`str  | None\`                                                                                                                                            |
| `text_color_3` | \`str  | None\`                                                                                                                                            |
| `text_color_4` | \`str  | None\`                                                                                                                                            |
| `has_p3`       | \`bool | None\`                                                                                                                                            |

## Description

```python
Description(standard: str, short: str | None = None)
```

Free-form long and short description text.

Attributes:

| Name       | Type  | Description            |
| ---------- | ----- | ---------------------- |
| `standard` | `str` | Long-form description. |
| `short`    | \`str | None\`                 |

## EditorialNotes

```python
EditorialNotes(name: str | None = None, short: str | None = None, standard: str | None = None, tagline: str | None = None)
```

Editorial copy shown next to a resource.

Attributes:

| Name       | Type  | Description |
| ---------- | ----- | ----------- |
| `name`     | \`str | None\`      |
| `short`    | \`str | None\`      |
| `standard` | \`str | None\`      |
| `tagline`  | \`str | None\`      |

## Genre

```python
Genre(name: str, url: str, parent_id: str | None = None, parent_name: str | None = None)
```

Apple Music catalog genre.

Attributes:

| Name          | Type  | Description                            |
| ------------- | ----- | -------------------------------------- |
| `name`        | `str` | Display name of the genre.             |
| `url`         | `str` | Genre landing-page URL on Apple Music. |
| `parent_id`   | \`str | None\`                                 |
| `parent_name` | \`str | None\`                                 |

## Grouping

```python
Grouping(name: str, url: str, artwork: Artwork | None = None)
```

Apple Music catalog grouping (editorial category for apple-curators).

Attributes:

| Name      | Type      | Description                               |
| --------- | --------- | ----------------------------------------- |
| `name`    | `str`     | Display name of the grouping.             |
| `url`     | `str`     | Grouping landing-page URL on Apple Music. |
| `artwork` | \`Artwork | None\`                                    |

## Preview

```python
Preview(url: str, hls_url: str | None = None, artwork: Artwork | None = None)
```

Preview asset reference (audio or video).

Attributes:

| Name      | Type      | Description                                     |
| --------- | --------- | ----------------------------------------------- |
| `url`     | `str`     | Progressive download URL for the preview asset. |
| `hls_url` | \`str     | None\`                                          |
| `artwork` | \`Artwork | None\`                                          |

## PreviewRange

```python
PreviewRange(start_sec: float, duration_sec: float)
```

Time window (in seconds) to extract from the source audio as the preview.

Attributes:

| Name           | Type    | Description                                               |
| -------------- | ------- | --------------------------------------------------------- |
| `start_sec`    | `float` | Start offset in seconds from the beginning of the source. |
| `duration_sec` | `float` | Preview duration in seconds.                              |

## RecordLabel

```python
RecordLabel(name: str, url: str, artwork: Artwork | None = None, description: Description | None = None)
```

Apple Music catalog record label.

Attributes:

| Name          | Type          | Description                                   |
| ------------- | ------------- | --------------------------------------------- |
| `name`        | `str`         | Display name of the record label.             |
| `url`         | `str`         | Record-label landing-page URL on Apple Music. |
| `artwork`     | \`Artwork     | None\`                                        |
| `description` | \`Description | None\`                                        |

## HlsChunk

```python
HlsChunk(duration_sec: float, byte_offset: int, byte_length: int)
```

Byte range of one media chunk inside an HLS fMP4 segment file.

Attributes:

| Name           | Type    | Description                                  |
| -------------- | ------- | -------------------------------------------- |
| `duration_sec` | `float` | Duration of this chunk in seconds.           |
| `byte_offset`  | `int`   | Offset of the chunk within the segment file. |
| `byte_length`  | `int`   | Length of the chunk in bytes.                |

## HlsLayout

```python
HlsLayout(target_duration_sec: int, init_byte_offset: int, init_byte_length: int, chunks: tuple[HlsChunk, ...])
```

fMP4 segment layout describing what the HLS manifest must declare.

The mock composes the wire-format manifest at serve time so the EXT-X-KEY directive can be selected from the active key system.

Attributes:

| Name                  | Type                   | Description                                                    |
| --------------------- | ---------------------- | -------------------------------------------------------------- |
| `target_duration_sec` | `int`                  | Target chunk duration declared in the manifest.                |
| `init_byte_offset`    | `int`                  | Offset of the initialization fragment within the segment file. |
| `init_byte_length`    | `int`                  | Length of the initialization fragment in bytes.                |
| `chunks`              | `tuple[HlsChunk, ...]` | Per-chunk byte-range descriptors in playback order.            |

## SongMetadataFallback

```python
SongMetadataFallback(title: str | None = None, artist: str | None = None, album: str | None = None, artwork: Artwork | None = None, genres: list[str] | None = None, release_date: str | None = None, track_number: int | None = None, disc_number: int | None = None, composer: str | None = None, has_lyrics: bool | None = None, isrc: str | None = None, content_rating: str | None = None, is_apple_digital_master: bool | None = None, url: str | None = None)
```

Metadata defaults applied when an audio file's tags are missing fields.

Each field corresponds to the same-named attribute on the song dataclass and is used only when the source file's tags do not supply the value. Fields left unset (`None`) provide no fallback; the loader raises if the tag is also missing and the song requires the field, and leaves the field unset otherwise.

Attributes:

| Name                      | Type        | Description |
| ------------------------- | ----------- | ----------- |
| `title`                   | \`str       | None\`      |
| `artist`                  | \`str       | None\`      |
| `album`                   | \`str       | None\`      |
| `artwork`                 | \`Artwork   | None\`      |
| `genres`                  | \`list[str] | None\`      |
| `release_date`            | \`str       | None\`      |
| `track_number`            | \`int       | None\`      |
| `disc_number`             | \`int       | None\`      |
| `composer`                | \`str       | None\`      |
| `has_lyrics`              | \`bool      | None\`      |
| `isrc`                    | \`str       | None\`      |
| `content_rating`          | \`str       | None\`      |
| `is_apple_digital_master` | \`bool      | None\`      |
| `url`                     | \`str       | None\`      |

## Lookup callback context

## LookupContext

```python
LookupContext(id: str, locale: str | None)
```

Per-request resource lookup input.

Passed to callable data sources so user code can produce locale-aware responses. Mapping sources ignore the locale (id-only mapping is the simplest contract).

Attributes:

| Name     | Type  | Description                                            |
| -------- | ----- | ------------------------------------------------------ |
| `id`     | `str` | Catalog or library id of the resource being looked up. |
| `locale` | \`str | None\`                                                 |
