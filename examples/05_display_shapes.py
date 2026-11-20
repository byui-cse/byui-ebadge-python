"""Draw basic shapes using the public display helpers."""

import byui_ebadge


def main():
    """Show pixels, lines, and outlined and filled rectangles."""
    byui_ebadge.initialize()
    try:
        byui_ebadge.display_clear(byui_ebadge.BLACK)
        byui_ebadge.display_text("Display shapes", x=8, y=8)
        byui_ebadge.draw_pixel(20, 40, byui_ebadge.RED)
        byui_ebadge.draw_line(35, 40, 110, 40, byui_ebadge.BLUE)
        byui_ebadge.draw_rectangle(20, 60, 90, 50, byui_ebadge.GREEN)
        byui_ebadge.draw_rectangle(130, 60, 90, 50, byui_ebadge.YELLOW, filled=True)
        print("Drawing is complete. Press Ctrl-C to stop.")
        while True:
            byui_ebadge.pause(1000)
    except KeyboardInterrupt:
        pass
    finally:
        byui_ebadge.shutdown()


if __name__ == "__main__":
    main()
