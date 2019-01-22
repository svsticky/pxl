import tempfile

from pathlib import Path
from typing import Dict

from pxl import state

from PIL import Image  # type: ignore


def compress_image(local_filename: Path) -> Dict[state.Size, Path]:
    """
    Compresses the image to different sizes.
    Returns a Dict of `state.Size`s to `Path`s in a temporary directory.
    """
    sizes_to_generate = [state.Size.thumbnail_w_400, state.Size.display_w_1600]
    image_paths: Dict[state.Size, Path] = {}
    tempdir = Path(tempfile.gettempdir())

    with Image.open(local_filename, "r") as image:
        original_tmp_path = tempdir / local_filename.name
        image = image.convert("RGB")
        image.save(original_tmp_path)
        image_paths[state.Size.original] = original_tmp_path

        # Get the original dimensions
        real_w, real_h = image.size
        for size_to_generate in sizes_to_generate:
            # Prevent upscaling
            w = size_to_generate.max_width
            if w >= real_w:
                image_paths[size_to_generate] = original_tmp_path

            # Copy original image
            scaled = image.copy()
            # Calculate scaling by preserving aspect ratio
            size = w, real_h * (w / real_w)
            # Scale the image
            scaled.thumbnail(size, Image.ANTIALIAS)
            # Save the image with a width specification
            scaled_path = Path(tempfile.gettempdir()).joinpath(
                f"{local_filename.stem}-w{size[0]}.jpeg"
            )
            scaled.save(scaled_path, image.format)

            # Add the path to the output list
            image_paths[size_to_generate] = scaled_path

    return image_paths
