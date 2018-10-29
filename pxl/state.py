import json
import uuid
import sys

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


PXL_DIR = Path.home() / Path('.pxl/')
PXL_STATE = PXL_DIR / 'state.json'
PXL_CONFIG = PXL_DIR / 'config.json'


@dataclass
class Config:
    s3_endpoint: str
    s3_region: str
    s3_bucket: str
    s3_key_id: str
    s3_key_secret: str

    def to_json(self) -> Dict[str, str]:
        return {
            's3_endpoint': self.s3_endpoint,
            's3_region': self.s3_region,
            's3_bucket': self.s3_bucket,
            's3_key_id': self.s3_key_id,
            's3_key_secret': self.s3_key_secret,
        }


@dataclass
class Image:
    # The local filename which this image is derived from.
    # Optional: it's only populated when we add new photos to upload.
    local_filename: Optional[Path]

    # The UUID derives the remote filename for the original, detail
    # and thumbnail versions of the image.
    uuid: uuid.UUID

    def to_json(self):
        return {
            'uuid': self.uuid.hex,
        }


@dataclass
class Album:
    images: List[Image]
    name_display: str
    name_nav: str

    def to_json(self) -> Dict[str, Any]:
        return {
            'images': list(map(lambda image: image.to_json(), self.images)),
        }


@dataclass
class Index:
    albums: List[Album]

    def to_json(self) -> Dict[str, Any]:
        return {
            'albums': list(map(lambda album: album.to_json(), self.albums)),
        }


@dataclass
class State:
    index: Index

    @classmethod
    def from_json(cls, json: Any) -> Optional['State']:
        return cls(
                index=Index(
                    albums=[Album(
                            images=[Image(
                                    local_filename = Path('sticky.png'),
                                    uuid = uuid.uuid4()
                                )],
                            name_display = "Foobar",
                            name_nav = "foobar"
                        )]
                    )
                )

    def to_json(self) -> Dict[str, Any]:
        return { 'index': self.index.to_json() }


def initialize(config: Config) -> None:
    default_state = State.from_json('unused')

    PXL_DIR.mkdir(exist_ok=True)

    with PXL_CONFIG.open(mode='w') as config_file:
        json.dump(config.to_json(), config_file)

    with PXL_STATE.open(mode='w') as state_file:
        json.dump(default_state.to_json(), state_file)


def clean(clean_config=False) -> None:
    PXL_STATE.unlink()

    if all:
        PXL_CONFIG.unlink()
        PXL_DIR.rmdir()


def get_state_or_fail() -> State:
    if not is_initiated():
        print('Please run `pxl init` before running other commands')
        sys.exit(1)

    with PXL_STATE.open() as f:
        state_json = json.read(f)

    state = State.from_json(state_json)
    if state is None:
        print('Corrupted pxl state. Please fix or clean.')
        sys.exit(1)

    return state


def is_initiated() -> bool:
    return PXL_STATE.is_file()
