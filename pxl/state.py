from __future__ import annotations

import datetime
import json
import uuid
import sys

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Image:
    # The UUID derives the remote filename for the original, detail
    # and thumbnail versions of the image.
    remote_uuid: uuid.UUID

    @classmethod
    def from_json(cls, json):
        try:
            return cls(remote_uuid=uuid.UUID(json['remote_uuid']))
        except KeyError:
            return None

    def to_json(self):
        return {
            'remote_uuid': self.remote_uuid.hex,
        }


@dataclass
class Album:
    images: List[Image]
    name_display: str
    name_nav: str

    @classmethod
    def from_json(cls, json):
        try:
            name_display = json['name_display']
            name_nav = json['name_nav']
            return cls(images=list(map(Image.from_json, json['images'])),
                       name_display=name_display,
                       name_nav=name_nav)
        except KeyError:
            return None

    def to_json(self) -> Dict[str, Any]:
        return {
            'images': list(map(lambda image: image.to_json(), self.images)),
            'name_nav': self.name_nav,
            'name_display': self.name_display,
        }

    def add_image(self, image: Image) -> Album:
        return Album(images=self.images + [image],
                     name_display=self.name_display,
                     name_nav=self.name_nav)


@dataclass
class Overview:
    albums: List[Album]

    @classmethod
    def from_json(cls, json):
        try:
            return cls(albums=list(map(Album.from_json, json['albums'])))
        except KeyError:
            return None

    def to_json(self) -> Dict[str, Any]:
        return {
            'albums': list(map(lambda album: album.to_json(), self.albums)),
        }

    def add_or_replace_album(self, new_album: Album) -> Overview:
        albums = [album for album in self.albums
                        if album.name_display != new_album.name_display]
        return Overview(albums=albums + [new_album])

    def get_album_by_name(self, album_name: str) -> Optional[Album]:
        for album in self.albums:
            if album.name_display == album_name:
                return album

        return None

    @classmethod
    def empty(cls):
        return cls(albums=[])
