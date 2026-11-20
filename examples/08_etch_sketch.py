"""Draw on the display with the eBadge directional buttons."""

import byui_ebadge


MIN_X = 3
MAX_X = 316
MIN_Y = 28
MAX_Y = 236
MOVE_PIXELS = 2
FRAME_MS = 25

COLORS = (
    ("white", byui_ebadge.WHITE),
    ("cyan", byui_ebadge.CYAN),
    ("yellow", byui_ebadge.YELLOW),
    ("magenta", byui_ebadge.MAGENTA),
    ("green", byui_ebadge.GREEN),
    ("red", byui_ebadge.RED),
    ("blue", byui_ebadge.BLUE),
    ("orange", byui_ebadge.ORANGE),
)


def draw_status(color_index, eraser):
    """Refresh the instructions in the reserved top strip."""
    byui_ebadge.draw_rectangle(1, 1, 318, 24, byui_ebadge.BLACK, filled=True)
    if eraser:
        label = "ERASER"
        led_color = byui_ebadge.WHITE
    else:
        name, led_color = COLORS[color_index]
        label = "COLOR: {}".format(name.upper())
    byui_ebadge.display_text(label, x=4, y=4, color=byui_ebadge.WHITE)
    byui_ebadge.display_text("A color  B erase  A+B clear", x=118, y=4)
    byui_ebadge.set_rgb_led(led_color)


def clear_canvas():
    """Clear the drawing area and return the cursor to its starting point."""
    byui_ebadge.display_clear(byui_ebadge.BLACK)
    byui_ebadge.draw_rectangle(0, 0, 319, 239, byui_ebadge.WHITE)
    return 160, 132


def main():
    """Run the drawing loop until interrupted."""
    byui_ebadge.initialize()
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
            a_pressed = byui_ebadge.is_pressed(byui_ebadge.BUTTON_A)
            b_pressed = byui_ebadge.is_pressed(byui_ebadge.BUTTON_B)
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
            if byui_ebadge.is_pressed(byui_ebadge.BUTTON_LEFT):
                next_x -= MOVE_PIXELS
            if byui_ebadge.is_pressed(byui_ebadge.BUTTON_RIGHT):
                next_x += MOVE_PIXELS
            if byui_ebadge.is_pressed(byui_ebadge.BUTTON_UP):
                next_y -= MOVE_PIXELS
            if byui_ebadge.is_pressed(byui_ebadge.BUTTON_DOWN):
                next_y += MOVE_PIXELS

            next_x = max(MIN_X, min(MAX_X, next_x))
            next_y = max(MIN_Y, min(MAX_Y, next_y))
            if next_x != cursor_x or next_y != cursor_y:
                color = byui_ebadge.BLACK if eraser else COLORS[color_index][1]
                byui_ebadge.draw_line(cursor_x, cursor_y, next_x, next_y, color)
                cursor_x, cursor_y = next_x, next_y

            byui_ebadge.pause(FRAME_MS)
    except KeyboardInterrupt:
        pass
    finally:
        byui_ebadge.shutdown()


if __name__ == "__main__":
    main()
