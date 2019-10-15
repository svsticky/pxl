import click
import datetime
import functools
import getpass
import http.server
import json
import socketserver
import subprocess
import sys

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import pxl.config as config
import pxl.generate as generate
import pxl.state as state
import pxl.upload as upload


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
            click.echo("Creating new album.", err=True)
            album = state.Album(
                name_display=album_name,
                name_nav=album_name.lower().replace(" ", "-"),
                created=datetime.datetime.now(),
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
    click.echo("Building site...", err=True)
    output_dir = Path.cwd() / "ignore" / "build"
    design_dir = Path.cwd() / "design"

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
    output_dir = Path.cwd() / "ignore" / "build"
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

    output_dir = Path.cwd() / "ignore" / "build"
    if not output_dir.is_dir():
        click.echo("No output to deploy. Please run `pxl build` first.", err=False)
        sys.exit(1)

    cfg = config.load()

    deploy_command = [
        "rsync",
        "-rzP",
        "--delete",
        f"{output_dir}/",
        f"{cfg.deploy_user}@{cfg.deploy_host}:{cfg.deploy_path}",
    ]
    subprocess.run(deploy_command)


def main() -> None:
    cli()
