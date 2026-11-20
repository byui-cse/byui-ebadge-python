"""Play the supplied Popcorn melody through the eBadge piezo buzzer.

Run with ``python simulator.py 12_popcorn`` on a computer, or deploy it with
``python deploy.py --install-library examples/12_popcorn.py`` to the badge.
Press Ctrl-C to stop playback.
"""

import byui_ebadge


C5, D5, E5, F5, G5, A5 = 523, 587, 659, 698, 784, 880
SIXTEENTH, DOTTED_EIGHTH, QUARTER, HALF = 63, 188, 250, 500
GAP_MS = 30

MELODY = (
    (C5, SIXTEENTH), (C5, QUARTER), (C5, DOTTED_EIGHTH), (C5, SIXTEENTH),
    (C5, DOTTED_EIGHTH), (D5, SIXTEENTH), (E5, QUARTER), (F5, DOTTED_EIGHTH),
    (G5, SIXTEENTH), (A5, QUARTER), (D5, HALF), (G5, QUARTER),
    (G5, QUARTER), (G5, DOTTED_EIGHTH), (A5, SIXTEENTH), (G5, DOTTED_EIGHTH),
    (F5, SIXTEENTH), (E5, DOTTED_EIGHTH), (C5, SIXTEENTH), (D5, QUARTER),
    (C5, HALF),
)


def main():
    byui_ebadge.initialize()
    byui_ebadge.display_clear()
    byui_ebadge.display_text("Popcorn", x=8, y=8)
    byui_ebadge.display_text("Playing...", x=8, y=28)

    try:
        while True:
            for frequency, duration in MELODY:
                byui_ebadge.play_tone(frequency, duration * 2)
                byui_ebadge.pause(GAP_MS)
            byui_ebadge.pause(800)
    except KeyboardInterrupt:
        byui_ebadge.stop_tone()
    finally:
        byui_ebadge.shutdown()


if __name__ == "__main__":
    main()
