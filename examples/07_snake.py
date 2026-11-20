"""Play Snake with the eBadge directional buttons."""

import random

import pybadge


GRID_WIDTH = 16
GRID_HEIGHT = 14
CELL_SIZE = 10
ORIGIN_X = 10
ORIGIN_Y = 18
FRAME_MS = 220

DIRECTIONS = (
    (0, -1, pybadge.BUTTON_UP),
    (1, 0, pybadge.BUTTON_RIGHT),
    (0, 1, pybadge.BUTTON_DOWN),
    (-1, 0, pybadge.BUTTON_LEFT),
)


def draw_cell(x, y, color):
    """Draw one grid cell."""
    pybadge.draw_rectangle(
        ORIGIN_X + x * CELL_SIZE,
        ORIGIN_Y + y * CELL_SIZE,
        CELL_SIZE - 1,
        CELL_SIZE - 1,
        color,
        filled=True,
    )


def choose_food(snake):
    """Choose an unoccupied grid cell, or return ``None`` if full."""
    available = []
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if (x, y) not in snake:
                available.append((x, y))
    if not available:
        return None
    return random.choice(available)


def direction_from_buttons(current_direction):
    """Read a direction button while preventing an instant reverse."""
    for index, (_dx, _dy, button) in enumerate(DIRECTIONS):
        if pybadge.is_pressed(button):
            if (index + 2) % 4 != current_direction:
                return index
    return current_direction


def draw_board(snake, food, score):
    """Draw the initial playfield, score, and controls."""
    pybadge.display_clear(pybadge.BLACK)
    pybadge.draw_rectangle(
        ORIGIN_X - 2,
        ORIGIN_Y - 2,
        GRID_WIDTH * CELL_SIZE + 2,
        GRID_HEIGHT * CELL_SIZE + 2,
        pybadge.WHITE,
    )
    draw_score(score)
    pybadge.display_text("D-pad: steer", x=190, y=48)
    pybadge.display_text("A: restart", x=190, y=68)
    for index, (x, y) in enumerate(snake):
        draw_cell(x, y, pybadge.GREEN if index == 0 else (0, 100, 0))
    if food is not None:
        draw_cell(food[0], food[1], pybadge.RED)


def draw_score(score):
    """Update the score without redrawing the playfield."""
    pybadge.display_text("SCORE {}".format(score), x=190, y=20)


def draw_move(previous_head, previous_tail, next_head, eating, food, score):
    """Redraw only cells and status that changed on one game tick."""
    if not eating:
        draw_cell(previous_tail[0], previous_tail[1], pybadge.BLACK)
    draw_cell(previous_head[0], previous_head[1], (0, 100, 0))
    draw_cell(next_head[0], next_head[1], pybadge.GREEN)

    if eating:
        draw_score(score)
        if food is not None:
            draw_cell(food[0], food[1], pybadge.RED)


def wait_for_restart():
    """Wait for button A before starting another round."""
    while not pybadge.is_pressed(pybadge.BUTTON_A):
        pybadge.pause(30)
    while pybadge.is_pressed(pybadge.BUTTON_A):
        pybadge.pause(30)


def play_round():
    """Run a game until the snake hits a wall or itself."""
    snake = [(5, 7), (4, 7), (3, 7)]
    direction = 1
    food = choose_food(snake)
    score = 0
    draw_board(snake, food, score)

    while True:
        direction = direction_from_buttons(direction)
        dx, dy, _button = DIRECTIONS[direction]
        head_x, head_y = snake[0]
        next_head = (head_x + dx, head_y + dy)
        x, y = next_head

        if x < 0 or x >= GRID_WIDTH or y < 0 or y >= GRID_HEIGHT:
            break

        eating = next_head == food
        body = snake if eating else snake[:-1]
        if next_head in body:
            break

        previous_head = snake[0]
        previous_tail = snake[-1]
        snake.insert(0, next_head)
        if eating:
            score += 1
            food = choose_food(snake)
            pybadge.play_tone(660, 50)
        else:
            snake.pop()

        draw_move(previous_head, previous_tail, next_head, eating, food, score)
        if food is None:
            break
        pybadge.pause(FRAME_MS)

    pybadge.display_clear(pybadge.BLACK)
    pybadge.display_text("GAME OVER", x=90, y=80, color=pybadge.RED)
    pybadge.display_text("Score {}".format(score), x=105, y=112)
    pybadge.display_text("Press A to restart", x=65, y=150)
    pybadge.set_rgb_led(pybadge.RED)
    wait_for_restart()


def main():
    """Initialize the board and repeat Snake rounds until interrupted."""
    pybadge.initialize()
    try:
        while True:
            pybadge.turn_rgb_led_off()
            play_round()
    except KeyboardInterrupt:
        pass
    finally:
        pybadge.shutdown()


if __name__ == "__main__":
    main()
