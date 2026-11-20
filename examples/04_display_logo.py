"""Display the LEGO Python image prepared from the repository PNG.

Run `python resize_image.py assets/lego-python.png` from the repository root first.
Deploy the generated BMP along with this program when using hardware mode.
"""

import byui_ebadge


def main():
    byui_ebadge.initialize()
    byui_ebadge.set_rgb_led("yellow")
    byui_ebadge.display_clear()
    byui_ebadge.display_image("lego-python_badge.bmp", x=0, y=0)
    byui_ebadge.set_rgb_led("blue")


if __name__ == "__main__":
    main()
