import jinja2

from pathlib import Path

import pxl.state as state


def build(overview: state.Overview, output_dir: Path, template_dir: Path):
    """Build a static site based on the state."""

    index_template = load_template(template_dir / 'index.html.j2')
    album_template = load_template(template_dir / 'album.html.j2')
    photo_template = load_template(template_dir / 'photo.html.j2')

    clear_directory(output_dir)
    output_dir.mkdir()

    with (output_dir / 'index.html').open('w+') as f:
        index_template.stream(overview=overview).dump(f)


def load_template(template_file: Path) -> jinja2.Template:
    """Load a jinja template from a file.

    There isn't a method in the standard API that does this, so
    we roll it ourselves."""

    with template_file.open() as f:
        return jinja2.Template(f.read())


def clear_directory(dir_path: Path):
    if not dir_path.exists():
        return

    assert dir_path.is_dir()

    for entry in dir_path.iterdir():
        if entry.is_dir():
            clear_directory(entry)
        else:
            entry.unlink()

    dir_path.rmdir()
