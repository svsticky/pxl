from __main__ import __file__ as entrypoint_file  # type: ignore
import click
import datetime
from dateutil import parser
import functools
import getpass
import http.server
import json
import socketserver
import subprocess
import sys
import copy

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Any

import pxl.config as config
import pxl.generate as generate
import pxl.state as state
import pxl.upload as upload

entrypoint = Path(entrypoint_file).parent.absolute()
if entrypoint.match("/usr/*"):
    build_path = Path.home() / ".local" / "share" / "pxl" / "build"
else:
    build_path = Path("ignore/build")


def validate(value: str) -> Optional[Any]:
    try:
        date: datetime.datetime = parser.parse(value)
    except:
        raise click.BadParameter("Wrong date input.", param=value)  # type: ignore
    return date


@click.group(name="pxl")
def cli() -> None:
    """Photo management script for S3 albums."""


@cli.command(name="init")
@click.option("--force", is_flag=True, default=False)
def init_cmd(force: bool) -> None:
    """Initialize pxl configuration"""
    if config.is_initialized() and not force:
        click.echo("pxl is already initiated. Add `--force` to override.", err=True)
        sys.exit(1)

    click.echo("We need some information. Please answer the prompts.", err=True)
    click.echo("Defaults are between [brackets].\n", err=True)

    s3_endpoint = click.prompt("S3 endpoint", default="digitaloceanspaces.com")
    s3_region = click.prompt("S3 region", default="ams3")
    s3_bucket = click.prompt("S3 bucket")
    s3_key_id = click.prompt("S3 key ID")
    s3_key_secret = click.prompt("S3 key secret (not shown)", hide_input=True)

    deploy_host = click.prompt("Deploy host")
    deploy_user = click.prompt("Deploy user")
    deploy_path = click.prompt("Deploy path")

    public_image_url = click.prompt("Public image base URL (optional)", default="")

    cfg = config.Config(
        s3_endpoint,
        s3_region,
        s3_bucket,
        s3_key_id,
        s3_key_secret,
        deploy_host,
        deploy_user,
        deploy_path,
        public_image_url,
    )

    config.save(cfg)


@cli.command(name="clean")
def clean_cmd() -> None:
    """Clean pxl files from system"""
    click.echo("This operation will remove your `pxl` configuration.", err=True)
    click.echo("Any deployed files or uploaded images are unaffected.\n", err=True)

    click.confirm("Do you want to continue?", abort=True)
    config.clean()


@cli.command(name="edit")
@click.argument("album_name")
@click.option("--force", is_flag=True, type=bool, help="Force break lock")
def edit_cmd(album_name: str, force: bool) -> None:
    """
    Edit the name and date of an album
    """
    cfg = config.load()
    with upload.client(cfg, break_lock=force) as client:
        try:
            pxl_state_json = upload.get_json(client, "state.json")
            pxl_state = state.Overview.from_json(pxl_state_json)
            assert pxl_state is not None, "Expected state to be valid"
        except client.boto.exceptions.NoSuchKey as e:
            pxl_state = state.Overview.empty()
        except Exception as e:
            print(e)
            sys.exit(1)

        print(pxl_state)
        old_album = pxl_state.get_album_by_name(album_name)
        if not (old_album):
            click.echo(f"{album_name} does not exist", err=True)
            sys.exit(1)
        else:
            new_album = copy.deepcopy(old_album)
            album_name = click.prompt(
                "What should the new album name be?", default=old_album.name_display
            )
            album_date = click.prompt(  # type: ignore
                "What should the new album date be?",
                default=str(old_album.created),
                value_proc=validate,
            )

            alt_album = pxl_state.get_album_by_name(album_name)
            if alt_album and not (album_name == old_album.name_display):
                click.confirm(
                    "An album with that name already exists. Merge albums?", abort=True
                )
                alt_album.created = album_date
                alt_album.images = alt_album.images + old_album.images
                pxl_state = pxl_state.remove_album(old_album)
                pxl_state = pxl_state.edit_album(alt_album, alt_album)
                upload.private_json(
                    client, json.dumps(pxl_state.to_json()), "state.json"
                )
            else:
                new_album.name_display = album_name
                new_album.name_nav = album_name.lower().replace(" ", "-")
                new_album.created = album_date

                pxl_state = pxl_state.edit_album(old_album, new_album)
                upload.private_json(
                    client, json.dumps(pxl_state.to_json()), "state.json"
                )


