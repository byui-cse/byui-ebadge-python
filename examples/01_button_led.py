"""Light the RGB LED while button A is held.

Run from the repository root after `byui_ebadge.py` is implemented.
"""

import byui_ebadge


def main():
    byui_ebadge.initialize()
    print("Hold button A to light the LED. Press Ctrl-C to stop.")

    try:
        while True:
            if byui_ebadge.is_pressed(byui_ebadge.BUTTON_A):
                byui_ebadge.set_rgb_led("blue")
            else:
                byui_ebadge.turn_rgb_led_off()
            byui_ebadge.pause(20)
    except KeyboardInterrupt:
        byui_ebadge.turn_rgb_led_off()


if __name__ == "__main__":
    main()
