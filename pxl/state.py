from __future__ import annotations

import datetime
import locale
import uuid

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple, TypeVar


class Size(Enum):
    original = auto()
    display_w_1600 = auto()
    thumbnail_w_400 = auto()

    @property
    def path_suffix(self) -> str:
        res_dict = {
            Size.original: "_o",
            Size.display_w_1600: "_w_1600",
            Size.thumbnail_w_400: "_w_400",
        }
        return res_dict[self]

    @property
    def max_width(self) -> int:
        size_switch = {
            # Not actually unlimited but people shouldn't be stupid
            # like this. Browsers don't accept these huge images.
            Size.original: 10_000_000,
            Size.display_w_1600: 1600,
            Size.thumbnail_w_400: 400,
        }
        return size_switch[self]


@dataclass
class Image:
    # The UUID derives the remote filename for the original, detail
    # and thumbnail versions of the image.
    remote_uuid: uuid.UUID
    available_sizes: List[Size]

    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> Optional[Image]:
        try:
            available_sizes = json.get("available_sizes", ["original"])
            sizes_parsed = list(map(lambda x: Size[x], available_sizes))

            return cls(
                remote_uuid=uuid.UUID(json["remote_uuid"]), available_sizes=sizes_parsed
            )
        except KeyError:
            return None

    def to_json(self) -> Dict[str, Any]:
        return {
            "remote_uuid": self.remote_uuid.hex,
            "available_sizes": list(map(lambda x: x.name, self.available_sizes)),
        }

    def get_name(self, size_name: str) -> str:
        try:
            size = Size[size_name]
            if size in self.available_sizes:
                return f"{self.remote_uuid}{size.path_suffix}"
            else:
                print(
                    f"WARN: {size_name} is not available for {self.remote_uuid}, defaulting to {Size.original}"
                )
                return f"{self.remote_uuid}{Size.original.path_suffix}"
        except KeyError:
            print(
                f"WARN: {size_name} is not a valid Size, defaulting to {Size.original}"
            )
            return Size.original.path_suffix


@dataclass
class Album:
    created: datetime.datetime
    images: List[Image]
    name_display: str
    name_nav: str

    @property
    def created_human(self) -> str:
        # We need to set the locale, because of course Python uses
        # this kind of braindamage instead of accepting a parameter
        # to the format function... Not thread safe of course because
        # of the locale API. Fun read here: https://github.com/
        # mpv-player/mpv/commit/1e70e82baa9193f6f027338b0fab0f5078971fbe
        default_locale = locale.getlocale(locale.LC_TIME)
        locale.setlocale(locale.LC_TIME, "en_US.UTF-8")

        format_str = "%b %d, %Y"  # Ex: Jan 25, 2018
        res = self.created.strftime(format_str)

        # Set back the default locale.
        locale.setlocale(locale.LC_TIME, default_locale)

        return res

    @classmethod
    def from_json(cls, json: Any) -> Optional[Album]:
        assert isinstance(json, dict)
        try:
            name_display = json["name_display"]
            name_nav = json["name_nav"]
            images = filter_optionals([Image.from_json(img) for img in json["images"]])
            return cls(
                images=images,
                name_display=name_display,
                name_nav=name_nav,
                created=datetime.datetime.fromisoformat(json["created"]),
            )
        except KeyError:
            return None

    def to_json(self) -> Dict[str, Any]:
        return {
            "images": list(map(lambda image: image.to_json(), self.images)),
            "name_nav": self.name_nav,
            "name_display": self.name_display,
            "created": self.created.isoformat(timespec="seconds"),
        }

    def add_image(self, image: Image) -> Album:
        return Album(
            images=self.images + [image],
            name_display=self.name_display,
            created=self.created,
            name_nav=self.name_nav,
        )


@dataclass
class Overview:
    albums: List[Album]

    @classmethod
    def from_json(cls, json: Any) -> Optional[Overview]:
        assert isinstance(json, dict)
        try:
            albums = filter_optionals(
                [Album.from_json(album) for album in json["albums"]]
            )
            return cls(albums=albums)
        except KeyError:
            return None

    def to_json(self) -> Dict[str, Any]:
        return {"albums": list(map(lambda album: album.to_json(), self.albums))}

    def add_or_replace_album(self, new_album: Album) -> Overview:
        albums = [
            album
            for album in self.albums
            if album.name_display != new_album.name_display
        ]
        return Overview(albums=albums + [new_album])

    def get_album_by_name(self, album_name: str) -> Optional[Album]:
        for album in self.albums:
            if album.name_display == album_name:
                return album

        return None

    def remove_album(self, album_to_remove: Album) -> Overview:
        albums = [
            album
            for album in self.albums
            if album.name_display != album_to_remove.name_display
        ]
        return Overview(albums=albums)

    @classmethod
    def empty(cls) -> Overview:
        return cls(albums=[])


T = TypeVar("T")


def filter_optionals(elems: List[Optional[T]]) -> List[T]:
    return [elem for elem in elems if elem is not None]
