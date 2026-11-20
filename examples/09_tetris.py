"""Play a simple D-pad controlled Tetris game on the eBadge."""

import random

import byui_ebadge


GRID_WIDTH = 10
GRID_HEIGHT = 18
CELL_SIZE = 11
GRID_X = 50
GRID_Y = 15
FRAME_MS = 20
GRAVITY_FRAMES = 25
MOVE_REPEAT_FRAMES = 6

COLORS = (
    byui_ebadge.CYAN,
    byui_ebadge.YELLOW,
    byui_ebadge.MAGENTA,
    byui_ebadge.GREEN,
    byui_ebadge.RED,
    byui_ebadge.BLUE,
    byui_ebadge.ORANGE,
)

# Each shape uses four rows of four cells. Rotations are calculated as needed.
SHAPES = (
    ((0, 1, 0, 0), (0, 1, 0, 0), (0, 1, 0, 0), (0, 1, 0, 0)),
    ((0, 1, 1, 0), (0, 1, 1, 0), (0, 0, 0, 0), (0, 0, 0, 0)),
    ((0, 1, 0, 0), (1, 1, 1, 0), (0, 0, 0, 0), (0, 0, 0, 0)),
    ((0, 1, 1, 0), (1, 1, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0)),
    ((1, 1, 0, 0), (0, 1, 1, 0), (0, 0, 0, 0), (0, 0, 0, 0)),
    ((1, 0, 0, 0), (1, 1, 1, 0), (0, 0, 0, 0), (0, 0, 0, 0)),
    ((0, 0, 1, 0), (1, 1, 1, 0), (0, 0, 0, 0), (0, 0, 0, 0)),
)


def rotate_shape(shape):
    """Return ``shape`` rotated 90 degrees clockwise."""
    uses_four_cell_box = any(shape[3]) or any(row[3] for row in shape)
    box_size = 4 if uses_four_cell_box else 3
    rotated = [[0] * 4 for _ in range(4)]
    for y in range(box_size):
        for x in range(box_size):
            rotated[x][box_size - 1 - y] = shape[y][x]
    return tuple(tuple(row) for row in rotated)


def get_shape(piece):
    """Return the piece matrix after its requested number of rotations."""
    shape = SHAPES[piece["kind"]]
    if piece["kind"] == 1:
        return shape
    for _ in range(piece["rotation"]):
        shape = rotate_shape(shape)
    return shape


def collides(grid, piece, offset_x=0, offset_y=0, rotation=None):
    """Return whether the piece would overlap a wall, floor, or locked block."""
    candidate = dict(piece)
    candidate["x"] += offset_x
    candidate["y"] += offset_y
    if rotation is not None:
        candidate["rotation"] = rotation
    shape = get_shape(candidate)

    for shape_y in range(4):
        for shape_x in range(4):
            if not shape[shape_y][shape_x]:
                continue
            x = candidate["x"] + shape_x
            y = candidate["y"] + shape_y
            if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
                return True
            if y >= 0 and grid[y][x]:
                return True
    return False


def draw_block(x, y, color):
    """Draw one Tetris block with a small black gap around it."""
    byui_ebadge.draw_rectangle(
        GRID_X + x * CELL_SIZE,
        GRID_Y + y * CELL_SIZE,
        CELL_SIZE - 1,
        CELL_SIZE - 1,
        color,
        filled=True,
    )


def draw_game(grid, piece, score, paused=False):
    """Draw the settled grid, active piece, and game information."""
    byui_ebadge.display_clear(byui_ebadge.BLACK)
    byui_ebadge.draw_rectangle(
        GRID_X - 2,
        GRID_Y - 2,
        GRID_WIDTH * CELL_SIZE + 3,
        GRID_HEIGHT * CELL_SIZE + 3,
        byui_ebadge.WHITE,
    )
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            color_index = grid[y][x]
            if color_index:
                draw_block(x, y, COLORS[color_index - 1])

    if piece is not None:
        shape = get_shape(piece)
        for shape_y in range(4):
            for shape_x in range(4):
                x = piece["x"] + shape_x
                y = piece["y"] + shape_y
                if shape[shape_y][shape_x] and 0 <= y < GRID_HEIGHT:
                    draw_block(x, y, COLORS[piece["kind"]])

    byui_ebadge.display_text("TETRIS", x=180, y=20, color=byui_ebadge.CYAN)
    byui_ebadge.display_text("Score {}".format(score), x=180, y=48)
    byui_ebadge.display_text("Left/Right: move", x=180, y=82)
    byui_ebadge.display_text("Up: rotate", x=180, y=102)
    byui_ebadge.display_text("Down: drop", x=180, y=122)
    byui_ebadge.display_text("A: pause", x=180, y=142)
    byui_ebadge.display_text("B: new game", x=180, y=162)
    if paused:
        byui_ebadge.draw_rectangle(77, 96, 166, 42, byui_ebadge.BLACK, filled=True)
        byui_ebadge.draw_rectangle(76, 95, 168, 44, byui_ebadge.WHITE)
        byui_ebadge.display_text("PAUSED", x=126, y=110, color=byui_ebadge.YELLOW)


