"""Tests for the beginner-facing API using the headless backend."""

import pytest

import byui_ebadge


def test_fixture_selects_headless_test_mode(badge_backend):
    assert byui_ebadge.current_mode() == "test"
    assert badge_backend.initialized
    assert type(badge_backend).__module__ == "backends.test_backend"


def test_button_state_can_be_controlled(badge_backend):
    assert byui_ebadge.is_pressed(byui_ebadge.BUTTON_A) is False

    badge_backend.press_button(byui_ebadge.BUTTON_A)
    assert byui_ebadge.is_pressed(byui_ebadge.BUTTON_A) is True

    badge_backend.release_button(byui_ebadge.BUTTON_A)
    assert byui_ebadge.is_pressed(byui_ebadge.BUTTON_A) is False


def test_button_rejects_unknown_name(badge_backend):
    with pytest.raises(ValueError, match=r"BUTTON_\* constants"):
        byui_ebadge.is_pressed("start")


def test_rgb_led_accepts_names_and_rgb_tuples(badge_backend):
    byui_ebadge.set_rgb_led("BLUE")
    assert badge_backend.rgb_led == "blue"

    byui_ebadge.set_rgb_led((12, 34, 56))
    assert badge_backend.rgb_led == (12, 34, 56)

    byui_ebadge.turn_rgb_led_off()
    assert badge_backend.rgb_led == byui_ebadge.OFF


def test_addressable_led_strip_pixel_frame_and_clear(badge_backend):
    byui_ebadge.set_led_strip_pixel(3, "red")
    assert badge_backend.led_strip[3] == "red"

    frame = ["off"] * 24
    frame[7] = (10, 20, 30)
    byui_ebadge.set_led_strip(frame)
    assert badge_backend.led_strip == frame

    byui_ebadge.clear_led_strip()
    assert badge_backend.led_strip == [byui_ebadge.OFF] * 24


@pytest.mark.parametrize("index", [-1, 24])
def test_addressable_led_strip_rejects_out_of_range_index(badge_backend, index):
    with pytest.raises(ValueError, match="from 0 to 23"):
        byui_ebadge.set_led_strip_pixel(index, "red")


def test_buzzer_records_and_stops_tone(badge_backend):
    byui_ebadge.play_tone(440, 250)

    assert badge_backend.tones == [(440, 250)]
    assert badge_backend.active_tone == (440, 250)

    byui_ebadge.stop_tone()
    assert badge_backend.active_tone is None


def test_buzzer_rejects_invalid_tone_values(badge_backend):
    with pytest.raises(ValueError, match="greater than zero"):
        byui_ebadge.play_tone(0, 100)
    with pytest.raises(ValueError, match="must not be negative"):
        byui_ebadge.play_tone(440, -1)


def test_display_operations_are_inspectable(badge_backend):
    byui_ebadge.display_clear(byui_ebadge.BLUE)
    byui_ebadge.display_text("Hello", x=12, y=24, color=(255, 255, 0))
    byui_ebadge.display_image("logo.bmp", x=2, y=3)

    assert badge_backend.display_color == byui_ebadge.BLUE
    assert badge_backend.display_operations == [
        ("clear", byui_ebadge.BLUE),
        ("text", "Hello", 12, 24, (255, 255, 0)),
        ("image", "logo.bmp", 2, 3),
    ]


def test_display_rejects_unknown_color(badge_backend):
    with pytest.raises(ValueError, match="unknown color name"):
        byui_ebadge.display_clear("navy")


def test_wifi_results_are_simple_by_default_and_detailed_on_request(badge_backend):
    badge_backend.set_wifi_results(
        [
            {
                "ssid": "ExampleNet",
                "signal_dbm": -42,
                "channel": 6,
                "security": "WPA2",
            }
        ]
    )

    assert byui_ebadge.scan_wifi() == [("ExampleNet", -42)]
    assert byui_ebadge.scan_wifi(include_details=True) == [
        {
            "ssid": "ExampleNet",
            "signal_dbm": -42,
            "channel": 6,
            "security": "WPA2",
        }
    ]


def test_wifi_connection_state_can_be_managed(badge_backend):
    assert byui_ebadge.is_wifi_connected() is False
    assert byui_ebadge.connect_wifi("ExampleNet", "secret") is True
    assert byui_ebadge.is_wifi_connected() is True

    byui_ebadge.disconnect_wifi()
    assert byui_ebadge.is_wifi_connected() is False


def test_http_get_requires_wifi_and_can_save_response(badge_backend, tmp_path):
    with pytest.raises(RuntimeError, match="connect to Wi-Fi"):
        byui_ebadge.download_url("https://example.com/photo.bmp")

    badge_backend.wifi_connected = True
    badge_backend.http_get_response = b"image bytes"
    assert byui_ebadge.download_url("https://example.com/photo.bmp") == b"image bytes"

    output = tmp_path / "photo.bmp"
    assert byui_ebadge.download_url(
        "https://example.com/photo.bmp", str(output)
    ) == str(output)
    assert output.read_bytes() == b"image bytes"
    assert badge_backend.http_requests[0] == (
        "GET",
        "https://example.com/photo.bmp",
        None,
    )


def test_http_post_requires_wifi_and_records_json_request(badge_backend):
    with pytest.raises(RuntimeError, match="connect to Wi-Fi"):
        byui_ebadge.post_url("https://example.com/api", json={"value": 3})

    badge_backend.wifi_connected = True
    badge_backend.http_post_response = b"created"
    assert byui_ebadge.post_url(
        "https://example.com/api", json={"value": 3}
    ) == b"created"
    assert badge_backend.http_requests == [
        ("POST", "https://example.com/api", None, {"value": 3}, None)
    ]


def test_http_post_rejects_both_data_and_json(badge_backend):
    with pytest.raises(ValueError, match="either data or json"):
        byui_ebadge.post_url("https://example.com/api", data="x", json={"x": 1})


def test_accelerometer_returns_g_values_and_can_be_unavailable(badge_backend):
    badge_backend.set_accelerometer(0.15, -0.25, 0.97)
    assert byui_ebadge.read_accelerometer() == (0.15, -0.25, 0.97)

    badge_backend.accelerometer_values = None
    assert byui_ebadge.read_accelerometer() is None


def test_battery_voltage_returns_volts_not_a_percentage(badge_backend):
    badge_backend.set_battery_voltage(3.87)
    assert byui_ebadge.read_battery_voltage() == 3.87


def test_shutdown_releases_test_outputs(badge_backend):
    byui_ebadge.set_rgb_led("green")
    byui_ebadge.play_tone(330, 100)

    byui_ebadge.shutdown()

    assert byui_ebadge.current_mode() is None
    assert badge_backend.initialized is False
    assert badge_backend.rgb_led == byui_ebadge.OFF
    assert badge_backend.active_tone is None


def test_test_context_manager_shuts_down_after_use():
    from testing import session

    with session() as backend:
        assert byui_ebadge.current_mode() == "test"
        assert backend.initialized

    assert byui_ebadge.current_mode() is None
    assert backend.initialized is False
