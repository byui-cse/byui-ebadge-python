"""Prepare PNG or JPEG artwork for the eBadge's 320 x 240 display.

The image is resized proportionally without enlarging smaller images and saved
as an uncompressed 24-bit BMP for the MicroPython display helper.

Usage::

    python resize_image.py assets/byui-cse.png
    python resize_image.py photo.jpg --output photo_badge.bmp
    python resize_image.py photos/ --output-directory photos_badge/
"""

import argparse
from pathlib import Path


DISPLAY_SIZE = (320, 240)
SUPPORTED_SUFFIXES = (".png", ".jpg", ".jpeg")


def resize_image(source, destination=None):
    """Resize a PNG/JPEG to fit the badge display and save a 24-bit BMP.

    Smaller images are not enlarged. The default output is written beside the
    source as ``<source-name>_badge.bmp``.

    Args:
        source: Input PNG, JPG, or JPEG file path.
        destination: Optional output BMP path.

    Returns:
        The output path as a :class:`pathlib.Path`.

    Raises:
        ImportError: If Pillow is not installed on the host computer.
        ValueError: If the source or destination extension is unsupported.
        OSError: If an image cannot be opened or written.
    """
    source = Path(source)
    if source.suffix.lower() not in SUPPORTED_SUFFIXES:
        raise ValueError("input must be a PNG, JPG, or JPEG image")

    if destination is None:
        destination = source.with_name(source.stem + "_badge.bmp")
    else:
        destination = Path(destination)
    if destination.suffix.lower() != ".bmp":
        raise ValueError("output filename must end in .bmp")

    try:
        from PIL import Image
    except ImportError as error:
        raise ImportError(
            "Image conversion requires Pillow. Install it with "
            "'python -m pip install pillow'."
        ) from error

    resampling = getattr(Image, "Resampling", Image).LANCZOS
    with Image.open(source) as source_image:
        rgba = source_image.convert("RGBA")
        background = Image.new("RGBA", rgba.size, (0, 0, 0, 255))
        image = Image.alpha_composite(background, rgba).convert("RGB")
        image.thumbnail(DISPLAY_SIZE, resampling)
        image.save(destination, format="BMP")

    return destination


def resize_directory(source_directory, destination_directory=None):
    """Convert supported images in a directory tree to display-sized BMPs.

    The directory structure is preserved. By default, output is written to a
    sibling directory named ``<source-name>_badge``. Converted files use the
    same ``<source-name>_badge.bmp`` naming pattern as :func:`resize_image`.

    Args:
        source_directory: Directory containing PNG, JPG, or JPEG files.
        destination_directory: Optional output directory. It must not be the
            source directory.

    Returns:
        A tuple containing the output directory and converted BMP paths.

    Raises:
        ValueError: If the source is not a directory, contains no supported
            images, the output is inside the source, or output names collide.
        ImportError: If Pillow is not installed on the host computer.
    """
    source_directory = Path(source_directory).expanduser().resolve()
    if not source_directory.is_dir():
        raise ValueError("source must be a directory")

    if destination_directory is None:
        destination_directory = source_directory.with_name(
            source_directory.name + "_badge"
        )
    else:
        destination_directory = Path(destination_directory).expanduser().resolve()
    try:
        destination_directory.relative_to(source_directory)
    except ValueError:
        pass
    else:
        raise ValueError("output directory must be outside the source directory")

    sources = sorted(
        path
        for path in source_directory.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
    )
    if not sources:
        raise ValueError("directory contains no PNG, JPG, or JPEG images")

    source_outputs = []
    seen_outputs = set()
    for source in sources:
        relative_path = source.relative_to(source_directory)
        output_path = destination_directory / relative_path.with_name(
            relative_path.stem + "_badge.bmp"
        )
        if output_path in seen_outputs:
            raise ValueError(
                "multiple images map to the same output filename: {}".format(
                    output_path
                )
            )
        seen_outputs.add(output_path)

        source_outputs.append((source, output_path))

    output_paths = []
    for source, output_path in source_outputs:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        resize_image(source, output_path)
        output_paths.append(output_path)

    return destination_directory, tuple(output_paths)


def main():
    """Run the image converter from the command line."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", help="source PNG/JPG/JPEG image or directory")
    parser.add_argument(
        "-o",
        "--output",
        help="output BMP path (default: <source-name>_badge.bmp)",
    )
    parser.add_argument(
        "--output-directory",
        help="output directory when the input is a directory",
    )
    args = parser.parse_args()

    try:
        source = Path(args.image)
        if source.is_dir():
            if args.output:
                parser.error("--output is for a single image; use --output-directory")
            output_directory, output_paths = resize_directory(
                source, args.output_directory
            )
            print("Saved {} BMP images to {}".format(len(output_paths), output_directory))
            return 0

        if args.output_directory:
            parser.error("--output-directory requires a directory input")
        output = resize_image(source, args.output)
    except (ImportError, OSError, ValueError) as error:
        parser.error(str(error))
    print("Saved {}".format(output))
    return 0


if __name__ == "__main__":
    main()