def new_piece():
    """Create a random piece near the top of the playfield."""
    return {"kind": random.randrange(len(SHAPES)), "rotation": 0, "x": 3, "y": 0}


def clear_completed_rows(grid):
    """Remove full rows and return the updated grid and number removed."""
    remaining = [row for row in grid if not all(row)]
    removed = GRID_HEIGHT - len(remaining)
    while len(remaining) < GRID_HEIGHT:
        remaining.insert(0, [0] * GRID_WIDTH)
    return remaining, removed


def lock_piece(grid, piece):
    """Write the active piece into the settled grid."""
    shape = get_shape(piece)
    for shape_y in range(4):
        for shape_x in range(4):
            x = piece["x"] + shape_x
            y = piece["y"] + shape_y
            if shape[shape_y][shape_x] and 0 <= y < GRID_HEIGHT:
                grid[y][x] = piece["kind"] + 1


def play_game():
    """Run one game; return when the stack reaches the top or B is pressed."""
    grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
    piece = new_piece()
    score = 0
    paused = False
    frame = 0
    move_cooldown = 0
    previous_a = False
    previous_b = False
    previous_up = False
    draw_game(grid, piece, score)

    while not collides(grid, piece):
        a_pressed = byui_ebadge.is_pressed(byui_ebadge.BUTTON_A)
        b_pressed = byui_ebadge.is_pressed(byui_ebadge.BUTTON_B)
        up_pressed = byui_ebadge.is_pressed(byui_ebadge.BUTTON_UP)

        if b_pressed and not previous_b:
            return
        if a_pressed and not previous_a:
            paused = not paused
        previous_a = a_pressed
        previous_b = b_pressed

        changed = False
        if not paused:
            if move_cooldown > 0:
                move_cooldown -= 1
            if move_cooldown == 0:
                if byui_ebadge.is_pressed(byui_ebadge.BUTTON_LEFT) and not collides(
                    grid, piece, offset_x=-1
                ):
                    piece["x"] -= 1
                    changed = True
                    move_cooldown = MOVE_REPEAT_FRAMES
                elif byui_ebadge.is_pressed(byui_ebadge.BUTTON_RIGHT) and not collides(
                    grid, piece, offset_x=1
                ):
                    piece["x"] += 1
                    changed = True
                    move_cooldown = MOVE_REPEAT_FRAMES

            if up_pressed and not previous_up:
                rotation = (piece["rotation"] + 1) % 4
                if not collides(grid, piece, rotation=rotation):
                    piece["rotation"] = rotation
                    changed = True

            gravity = 3 if byui_ebadge.is_pressed(byui_ebadge.BUTTON_DOWN) else GRAVITY_FRAMES
            if frame % gravity == 0:
                if not collides(grid, piece, offset_y=1):
                    piece["y"] += 1
                else:
                    lock_piece(grid, piece)
                    grid, cleared = clear_completed_rows(grid)
                    score += cleared * 100
                    piece = new_piece()
                    if collides(grid, piece):
                        break
                changed = True
        previous_up = up_pressed
        if changed:
            draw_game(grid, piece, score, paused)
        elif paused and frame % 10 == 0:
            draw_game(grid, piece, score, paused)
        frame += 1
        byui_ebadge.pause(FRAME_MS)

    draw_game(grid, None, score)
    byui_ebadge.display_text("GAME OVER", x=180, y=196, color=byui_ebadge.RED)
    byui_ebadge.display_text("B: new game", x=180, y=216)
    while not byui_ebadge.is_pressed(byui_ebadge.BUTTON_B):
        byui_ebadge.pause(30)
    while byui_ebadge.is_pressed(byui_ebadge.BUTTON_B):
        byui_ebadge.pause(30)


def main():
    """Initialize the board and repeat Tetris games until interrupted."""
    byui_ebadge.initialize()
    try:
        while True:
            play_game()
    except KeyboardInterrupt:
        pass
    finally:
        byui_ebadge.shutdown()


if __name__ == "__main__":
    main()
