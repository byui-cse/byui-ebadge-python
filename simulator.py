"""Run an example or project program with the local eBadge simulator.

Run from the repository root, for example:

    python simulator.py 07_snake
    python simulator.py projects/my_program.py

The child process runs on CPython, where ``pybadge.initialize()`` selects the
interactive simulator automatically.
"""

import argparse
import os
from pathlib import Path
import subprocess
import sys


REPOSITORY_ROOT = Path(__file__).resolve().parent
PROGRAM_DIRECTORIES = (
    REPOSITORY_ROOT / "examples",
    REPOSITORY_ROOT / "projects",
)


def _direct_candidates(path):
    """Return likely direct paths for a program argument."""
    if path.is_absolute():
        bases = (path,)
    else:
        bases = (Path.cwd() / path, REPOSITORY_ROOT / path)

    for candidate in bases:
        yield candidate
        if candidate.suffix.lower() != ".py":
            yield candidate.with_suffix(".py")


def _find_program(program_name):
    """Resolve a path or short program name to one Python file."""
    requested = Path(program_name).expanduser()
    for candidate in _direct_candidates(requested):
        if candidate.is_file() and candidate.suffix.lower() == ".py":
            return candidate.resolve()

    stem = requested.stem if requested.suffix else requested.name
    programs = []
    for directory in PROGRAM_DIRECTORIES:
        if directory.is_dir():
            programs.extend(directory.glob("*.py"))

    exact_matches = [
        path.resolve()
        for path in programs
        if path.name == requested.name or path.stem == stem
    ]
    matches = exact_matches
    if not matches:
        matches = [
            path.resolve()
            for path in programs
            if path.stem.endswith("_" + stem)
        ]

    matches = sorted(set(matches))
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        choices = "\n".join(
            "  {}".format(path.relative_to(REPOSITORY_ROOT)) for path in matches
        )
        raise ValueError(
            "Program name {!r} is ambiguous. Choose a path:\n{}".format(
                program_name, choices
            )
        )
    raise FileNotFoundError(
        "Program {!r} was not found. Use a path or a name from examples/ or "
        "projects/.".format(program_name)
    )


def _child_environment(program):
    """Add repository and program directories to the child's import path."""
    paths = [str(REPOSITORY_ROOT), str(program.parent)]
    inherited = os.environ.get("PYTHONPATH")
    if inherited:
        for path in inherited.split(os.pathsep):
            resolved = Path(path).expanduser() if path else Path.cwd()
            if not resolved.is_absolute():
                resolved = Path.cwd() / resolved
            paths.append(str(resolved))

    unique_paths = []
    for path in paths:
        if path and path not in unique_paths:
            unique_paths.append(path)

    environment = os.environ.copy()
    environment["PYTHONPATH"] = os.pathsep.join(unique_paths)
    return environment


def main():
    """Resolve and run the selected program in a simulator process."""
    parser = argparse.ArgumentParser(
        description="Run an example or project program in the terminal simulator."
    )
    parser.add_argument(
        "program",
        help="program path, example name, or project name (the .py suffix is optional)",
    )
    arguments = parser.parse_args()

    try:
        program = _find_program(arguments.program)
    except (FileNotFoundError, ValueError) as error:
        parser.error(str(error))

    return subprocess.call(
        [sys.executable, str(program)],
        cwd=str(REPOSITORY_ROOT),
        env=_child_environment(program),
    )


if __name__ == "__main__":
    sys.exit(main())
