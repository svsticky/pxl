import click
import getpass
import json
import sys

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import pxl.config as config
import pxl.state as state
import pxl.upload as upload

@click.group(name='pxl')
def cli():
    """Photo management script for S3 albums."""


@cli.command(name='init')
@click.option('--force', is_flag=True, default=False)
def init_cmd(force: bool):
    """Initialize pxl configuration"""
    if config.is_initialized():
        print('pxl is already initiated. Add `--force` to override.')
        sys.exit(1)

    print('We need some information. Please answer the prompts.')
    print('Defaults are between parentheses.')
    print()

    s3_endpoint = get_input('S3 endpoint ({default}): ', default='digitaloceanspaces.com')
    s3_region = get_input('S3 region ({default}): ', default='ams3')
    s3_bucket = get_input('S3 bucket: ')
    s3_key_id = get_input('S3 key ID: ')
    s3_key_secret = get_input('S3 key secret (not echoed): ', hide_input=True)

    config = config.Config(s3_endpoint,
                           s3_region,
                           s3_bucket,
                           s3_key_id,
                           s3_key_secret)


@cli.command(name='clean')
@click.option('--clean-config', is_flag=True, default=False, help='remove config')
def clean_cmd(clean_config: bool):
    """Clean pxl state"""
    confirmation = input('Are you sure? [y/N] ')
    if confirmation.lower() != 'y':
        print('Not confirmed. Exiting.')
        sys.exit(0)

    config.clean()


@cli.command(name='upload')
@click.argument('dir_name')
@click.option('--force', is_flag=True, type=bool, help='Force break lock')
def upload_cmd(dir_name: str, force: bool) -> None:
    """
    Upload a directory to the photo hosting.
    """
    cfg = config.load()

    dir_path = Path(dir_name)
    if not dir_path.is_dir():
        print(f'{dir_path} is not a directory.')

    with upload.client(cfg, break_lock=force) as client:
        album_name = get_input("What name should the album have? ({default}) ",
                               default=dir_path.name.title())

        try:
            pxl_state_json = upload.get_json(client, 'state.json')
            pxl_state = state.Overview.from_json(pxl_state_json)
        except Exception as e:
            print(e)
            sys.exit(1)

        # Get existing album with this name for appending.
        album = pxl_state.get_album_by_name(album_name)
        if album:
            append_confirm = get_input('Appending to existing album ok? [Y/n] ',
                                       default='y',
                                       validate=lambda x: x.lower() in ['y', 'n'])
            if append_confirm == 'n':
                print('Not appending. Choose a different album name.')
                sys.exit(1)
        else:
            print('Creating new album.')
            album = state.Album(name_display=album_name,
                                name_nav=album_name.lower().replace(' ', '-'),
                                images=[])

        # Find all files with known JPEG extensions. We don't
        # traverse nested directories, just the toplevel.
        for entry in dir_path.iterdir():
            if not entry.is_file():
                continue

            if not entry.suffix.lower() in ['.jpeg', '.jpg']:
                continue

            uuid = upload.public_image(client, entry)
            image = state.Image(remote_uuid=uuid)
            album = album.add_image(image)

        pxl_state = pxl_state.add_or_replace_album(album)
        upload.private_json(client, json.dumps(pxl_state.to_json()), 'state.json')


def get_input(
        prompt: str,
        default: Optional[str]=None,
        hide_input: bool=False,
        validate: Callable[[str], bool] = lambda x: True,
    ) -> str:
    """
    Utility for common user input scenario's.

    Supports defaults, hiding the input by the user (useful for sensitive
    information). Accepts a validate callback and reprompts the user if
    this callback fails.
    """
    # Slightly magic behavior: if the default is set, we call the
    # format method with the default on the string. This means the
    # user is shown the default.
    if default:
        prompt = prompt.format(default=default)

    while True:
        user_input = (getpass.getpass(prompt) if hide_input else input(prompt)).strip()
        if user_input == '' and default:
            return default
        if validate(user_input):
            return user_input


def main():
    cli()
