"""Tests for recursive Python-file deletion used by deploy.py."""

import importlib.util
from pathlib import Path


_HELPER_PATH = (
    Path(__file__).resolve().parents[1] / "tools" / "erase_python_files.py"
)
_SPEC = importlib.util.spec_from_file_location("erase_python_files", _HELPER_PATH)
erase_python_files = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(erase_python_files)


class _FakeFilesystem:
    """Provide MicroPython-style directory entries for the cleanup helper."""

    def __init__(self):
        self.entries = {
            "/": [
                ("main.py", 0x8000),
                ("boot.py", 0x8000),
                ("logo.bmp", 0x8000),
                ("photos", 0x4000),
            ],
            "/photos": [
                ("frame.mpy", 0x8000),
                ("archive", 0x4000),
            ],
            "/photos/archive": [
                ("cache.pyc", 0x8000),
                ("picture.jpg", 0x8000),
            ],
        }
        self.removed = []

    def ilistdir(self, path):
        return iter(self.entries[path])

    def remove(self, path):
        self.removed.append(path)


def test_erase_python_files_recurses_and_preserves_non_python_files(monkeypatch):
    filesystem = _FakeFilesystem()
    monkeypatch.setattr(erase_python_files, "os", filesystem)

    removed = erase_python_files._erase_python_files("/")

    assert removed == 4
    assert set(filesystem.removed) == {
        "/main.py",
        "/boot.py",
        "/photos/frame.mpy",
        "/photos/archive/cache.pyc",
    }
    assert "/logo.bmp" not in filesystem.removed
    assert "/photos/archive/picture.jpg" not in filesystem.removed
