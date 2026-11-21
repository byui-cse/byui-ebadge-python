"""Remove Python source and bytecode files from the badge filesystem.

This script runs on the badge through ``mpremote run`` and is not copied there.
"""

import os


_PYTHON_SUFFIXES = (".py", ".mpy", ".pyc")
_DIRECTORY_TYPE = 0x4000


def _join_path(directory, name):
    """Join a remote directory and entry name using MicroPython paths."""
    if directory == "/":
        return "/" + name
    return directory + "/" + name


def _erase_python_files(directory):
    """Recursively delete Python files and return the number removed."""
    removed = 0
    for entry in list(os.ilistdir(directory)):
        name, entry_type = entry[0], entry[1]
        if isinstance(name, bytes):
            name = name.decode()
        path = _join_path(directory, name)

        if entry_type & _DIRECTORY_TYPE:
            removed += _erase_python_files(path)
        elif name.endswith(_PYTHON_SUFFIXES):
            print("Removing {}".format(path))
            os.remove(path)
            removed += 1
    return removed


def main():
    """Erase Python files from the badge's root filesystem."""
    removed = _erase_python_files("/")
    print("Removed {} Python file(s).".format(removed))


if __name__ == "__main__":
    main()