@cli.command(name="upload")
@click.argument("dir_name")
@click.option("--force", is_flag=True, type=bool, help="Force break lock")
def upload_cmd(dir_name: str, force: bool) -> None:
    """
    Upload a directory to the photo hosting.
    """
    cfg = config.load()

    dir_path = Path(dir_name)
    if not dir_path.is_dir():
        click.echo(f"{dir_path} is not a directory.", err=True)
        sys.exit(1)

    if not list(dir_path.glob("*.jpg")):
        click.echo(f"{dir_path} does not contain any .jpg files.", err=True)
        sys.exit(1)

    with upload.client(cfg, break_lock=force) as client:
        album_name = click.prompt(
            "What name should the album have?", default=dir_path.name.title()
        )

        try:
            pxl_state_json = upload.get_json(client, "state.json")
            pxl_state = state.Overview.from_json(pxl_state_json)
            assert pxl_state is not None, "Expected state to be valid"
        except client.boto.exceptions.NoSuchKey as e:
            pxl_state = state.Overview.empty()
        except Exception as e:
            print(e)
            sys.exit(1)

        print(pxl_state)

        # Get existing album with this name for appending.
        album = pxl_state.get_album_by_name(album_name)
        if album:
            click.confirm("Album already exists. Add to existing album?", abort=True)
        else:
            date = click.prompt(  # type: ignore
                "What date was the album created?",
                default=datetime.datetime.now(),
                value_proc=validate,
            )

            click.echo("Creating new album.", err=True)
            album = state.Album(
                name_display=album_name,
                name_nav=album_name.lower().replace(" ", "-"),
                created=date,
                images=[],
            )

        # Find all files with known JPEG extensions. We don't
        # traverse nested directories, just the toplevel.
        for entry in dir_path.iterdir():
            if not entry.is_file():
                continue

            if not entry.suffix.lower() in [".jpeg", ".jpg"]:
                continue

            image = upload.public_image_with_size(client, entry)
            album = album.add_image(image)

        pxl_state = pxl_state.add_or_replace_album(album)
        upload.private_json(client, json.dumps(pxl_state.to_json()), "state.json")


@cli.command("build")
@click.option("--force", is_flag=True, type=bool, help="Force break lock")
def build_cmd(force: bool) -> None:
    """Build a static site based on current state."""
    output_dir = build_path
    output_dir.mkdir(parents=True, exist_ok=True)

    click.echo(f"Building site to {output_dir}...", err=True)
    design_dir = Path(entrypoint) / "design"

    cfg = config.load()
    with upload.client(cfg, break_lock=force) as client:
        try:
            pxl_state_json = upload.get_json(client, "state.json")
            overview = state.Overview.from_json(pxl_state_json)
            assert overview is not None, "Expected state to be valid"
        except client.boto.exceptions.NoSuchKey as e:
            click.echo(
                "Remote state not found. Please upload before continuing.", err=True
            )
            sys.exit(1)
        except Exception as e:
            click.echo(e, err=True)
            sys.exit(1)

        bucket_puburl = f"https://{cfg.s3_bucket}.{cfg.s3_region}.{cfg.s3_endpoint}"

        generate.build(
            overview=overview,
            output_dir=output_dir,
            template_dir=design_dir,
            bucket_puburl=bucket_puburl,
            public_image_url=cfg.public_image_url,
        )
    click.echo("Done.", err=True)


