"""Tests for the V4.1.1 hardware joystick calibration mapping."""

import pytest

from backends.hardware_backend import HardwareBackend


@pytest.mark.parametrize(
    "raw_value, expected",
    [
        (2012, 0.0),
        (2006, 0.0),
        (2021, 0.0),
        (455, -1.0),
        (3951, 1.0),
        (0, -1.0),
        (4095, 1.0),
    ],
)
def test_joystick_axis_center_endpoints_and_clamping(raw_value, expected):
    value = HardwareBackend._normalize_joystick_axis(raw_value, 2012, 455, 3951)

    assert value == pytest.approx(expected)


def test_joystick_axis_scales_each_side_from_center():
    left_half = HardwareBackend._normalize_joystick_axis(
        (2012 + 455) // 2, 2012, 455, 3951
    )
    right_half = HardwareBackend._normalize_joystick_axis(
        (2012 + 3951) // 2, 2012, 455, 3951
    )

    assert left_half == pytest.approx(-0.4565, abs=0.01)
    assert right_half == pytest.approx(0.4565, abs=0.01)
