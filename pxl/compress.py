from pathlib import Path
from PIL import Image
import tempfile

WIDTHS = [1600, 800]

def compress_image(local_filename: Path) -> [Path]:
    """Compresses the image to different sizes and saves them to /tmp, returns a list of paths"""

    image_paths = []
    with Image.open(local_filename, "r") as image:
        # Copy the original image to temp
        path = Path(tempfile.gettempdir()).joinpath(local_filename.name)
        image = image.convert("RGB")
        image.save(path)
        image_paths.append(path)

        # Get the original dimensions
        real_w, real_h = image.size
        for w in WIDTHS:
            # Prevent upscaling
            if w >= real_w:
                continue

            # Copy original image
            scaled = image.copy()
            # Calculate scaling by preserving aspect ratio
            size = w, real_h * (w / real_w)
            # Scale the image
            scaled.thumbnail(size, Image.ANTIALIAS)
            # Save the image with a width specification
            scaled_path = Path(tempfile.gettempdir()).joinpath(f"{local_filename.stem}-w{size[0]}.jpeg")
            scaled.save(scaled_path, image.format)

            # Add the path to the output list
            image_paths.append(scaled_path)

    return image_paths

