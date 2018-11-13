from __future__ import annotations

import json
import sys

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PXL_DIR = Path.home() / Path('.config') / Path('pxl')
PXL_CONFIG = PXL_DIR / Path('config.json')


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

    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> Config:
        return cls(
            s3_endpoint = json['s3_endpoint'],
            s3_region = json['s3_region'],
            s3_bucket = json['s3_bucket'],
            s3_key_id = json['s3_key_id'],
            s3_key_secret = json['s3_key_secret'])


def load() -> Config:
    if not is_initialized():
        print('Please run `pxl init` before running other commands')
        sys.exit(1)

    with PXL_CONFIG.open() as f:
        config_json = json.load(f)

    config = Config.from_json(config_json)
    if config is None:
        print('Corrupted pxl config. Please fix or clean.')
        sys.exit(1)

    return config


def clean(clean_config=False) -> None:
    PXL_CONFIG.unlink()


def is_initialized() -> bool:
    return PXL_CONFIG.is_file()
