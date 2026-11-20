"""Display the BYU-Idaho CSE logo prepared from the repository PNG.

Run `python resize_image.py byui-cse.png` from the repository root first. Copy
the generated BMP to the badge when using hardware mode.
"""

import byui_ebadge


def main():
    byui_ebadge.initialize()
    byui_ebadge.display_clear()
    byui_ebadge.display_image("byui-cse_badge.bmp", x=0, y=0)


if __name__ == "__main__":
    main()
