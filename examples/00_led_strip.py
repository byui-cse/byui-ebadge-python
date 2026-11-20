"""Open the computer simulator with a few sample outputs.

Run from the repository root with:
    PYTHONPATH=. python3 examples/00_led_strip.py

Click the controls to explore the simulated buttons and joystick. Press q to
close the simulator, then Ctrl-C in the terminal to stop this program.
"""

import byui_ebadge


def main():
    byui_ebadge.initialize(mode="simulator")
    byui_ebadge.display_clear("black")
    byui_ebadge.display_text("Simulator ready", x=8, y=16, color="white")
    byui_ebadge.set_rgb_led("blue")
    led_colors = ["red", "orange", "yellow", "green", "cyan", "blue"] * 4
    byui_ebadge.set_led_strip(led_colors)
    print("Simulator is open. Press q to close its window, then Ctrl-C to exit.")

    try:
        while True:
            byui_ebadge.pause(1000)
            led_colors.append(led_colors.pop(0))
            byui_ebadge.set_led_strip(led_colors)
    except KeyboardInterrupt:
        pass
    finally:
        byui_ebadge.shutdown()


if __name__ == "__main__":
    main()