@cli.command("preview")
@click.option("--port", default=8000, type=int, help="Port to use")
@click.option("--bind", default="", help="Address to bind on (default: all interfaces)")
def preview_cmd(port: int, bind: str) -> None:
    """Run a local webserver on build output"""
    output_dir = build_path
    if not output_dir.is_dir():
        click.echo("No output to serve. Please run `pxl build` first.", err=True)
        sys.exit(1)

    click.launch(f"http://localhost:{port}")

    # Start the default Python HTTP server.
    #
    # We want to specify that the `build` directory is used for serving
    # the responses. The TCPServer class expects a `handler_class` to
    # initialize, so we can't construct in a `SimpleHTTPRequestHandler`
    # instance and pass it the `directory` argument directly. Instead
    # we need to partially apply the constructor with the `directory`
    # keyword argument and pass that as the handler_class.
    #
    # This feels more complicated than it should be.
    server_address = (bind, port)
    handler_class = functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=str(output_dir)
    )
    with socketserver.TCPServer(server_address, handler_class) as httpd:  # type: ignore
        click.echo(f"Serving {output_dir} at port {port}", err=True)
        httpd.serve_forever()


@cli.command("deploy")
def deploy_cmd() -> None:
    """Deploy the static output."""
    if not config.is_initialized():
        click.echo("Config not initialized. Please run `pxl init` first.", err=False)
        sys.exit(1)

    output_dir = build_path
    if not output_dir.is_dir():
        click.echo("No output to deploy. Please run `pxl build` first.", err=False)
        sys.exit(1)

    cfg = config.load()

    dry_run_result = subprocess.run(
        build_deploy_rsync(output_dir, cfg, dry_run=True),
        capture_output=True,
        text=True,
    )

    # Inspect dry run output to check whether there are any files to delete
    if len(dry_run_result.stdout) > 0:
        stdout_lines = dry_run_result.stdout.split("\n")
        click.echo(
            click.style(
                "Warning! Rsync reports that it will delete these files:", fg="yellow"
            )
        )

        for line in stdout_lines[:-1]:
            parts = line.split(" ", 1)

            click.echo(click.style(parts[1], fg="yellow"))

        if not click.confirm("Continue?"):
            click.echo("Aborting.")
            return

    dry_run_result = subprocess.run(build_deploy_rsync(output_dir, cfg, dry_run=False))


def build_deploy_rsync(
    output_dir: Path, cfg: config.Config, dry_run: bool = False
) -> List[str]:
    """
    Helper to build the rsync command for deploying.

    If we're doing a dry run, the command will output all files to be deleted
    on stdout.  If we're not doing a dry run, the command will output all
    altered files and progress on stderr.
    """

    result = [
        "rsync",
        "--recursive",
        "--compress",
        "--partial",
        "--delete",
        f"{output_dir}/",
        f"{cfg.deploy_user}@{cfg.deploy_host}:{cfg.deploy_path}",
    ]

    if dry_run:
        result.insert(1, "--dry-run")
        result.insert(1, "--info=DEL")

    else:
        result.insert(1, "--progress")

    return result


@cli.command("delete")
@click.argument("album_name")
@click.option("--force", is_flag=True, type=bool, help="Force break lock")
def delete_cmd(album_name: str, force: bool) -> None:
    """
    Delete an album and its pictures.
    """
    cfg = config.load()

    with upload.client(cfg, break_lock=force) as client:

        try:
            pxl_state_json = upload.get_json(client, "state.json")
            pxl_state = state.Overview.from_json(pxl_state_json)
            assert pxl_state is not None, "Expected state to be valid"
        except client.boto.exceptions.NoSuchKey as e:
            pxl_state = state.Overview.empty()
        except Exception as e:
            print(e)
            sys.exit(1)

        print(pxl_state)

        # Get existing album with this name to check if it exists
        album = pxl_state.get_album_by_name(album_name)
        if album:
            click.echo("Album found, deleting pictures...")
            for image in album.images:
                upload.delete_image(client, image.get_name("original"))
                upload.delete_image(client, image.get_name("display_w_1600"))
                upload.delete_image(client, image.get_name("thumbnail_w_400"))

        else:
            click.echo("Given album not found")
            sys.exit(1)

        click.echo("deleting album...")

        pxl_state = pxl_state.remove_album(album)
        upload.private_json(client, json.dumps(pxl_state.to_json()), "state.json")

        click.echo("deleted album, please run build and deploy now")


def main() -> None:
    cli()
