# `mock.data` — resource data

Resource dataclasses you assign to `mock.data.<field>`. Each field accepts a `dict[str, T]` keyed by id or a `Callable[[LookupContext], T | None]` for dynamic resolution.

## Catalog resources

::: musickit_api_mock.Song
::: musickit_api_mock.Album
::: musickit_api_mock.Artist
::: musickit_api_mock.Playlist
::: musickit_api_mock.MusicVideo
::: musickit_api_mock.Station
::: musickit_api_mock.Curator

## Library resources

::: musickit_api_mock.LibrarySong
::: musickit_api_mock.LibraryAlbum
::: musickit_api_mock.LibraryArtist
::: musickit_api_mock.LibraryMusicVideo
::: musickit_api_mock.LibraryPlaylist

## Personal recommendations

::: musickit_api_mock.PersonalRecommendation
::: musickit_api_mock.PersonalRecommendationContent
::: musickit_api_mock.PersonalRecommendationDisplay

## Supporting types

::: musickit_api_mock.Artwork
::: musickit_api_mock.Description
::: musickit_api_mock.EditorialNotes
::: musickit_api_mock.Genre
::: musickit_api_mock.Grouping
::: musickit_api_mock.Preview
::: musickit_api_mock.PreviewRange
::: musickit_api_mock.RecordLabel
::: musickit_api_mock.HlsChunk
::: musickit_api_mock.HlsLayout
::: musickit_api_mock.SongMetadataFallback

## Lookup callback context

::: musickit_api_mock.LookupContext
