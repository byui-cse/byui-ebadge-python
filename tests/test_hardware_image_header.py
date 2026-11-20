"""Tests for BMP header integers used by the MicroPython image loader."""

import pytest

from backends.hardware_backend import HardwareBackend


@pytest.mark.parametrize(
    "value, expected",
    [
        (b"\x40\x01\x00\x00", 320),
        (b"\xf0\xff\xff\xff", -16),
        (b"\x00\x00\x00\x80", -2147483648),
    ],
)
def test_read_signed_little_endian_32_bit(value, expected):
    assert HardwareBackend._read_signed_int32_le(value) == expected
