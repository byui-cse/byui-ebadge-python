"""Host-side tests for the mpremote deployment helper."""

from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

import deploy


def test_build_command_copies_library_program_assets_and_directories(tmp_path):
    program = tmp_path / "show.py"
    first_asset = tmp_path / "cover.bmp"
    second_asset = tmp_path / "icon.bmp"
    first_directory = tmp_path / "photos"
    second_directory = tmp_path / "icons"

    command = deploy.build_command(
        "COM8",
        install_library=True,
        program=program,
        assets=(first_asset, second_asset),
        directories=(first_directory, second_directory),
    )

    assert command == [
        sys.executable,
        "-m",
        "mpremote",
        "connect",
        "COM8",
        "fs",
        "cp",
        str(deploy.PROJECT_ROOT / "byui_ebadge.py"),
        ":byui_ebadge.py",
        "+",
        "fs",
        "cp",
        "-r",
        str(deploy.PROJECT_ROOT / "backends"),
        ":",
        "+",
        "fs",
        "cp",
        str(program),
        ":main.py",
        "+",
        "fs",
        "cp",
        str(first_asset),
        str(second_asset),
        ":",
        "+",
        "fs",
        "cp",
        "-r",
        str(first_directory),
        str(second_directory),
        ":",
    ]


def test_main_runs_mpremote_and_returns_its_exit_code(tmp_path, monkeypatch):
    program = tmp_path / "show.py"
    program.write_text("print('hello')\n")
    photos = tmp_path / "photos"
    photos.mkdir()
    asset = tmp_path / "cover.bmp"
    asset.write_bytes(b"BMP")
    calls = []

    def fake_run(command, check):
        calls.append((command, check))
        return SimpleNamespace(returncode=7)

    monkeypatch.setattr(sys, "argv", [
        "deploy.py",
        "--port",
        "COM9",
        "--install-library",
        "--asset",
        str(asset),
        "--directory",
        str(photos),
        str(program),
    ])
    monkeypatch.setattr(deploy.subprocess, "run", fake_run)

    assert deploy.main() == 7
    assert len(calls) == 1
    command, check = calls[0]
    assert check is False
    assert command[:5] == [sys.executable, "-m", "mpremote", "connect", "COM9"]
    assert str(program.resolve()) in command
    assert str(asset.resolve()) in command
    assert str(photos.resolve()) in command


def test_main_rejects_missing_program_before_running_mpremote(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["deploy.py", "missing.py"])

    with pytest.raises(SystemExit) as error:
        deploy.main()

    assert error.value.code == 2


def test_main_rejects_a_file_as_a_directory(monkeypatch, tmp_path):
    file_path = tmp_path / "not-a-directory"
    file_path.write_text("file\n")
    monkeypatch.setattr(
        sys,
        "argv",
        ["deploy.py", "--directory", str(file_path)],
    )

    with pytest.raises(SystemExit) as error:
        deploy.main()

    assert error.value.code == 2
