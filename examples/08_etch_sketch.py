"""Draw on the display with the eBadge directional buttons."""

import pybadge


MIN_X = 3
MAX_X = 316
MIN_Y = 28
MAX_Y = 236
MOVE_PIXELS = 2
FRAME_MS = 25

COLORS = (
    ("white", pybadge.WHITE),
    ("cyan", pybadge.CYAN),
    ("yellow", pybadge.YELLOW),
    ("magenta", pybadge.MAGENTA),
    ("green", pybadge.GREEN),
    ("red", pybadge.RED),
    ("blue", pybadge.BLUE),
    ("orange", pybadge.ORANGE),
)


def draw_status(color_index, eraser):
    """Refresh the instructions in the reserved top strip."""
    pybadge.draw_rectangle(1, 1, 318, 24, pybadge.BLACK, filled=True)
    if eraser:
        label = "ERASER"
        led_color = pybadge.WHITE
    else:
        name, led_color = COLORS[color_index]
        label = "COLOR: {}".format(name.upper())
    pybadge.display_text(label, x=4, y=4, color=pybadge.WHITE)
    pybadge.display_text("A color  B erase  A+B clear", x=118, y=4)
    pybadge.set_rgb_led(led_color)


def clear_canvas():
    """Clear the drawing area and return the cursor to its starting point."""
    pybadge.display_clear(pybadge.BLACK)
    pybadge.draw_rectangle(0, 0, 319, 239, pybadge.WHITE)
    return 160, 132


def main():
    """Run the drawing loop until interrupted."""
    pybadge.initialize()
    cursor_x = 160
    cursor_y = 132
    color_index = 0
    eraser = False
    previous_a = False
    previous_b = False

    try:
        cursor_x, cursor_y = clear_canvas()
        draw_status(color_index, eraser)
        while True:
            a_pressed = pybadge.is_pressed(pybadge.BUTTON_A)
            b_pressed = pybadge.is_pressed(pybadge.BUTTON_B)
            a_just_pressed = a_pressed and not previous_a
            b_just_pressed = b_pressed and not previous_b

            if (a_just_pressed and b_pressed) or (b_just_pressed and a_pressed):
                cursor_x, cursor_y = clear_canvas()
                eraser = False
                draw_status(color_index, eraser)
            elif a_just_pressed:
                color_index = (color_index + 1) % len(COLORS)
                eraser = False
                draw_status(color_index, eraser)
            elif b_just_pressed:
                eraser = not eraser
                draw_status(color_index, eraser)

            previous_a = a_pressed
            previous_b = b_pressed

            next_x = cursor_x
            next_y = cursor_y
            if pybadge.is_pressed(pybadge.BUTTON_LEFT):
                next_x -= MOVE_PIXELS
            if pybadge.is_pressed(pybadge.BUTTON_RIGHT):
                next_x += MOVE_PIXELS
            if pybadge.is_pressed(pybadge.BUTTON_UP):
                next_y -= MOVE_PIXELS
            if pybadge.is_pressed(pybadge.BUTTON_DOWN):
                next_y += MOVE_PIXELS

            next_x = max(MIN_X, min(MAX_X, next_x))
            next_y = max(MIN_Y, min(MAX_Y, next_y))
            if next_x != cursor_x or next_y != cursor_y:
                color = pybadge.BLACK if eraser else COLORS[color_index][1]
                pybadge.draw_line(cursor_x, cursor_y, next_x, next_y, color)
                cursor_x, cursor_y = next_x, next_y

            pybadge.pause(FRAME_MS)
    except KeyboardInterrupt:
        pass
    finally:
        pybadge.shutdown()


if __name__ == "__main__":
    main()
