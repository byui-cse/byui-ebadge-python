"""Helpers for testing programs that use :mod:`byui_ebadge` without hardware."""

from contextlib import contextmanager

from backends.test_backend import TestBackend


def make_backend():
    """Create a deterministic in-memory backend for a test."""
    return TestBackend()


@contextmanager
def session(backend=None):
    """Initialize test mode and always shut it down when the block exits.

    Example::

        from testing import session

        with session() as board:
            board.press_button(byui_ebadge.BUTTON_A)
            assert byui_ebadge.is_pressed(byui_ebadge.BUTTON_A)
    """
    import byui_ebadge

    backend = backend or make_backend()
    byui_ebadge.initialize(mode="test", backend=backend)
    try:
        yield backend
    finally:
        byui_ebadge.shutdown()
