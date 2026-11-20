"""Cycle sample RGB and addressable LED colors on a computer or eBadge.

Run on a computer from the repository root with:
    python simulator.py 00_led_strip

Deploy to a badge from the repository root with:
    python deploy.py --install-library examples/00_led_strip.py

The program automatically selects the simulator on a computer and the
hardware backend on a MicroPython badge. Press Ctrl-C to stop it.
"""

import byui_ebadge


def main():
    byui_ebadge.initialize()
    byui_ebadge.display_clear("black")
    byui_ebadge.display_text("LED demo running", x=8, y=16, color="white")
    byui_ebadge.set_rgb_led("blue")
    led_colors = ["red", "orange", "yellow", "green", "cyan", "blue"] * 4
    byui_ebadge.set_led_strip(led_colors)
    print("LED demo is running. Press Ctrl-C to exit.")

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
