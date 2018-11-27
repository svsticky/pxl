import jinja2
import shutil

from pathlib import Path

import pxl.state as state


def build(overview: state.Overview,
          output_dir: Path,
          template_dir: Path,
          bucket_puburl: str):
    """Build a static site based on the state."""

    index_template = load_template(template_dir / 'index.html.j2')
    album_template = load_template(template_dir / 'album.html.j2')
    photo_template = load_template(template_dir / 'photo.html.j2')

    shutil.rmtree(output_dir)
    output_dir.mkdir()

    shutil.copytree(template_dir / 'css', output_dir / 'css')
    shutil.copytree(template_dir / 'js', output_dir / 'js')

    with (output_dir / 'index.html').open('w+') as f:
        index_template.stream(overview=overview,
                              img_baseurl=bucket_puburl).dump(f)

    for album in overview.albums:
        album_dir = output_dir / album.name_nav
        album_dir.mkdir()

        with (album_dir / 'index.html').open('w+') as f:
            album_template.stream(album=album,
                                  img_baseurl=bucket_puburl).dump(f)

        for image in album.images:
            image_dir = album_dir / str(image.remote_uuid)
            image_dir.mkdir()

            with (image_dir / 'index.html').open('w+') as f:
                photo_template.stream(image=image).dump(f)


def load_template(template_file: Path) -> jinja2.Template:
    """Load a jinja template from a file.

    There isn't a method in the standard API that does this, so
    we roll it ourselves."""

    with template_file.open() as f:
        return jinja2.Template(f.read())
