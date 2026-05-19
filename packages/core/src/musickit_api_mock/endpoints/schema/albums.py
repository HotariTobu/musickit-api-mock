"""Album resource JSON shape builder."""

from __future__ import annotations

from typing import TYPE_CHECKING

from musickit_api_mock.endpoints.schema.builders import (
    _artwork,
    _editorial_notes,
    _strip_none,
)
from musickit_api_mock.endpoints.schema.play_params import _play_params_album

if TYPE_CHECKING:
    from musickit_api_mock.data.album import Album
    from musickit_api_mock.json_value import _JSONValue


def _album_resource(
    sf: str,
    album_id: str,
    album: Album,
    *,
    relationships: dict[str, _JSONValue] | None = None,
    extend_editorial_artwork: bool = False,
) -> dict[str, _JSONValue]:
    """Emit ``editorialArtwork`` on ``?extend=editorialArtwork``.

    Apple emits this attribute only on demand; pass
    ``extend_editorial_artwork=True`` to opt in.
    """
    attrs: dict[str, _JSONValue] = _strip_none(
        {
            "name": album.name,
            "artistName": album.artist_name,
            "artwork": _artwork(album.artwork),
            "audioTraits": album.audio_traits,
            "contentRating": album.content_rating,
            "copyright": album.copyright,
            "editorialNotes": (
                _editorial_notes(album.editorial_notes)
                if album.editorial_notes is not None
                else None
            ),
            "genreNames": album.genre_names,
            "isCompilation": album.is_compilation,
            "isComplete": album.is_complete,
            "isMasteredForItunes": album.is_mastered_for_itunes,
            "isPrerelease": album.is_prerelease,
            "isSingle": album.is_single,
            "playParams": _play_params_album(album_id),
            "recordLabel": album.record_label,
            "releaseDate": album.release_date,
            "trackCount": album.track_count,
            "upc": album.upc,
            "url": album.url,
        }
    )
    if extend_editorial_artwork and album.editorial_artwork is not None:
        attrs["editorialArtwork"] = {
            key: _artwork(art) for key, art in album.editorial_artwork.items()
        }
    out: dict[str, _JSONValue] = {
        "id": album_id,
        "type": "albums",
        "href": f"/v1/catalog/{sf}/albums/{album_id}",
        "attributes": attrs,
    }
    if relationships:
        out["relationships"] = relationships
    return out
