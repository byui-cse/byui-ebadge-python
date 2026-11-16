"""Host-side tests for single-image and directory image preparation."""

import builtins
import sys

import pytest

import resize_image


def _pillow_image():
    return pytest.importorskip("PIL.Image")


def test_resize_image_makes_a_24_bit_bmp_without_changing_aspect_ratio(tmp_path):
    image_module = _pillow_image()
    source = tmp_path / "landscape.png"
    image_module.new("RGB", (640, 480), (20, 80, 160)).save(source)

    output = resize_image.resize_image(source)

    assert output == tmp_path / "landscape_badge.bmp"
    with image_module.open(output) as result:
        assert result.size == (320, 240)
        assert result.mode == "RGB"
        assert result.format == "BMP"
    assert int.from_bytes(output.read_bytes()[28:30], "little") == 24


def test_resize_image_does_not_enlarge_small_images(tmp_path):
    image_module = _pillow_image()
    source = tmp_path / "small.jpeg"
    image_module.new("RGB", (100, 50), (40, 90, 130)).save(source)

    output = resize_image.resize_image(source)

    with image_module.open(output) as result:
        assert result.size == (100, 50)


def test_resize_image_composites_transparency_on_black(tmp_path):
    image_module = _pillow_image()
    source = tmp_path / "transparent.png"
    image = image_module.new("RGBA", (2, 1))
    image.putdata([(255, 0, 0, 0), (0, 255, 0, 255)])
    image.save(source)

    output = resize_image.resize_image(source)

    with image_module.open(output) as result:
        assert result.getpixel((0, 0)) == (0, 0, 0)
        assert result.getpixel((1, 0)) == (0, 255, 0)


def test_resize_image_rejects_unsupported_extensions_before_importing_pillow(
    monkeypatch, tmp_path
):
    original_import = builtins.__import__

    def import_without_pillow(name, *args, **kwargs):
        if name == "PIL":
            raise ImportError("Pillow intentionally unavailable in this test")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", import_without_pillow)
    source = tmp_path / "unsupported.gif"

    with pytest.raises(ValueError, match="PNG, JPG, or JPEG"):
        resize_image.resize_image(source)


def test_resize_image_rejects_non_bmp_output_before_opening_source(tmp_path):
    source = tmp_path / "image.png"

    with pytest.raises(ValueError, match="end in .bmp"):
        resize_image.resize_image(source, tmp_path / "image.png")


def test_resize_directory_converts_nested_photos_and_skips_other_files(tmp_path):
    image_module = _pillow_image()
    source_directory = tmp_path / "photos"
    nested_directory = source_directory / "trips" / "day_one"
    nested_directory.mkdir(parents=True)
    image_module.new("RGB", (640, 480), (200, 10, 20)).save(
        source_directory / "front.png"
    )
    image_module.new("RGB", (80, 60), (20, 100, 40)).save(
        nested_directory / "small.JPG"
    )
    (source_directory / "notes.txt").write_text("not an image\n")

    output_directory, outputs = resize_image.resize_directory(source_directory)

    assert output_directory == tmp_path / "photos_badge"
    assert outputs == (
        output_directory / "front_badge.bmp",
        output_directory / "trips" / "day_one" / "small_badge.bmp",
    )
    with image_module.open(outputs[0]) as large_image:
        assert large_image.size == (320, 240)
    with image_module.open(outputs[1]) as small_image:
        assert small_image.size == (80, 60)


def test_resize_directory_rejects_empty_image_directories(tmp_path):
    source_directory = tmp_path / "empty_photos"
    source_directory.mkdir()

    with pytest.raises(ValueError, match="contains no PNG, JPG, or JPEG"):
        resize_image.resize_directory(source_directory)


def test_resize_directory_rejects_output_equal_to_source(tmp_path):
    source_directory = tmp_path / "photos"
    source_directory.mkdir()

    with pytest.raises(ValueError, match="outside the source"):
        resize_image.resize_directory(source_directory, source_directory)


def test_resize_directory_rejects_output_nested_in_source(tmp_path):
    source_directory = tmp_path / "photos"
    source_directory.mkdir()

    with pytest.raises(ValueError, match="outside the source"):
        resize_image.resize_directory(source_directory, source_directory / "prepared")


def test_resize_directory_detects_filename_collisions_before_writing(tmp_path):
    source_directory = tmp_path / "photos"
    source_directory.mkdir()
    (source_directory / "same.png").write_bytes(b"first")
    (source_directory / "same.jpg").write_bytes(b"second")
    output_directory = tmp_path / "prepared"

    with pytest.raises(ValueError, match="same output filename"):
        resize_image.resize_directory(source_directory, output_directory)

    assert not output_directory.exists()


def test_directory_cli_uses_the_requested_output_directory(tmp_path, monkeypatch, capsys):
    image_module = _pillow_image()
    source_directory = tmp_path / "photos"
    source_directory.mkdir()
    image_module.new("RGB", (32, 24), (20, 40, 60)).save(
        source_directory / "one.png"
    )
    output_directory = tmp_path / "prepared"
    monkeypatch.setattr(sys, "argv", [
        "resize_image.py",
        str(source_directory),
        "--output-directory",
        str(output_directory),
    ])

    assert resize_image.main() == 0
    assert (output_directory / "one_badge.bmp").is_file()
    assert str(output_directory) in capsys.readouterr().out
