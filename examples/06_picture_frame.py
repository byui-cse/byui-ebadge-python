"""Cycle through BMP photos stored in the badge's ``photos`` directory.

Prepare photos with ``resize_image.py photos/`` and deploy the resulting
``photos_badge/`` directory to the badge before running this program.
"""

import os

import pybadge


PHOTO_DIRECTORY = "photos_badge"
DISPLAY_DURATION_MS = 3000


def list_photos(directory):
    """Return sorted BMP paths found directly inside ``directory``."""
    filenames = os.listdir(directory)
    photos = []
    for filename in filenames:
        if filename.lower().endswith(".bmp"):
            photos.append(directory + "/" + filename)
    photos.sort()
    return photos


def main():
    """Display each photo in a repeating slideshow."""
    pybadge.initialize()
    try:
        photos = list_photos(PHOTO_DIRECTORY)
        if not photos:
            raise ValueError(
                "No BMP photos found in {}".format(PHOTO_DIRECTORY)
            )

        while True:
            for photo in photos:
                pybadge.display_image(photo)
                pybadge.pause(DISPLAY_DURATION_MS)
    except KeyboardInterrupt:
        pass
    finally:
        pybadge.shutdown()


if __name__ == "__main__":
    main()
