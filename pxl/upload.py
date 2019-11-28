from __future__ import annotations

import boto3  # type: ignore
import datetime
import getpass
import json
import socket
import sys
import uuid

from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterator, Union, Optional

import pxl.config as config
import pxl.compress as compress
import pxl.state as state


@dataclass
class Client:
    boto: Any  # Boto is bad at typing.
    cfg: config.Config


@dataclass
class Lock:
    user: str
    hostname: str
    start_time: datetime.datetime

    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> Lock:
        return cls(
            user=json["user"],
            hostname=json["hostname"],
            start_time=datetime.datetime.fromisoformat(json["start_time"]),
        )

    def to_json(self) -> Dict[str, str]:
        return {
            "user": self.user,
            "hostname": self.hostname,
            "start_time": self.start_time.isoformat(timespec="seconds"),
        }

    @classmethod
    def new(cls) -> Lock:
        return cls(
            user=getpass.getuser(),
            hostname=socket.gethostname(),
            start_time=datetime.datetime.now(),
        )


@contextmanager
def client(cfg: config.Config, *, break_lock: bool = False) -> Iterator[Client]:
    """Contextmanager for an upload client"""
    endpoint_url = f"https://{cfg.s3_region}.{cfg.s3_endpoint}"
    boto = boto3.client(
        service_name="s3",
        aws_access_key_id=cfg.s3_key_id,
        aws_secret_access_key=cfg.s3_key_secret,
        endpoint_url=endpoint_url,
    )

    placed_lock = False
    try:
        resp = boto.list_objects_v2(Prefix="lock.json", Bucket=cfg.s3_bucket)
        for obj in resp.get("Contents", []):
            object_data = boto.get_object(Key="lock.json", Bucket=cfg.s3_bucket)
            lock_json = json.load(object_data["Body"])
            existing_lock = Lock.from_json(lock_json)

            lock_info = f"{existing_lock.user}@{existing_lock.hostname} on {existing_lock.start_time}"

            if not break_lock:
                print("Lock exists, aborting.")
                print(f"The state was locked by {lock_info}.")
                print("Pass --force to ignore this.")

                sys.exit(1)

            else:
                print(f"Breaking a lock set by {lock_info}.")

        boto.put_object(
            Body=json.dumps(Lock.new().to_json()),
            Bucket=cfg.s3_bucket,
            ContentType="application/json",
            Key="lock.json",
        )
        placed_lock = True

        yield Client(boto=boto, cfg=cfg)

    finally:
        if placed_lock:
            boto.delete_objects(
                Delete={"Objects": [{"Key": "lock.json"}]}, Bucket=cfg.s3_bucket
            )


def public_image_with_size(client: Client, local_filename: Path) -> state.Image:
    file_uuid = uuid.uuid4()
    extension = get_normalized_extension(local_filename)

    local_scaled_files = compress.compress_image(local_filename)
    for size, local_filename in local_scaled_files.items():
        object_name = f"{file_uuid}{size.path_suffix}{extension}"
        public_image(client, local_filename, object_name)

    return state.Image(
        remote_uuid=file_uuid, available_sizes=list(local_scaled_files.keys())
    )


def public_image(client: Client, local_filename: Path, object_name: str) -> None:
    """
    Upload a local image as world readable with a random UUID.
    """
    print(f"Uploading {local_filename} as {object_name}")
    extra_args = {
        "ContentType": "image/jpeg",
        "ACL": "public-read",
        "ContentDisposition": "attachment",
        "CacheControl": "must-revalidate",
    }
    client.boto.upload_file(
        Filename=str(local_filename),
        Bucket=client.cfg.s3_bucket,
        ExtraArgs=extra_args,
        Key=object_name,
    )


def get_json(client: Client, object_name: str) -> Any:
    resp = client.boto.get_object(Bucket=client.cfg.s3_bucket, Key=object_name)
    contents = resp["Body"].read()
    return json.loads(contents)


def private_json(client: Client, contents: str, object_name: str) -> None:
    """
    Upload a local JSON file as private under a given name.
    """
    client.boto.put_object(
        Body=contents,
        Bucket=client.cfg.s3_bucket,
        ContentType="application/json",
        Key=object_name,
    )


def get_normalized_extension(filename: Path) -> str:
    suffix_lowered = filename.suffix.lower()

    if suffix_lowered in [".jpeg", ".jpg"]:
        return ".jpg"

    return suffix_lowered


def delete_image(client: Client, filename: str) -> None:
    """
    Delete an image from the photo hosting.
    """
    client.boto.delete_objects(
        Delete={"Objects": [{"Key": filename + ".jpg"}]}, Bucket=client.cfg.s3_bucket
    )
    print("deleted " + filename + ".jpg")
