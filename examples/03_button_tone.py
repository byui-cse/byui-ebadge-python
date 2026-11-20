"""Play one short tone each time button A is pressed.

Run from the repository root after `byui_ebadge.py` is implemented.
"""

import byui_ebadge


def main():
    byui_ebadge.initialize()
    byui_ebadge.display_clear()
    byui_ebadge.display_text("Press A to play a note", x=8, y=8)
    was_pressed = False

    try:
        while True:
            is_pressed = byui_ebadge.is_pressed(byui_ebadge.BUTTON_A)
            if is_pressed and not was_pressed:
                byui_ebadge.play_tone(440, 180)
            was_pressed = is_pressed
            byui_ebadge.pause(20)
    except KeyboardInterrupt:
        byui_ebadge.stop_tone()


if __name__ == "__main__":
    main()
