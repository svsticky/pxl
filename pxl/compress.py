import tempfile
import pathlib

from typing import Any, Dict

from PIL import Image  # type: ignore

from pxl import state


def compress_image(local_filename: pathlib.Path) -> Dict[state.Size, pathlib.Path]:
    """
    Compresses the image to different sizes.
    Returns a Dict of `state.Size`s to `Path`s in a temporary directory.
    """
    sizes_to_generate = [state.Size.thumbnail_w_400, state.Size.display_w_1600]
    image_paths: Dict[state.Size, pathlib.Path] = {}
    tempdir = pathlib.Path(tempfile.gettempdir())

    with Image.open(local_filename, "r") as image:
        image = orient_exif(image)

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
            scaled_path = pathlib.Path(tempfile.gettempdir()).joinpath(
                f"{local_filename.stem}-w{size[0]}.jpeg"
            )
            scaled.save(scaled_path, image.format)

            # Add the path to the output list
            image_paths[size_to_generate] = scaled_path

    return image_paths


def orient_exif(image: Any) -> Any:
    """
    Rotate the image according to EXIF metadata.
    """
    exif_data = image._getexif()
    if not(exif_data):
        return image

    # EXIF metadata is a binary format. The magic number below stands for
    # the part of the metadata which all compliant software uses as the
    # orientation tag. The parsing logic above only yields a dict from
    # magic numbers to binary data. We need to use this number to get the
    # orientation number, which is another magic number.
    orientation_tag = 274
    orientation = exif_data.get(orientation_tag)

    if orientation is None:
        return image

    # We have some orientation. So we need to flip and mirror the image in
    # some weird ways. See http://sylvana.net/jpegcrop/exif_orientation.html
    if orientation == 1:
        return image
    if orientation == 2:
        return image.transpose(Image.FLIP_LEFT_RIGHT)
    elif orientation == 3:
        return image.rotate(180)
    elif orientation == 4:
        return image.rotate(180).transpose(Image.FLIP_LEFT_RIGHT)
    elif orientation == 5:
        return image.rotate(-90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
    elif orientation == 6:
        return image.rotate(-90, expand=True)
    elif orientation == 7:
        return image.rotate(90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
    elif orientation == 8:
        return image.rotate(90, expand=True)

    # In the unlikely case rotation exif tag is 0 or higher then 9
    return image
