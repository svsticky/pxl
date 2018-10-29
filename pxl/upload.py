import uuid

from enum import Enum
from pathlib import Path
from typing import Union

import pxl.state as state


def as_public(
        config: state.Config,
        local_filename: Path,
    ) -> uuid.UUID:
    """
    Upload a local file as world readable with a random UUID.
    """
    file_uuid = uuid.uuid4()
    extension = get_normalized_extension(local_filename)
    object_name = f'{file_uuid}{extension}'
    print(f'Uploading {local_filename} as {object_name}')
    return file_uuid


def as_private(
        config: state.Config,
        local_filename: Path,
        object_name: str,
    ) -> str:
    """
    Upload a local file as private under a given name. Returns
    """
    pass


def get_normalized_extension(filename: Path) -> str:
    suffix_lowered = filename.suffix.lower()

    if suffix_lowered in ['.jpeg', '.jpg']:
        return '.jpg'

    return suffix_lowered
