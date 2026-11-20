"""Choose and run a Python program copied to the eBadge's root directory.

Deploy this file as ``main.py`` and copy the programs to the badge with
``deploy.py --asset``. Use Up/Down to choose a program and A to run it.
"""

import os

import byui_ebadge


VISIBLE_PROGRAMS = 10
SKIP_FILES = (
    "boot.py",
    "main.py",
    "program_selector.py",
    "byui_ebadge.py",
)


def list_programs(directory="."):
    """Return sorted Python program filenames in ``directory``."""
    programs = []
    for filename in os.listdir(directory):
        if filename.endswith(".py") and filename not in SKIP_FILES:
            programs.append(filename)
    programs.sort()
    return programs


def visible_start(selected, program_count):
    """Return the first filename index in the current menu window."""
    if program_count <= VISIBLE_PROGRAMS:
        return 0
    start = selected - VISIBLE_PROGRAMS + 1
    return max(0, min(start, program_count - VISIBLE_PROGRAMS))


def draw_menu(programs, selected):
    """Draw the current program selection menu."""
    byui_ebadge.display_clear(byui_ebadge.BLACK)
    byui_ebadge.display_text("Choose a program", x=8, y=8, color=byui_ebadge.CYAN)
    byui_ebadge.display_text("Up/Down select; A run", x=8, y=26)
    if not programs:
        byui_ebadge.display_text("No programs found", x=8, y=58, color=byui_ebadge.YELLOW)
        byui_ebadge.display_text("Copy .py files to badge", x=8, y=78)
        return

    start = visible_start(selected, len(programs))
    end = min(start + VISIBLE_PROGRAMS, len(programs))
    for index in range(start, end):
        prefix = "> " if index == selected else "  "
        byui_ebadge.display_text(
            prefix + programs[index],
            x=8,
            y=50 + (index - start) * 18,
            color=byui_ebadge.GREEN if index == selected else byui_ebadge.WHITE,
        )


def run_program(filename):
    """Execute a selected program and return to the selector when it ends."""
    path = filename if filename.startswith("/") else "/" + filename
    with open(path, "r") as program_file:
        source = program_file.read()
    program_globals = {"__name__": "__main__", "__file__": path}
    exec(source, program_globals)


def main():
    """Show a button-controlled program list and run the selected file."""
    byui_ebadge.initialize()
    programs = list_programs()
    selected = 0
    previous_up = False
    previous_down = False
    previous_a = False
    draw_menu(programs, selected)

    try:
        while True:
            up = byui_ebadge.is_pressed(byui_ebadge.BUTTON_UP)
            down = byui_ebadge.is_pressed(byui_ebadge.BUTTON_DOWN)
            button_a = byui_ebadge.is_pressed(byui_ebadge.BUTTON_A)

            changed = False
            if programs and up and not previous_up:
                selected = (selected - 1) % len(programs)
                changed = True
            elif programs and down and not previous_down:
                selected = (selected + 1) % len(programs)
                changed = True

            if changed:
                draw_menu(programs, selected)
            if programs and button_a and not previous_a:
                error_message = None
                try:
                    run_program(programs[selected])
                except KeyboardInterrupt:
                    pass
                except SystemExit:
                    pass
                except Exception as error:
                    print("Program error:", error)
                    error_message = str(error)

                byui_ebadge.initialize()
                if error_message is not None:
                    byui_ebadge.display_clear(byui_ebadge.BLACK)
                    byui_ebadge.display_text("Program error", x=8, y=8, color=byui_ebadge.RED)
                    byui_ebadge.display_text(error_message[:35], x=8, y=30)
                    byui_ebadge.pause(1500)
                programs = list_programs()
                if selected >= len(programs):
                    selected = max(0, len(programs) - 1)
                draw_menu(programs, selected)

            previous_up = up
            previous_down = down
            previous_a = button_a
            byui_ebadge.pause(30)
    except KeyboardInterrupt:
        pass
    finally:
        byui_ebadge.shutdown()


if __name__ == "__main__":
    main()
