import uuid
import boto3  # type: ignore

from enum import Enum
from pathlib import Path
from typing import Any, Union

import pxl.state as state


def public_image(
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
    client = _get_client(config)

    extra_args = {
        'ContentType': 'image/jpeg',
        'ACL': 'public-read',
    }

    client.upload_file(Filename=str(local_filename),
                       Bucket=config.s3_bucket,
                       ExtraArgs=extra_args,
                       Key=object_name)

    return file_uuid


def private_json(
        config: state.Config,
        local_filename: Path,
        object_name: str,
    ) -> None:
    """
    Upload a local JSON file as private under a given name.
    """
    client = _get_client(config)

    extra_args = {
        'ContentType': 'application/json',
    }

    client.upload_file(Filename=str(local_filename),
                       Bucket=config.s3_bucket,
                       ExtraArgs=extra_args,
                       Key=object_name)


def get_normalized_extension(filename: Path) -> str:
    suffix_lowered = filename.suffix.lower()

    if suffix_lowered in ['.jpeg', '.jpg']:
        return '.jpg'

    return suffix_lowered


def _get_client(config: state.Config) -> Any:
    return boto3.client(service_name='s3',
                        aws_access_key_id=config.s3_key_id,
                        aws_secret_access_key=config.s3_key_secret,
                        endpoint_url=f'https://{config.s3_region}.{config.s3_endpoint}')
