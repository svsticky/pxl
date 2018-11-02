import click
import getpass
import sys

from pathlib import Path
from typing import Callable, Optional

import pxl.state as state
import pxl.upload as upload

@click.group(name='pxl')
def cli():
    """Photo management script for S3 albums."""


@cli.command(name='init')
@click.option('--force', is_flag=True, default=False)
def init_cmd(force: bool):
    """Initialize pxl configuration"""
    if force:
        state.clean()

    if state.is_initiated():
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

    config = state.Config(s3_endpoint,
                          s3_region,
                          s3_bucket,
                          s3_key_id,
                          s3_key_secret)

    state.initialize(config)


@cli.command(name='clean')
@click.option('--clean-config', is_flag=True, default=False, help='remove config')
def clean_cmd(clean_config: bool):
    """Clean pxl state"""
    confirmation = input('Are you sure? [y/N] ')
    if confirmation.lower() != 'y':
        print('Not confirmed. Exiting.')
        sys.exit(0)

    state.clean(clean_config)


@cli.command(name='upload')
@click.argument('dir_name')
def upload_cmd(dir_name: str) -> None:
    """
    Upload a directory to the photo hosting.
    """
    (pxl_state, pxl_config) = state.get_state_and_config_or_fail()

    dir_path = Path(dir_name)
    if not dir_path.is_dir():
        print(f'{dir_path} is not a directory.')

    album_name = get_input("What name should the album have? ({default}) ",
                           default=dir_path.name.title())

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

        uuid = upload.public_image(pxl_config, entry)
        image = state.Image(remote_uuid=uuid)
        album = album.add_image(image)

    pxl_state = pxl_state.add_album(album)
    state.save_state(pxl_state)


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
