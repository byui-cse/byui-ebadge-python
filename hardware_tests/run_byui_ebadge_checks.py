"""Guided physical eBadge checks using the public ``byui_ebadge`` API.

Run this file with mpremote after installing the hardware backend files. The
GPIO loopback check requires a jumper wire from GPIO13 to GPIO14. The analog
check requires a known voltage source and common ground. Use only the
documented GPIO voltage range and skip any setup that is unavailable.
"""

import byui_ebadge


_results = []


class _SkipCheck(Exception):
    """Signal that a hardware check was intentionally skipped."""


def _record_check(name, action):
    """Run an action until it is passed, failed, or skipped."""
    while True:
        print("\n== {} ==".format(name))
        try:
            action()
        except _SkipCheck as error:
            print("Skipped: {}".format(error))
            _results.append((name, "SKIP"))
            return
        except byui_ebadge.UnsupportedFeatureError as error:
            print("Skipped: {}".format(error))
            _results.append((name, "SKIP"))
            return
        except Exception as error:
            print("The check raised {}: {}".format(type(error).__name__, error))

        choice = input("Record [p]ass, [f]ail, [r]etry, or [s]kip? ").strip().lower()
        if choice == "p":
            _results.append((name, "PASS"))
            return
        if choice == "f":
            _results.append((name, "FAIL"))
            return
        if choice == "s":
            _results.append((name, "SKIP"))
            return
        if choice != "r":
            print("Enter p, f, r, or s.")


def _check_button(button, label):
    input("Hold {} and press Enter. ".format(label))
    pressed = byui_ebadge.is_pressed(button)
    print("Pressed reading: {}".format(pressed))
    input("Release {} and press Enter. ".format(label))
    released = not byui_ebadge.is_pressed(button)
    print("Released reading: {}".format(released))
    print("Both readings should be True.")


def _check_rgb_led():
    for color in ("red", "green", "blue"):
        byui_ebadge.set_rgb_led(color)
        input("Confirm the RGB indicator appears {} and press Enter. ".format(color))
    byui_ebadge.turn_rgb_led_off()


def _check_led_strip():
    colors = ["off"] * 24
    for index, color in enumerate(("red", "green", "blue")):
        colors[index] = color
    byui_ebadge.set_led_strip(colors)
    input("Confirm strip LEDs 0–2 show red, green, and blue; press Enter. ")
    byui_ebadge.clear_led_strip()


def _check_buzzer():
    input("A 440 Hz tone will play briefly. Press Enter to continue. ")
    byui_ebadge.play_tone(440, 500)
    input("Did you hear the tone? Press Enter to record your result. ")


def _check_display():
    byui_ebadge.display_clear(byui_ebadge.BLUE)
    byui_ebadge.display_text("eBadge hardware check", 8, 8, byui_ebadge.WHITE)
    input("Confirm the blue screen and white text, then press Enter. ")
    byui_ebadge.display_clear(byui_ebadge.BLACK)


def _check_wifi():
    try:
        networks = byui_ebadge.scan_wifi()
        print("Visible networks (SSID, RSSI dBm):")
        for network in networks:
            print("  {}".format(network))
        if not networks:
            print("No networks were returned; this may be normal in a shielded area.")
        print("Current Wi-Fi information: {}".format(byui_ebadge.wifi_info()))
        byui_ebadge.display_wifi_info()
        input("Confirm the status shown on the display, then press Enter. ")
    finally:
        # The later ADC2 check requires Wi-Fi to be inactive.
        byui_ebadge.disconnect_wifi()


def _check_wifi_setup():
    print("Use the badge screen and buttons to select a network and enter its password.")
    print("The check disconnects Wi-Fi afterward so the ADC2 check can run.")
    try:
        connected = byui_ebadge.connect_wifi_with_screen()
        if not connected:
            raise RuntimeError("Wi-Fi setup was cancelled or did not connect.")

        state = byui_ebadge.is_wifi_connected()
        info = byui_ebadge.wifi_info()
        byui_ebadge.display_wifi_info()
        print("is_wifi_connected(): {}".format(state))
        print("wifi_info(): {}".format(info))
        input("Confirm the connected network and details, then press Enter. ")
        print("Both connection status and dictionary details should be available.")
    finally:
        # Also disable the interface after a timeout or canceled setup.
        byui_ebadge.disconnect_wifi()


def _check_http_helpers():
    print("Enter test endpoints, or leave both blank to skip this check.")
    get_url = input("Small HTTP GET URL (blank to skip GET): ").strip()
    post_url = input("HTTP POST test endpoint (blank to skip POST): ").strip()
    if not get_url and not post_url:
        raise _SkipCheck("no GET or POST test endpoint was supplied")
    if post_url:
        print("POST sends a small JSON test payload to the endpoint you entered.")

    try:
        if not byui_ebadge.is_wifi_connected():
            print("Use the badge screen and buttons to connect to Wi-Fi.")
            if not byui_ebadge.connect_wifi_with_screen():
                raise RuntimeError("Wi-Fi setup was cancelled or did not connect.")

        if get_url:
            save_path = input(
                "Optional GET destination file on the badge (blank returns bytes): "
            ).strip()
            if save_path:
                result = byui_ebadge.download_url(get_url, filename=save_path)
                print("GET saved the response to {}.".format(result))
            else:
                result = byui_ebadge.download_url(get_url)
                print("GET returned {} bytes.".format(len(result)))

        if post_url:
            result = byui_ebadge.post_url(
                post_url,
                json={"message": "eBadge hardware check"},
            )
            print("POST returned {} response bytes.".format(len(result)))
        input("Review the GET/POST results, then press Enter to record them. ")
    finally:
        byui_ebadge.disconnect_wifi()


def _check_joystick():
    print("Check the center and each direction using normalized (x, y) values.")
    readings = {}
    for position in ("center", "left", "right", "up", "down"):
        input("Place the joystick at {} and press Enter. ".format(position))
        readings[position] = byui_ebadge.joystick()
        print("{}: {}".format(position, readings[position]))

    center = readings["center"]
    checks = (
        ("center", abs(center[0]) <= 0.1 and abs(center[1]) <= 0.1),
        ("left", readings["left"][0] <= -0.8 and abs(readings["left"][1]) <= 0.2),
        ("right", readings["right"][0] >= 0.8 and abs(readings["right"][1]) <= 0.2),
        ("up", readings["up"][1] >= 0.8 and abs(readings["up"][0]) <= 0.2),
        ("down", readings["down"][1] <= -0.8 and abs(readings["down"][0]) <= 0.2),
    )
    for position, passed in checks:
        print("{} direction: {}".format(position, "PASS" if passed else "FAIL"))
    if not all(passed for _, passed in checks):
        raise RuntimeError("Joystick direction or center readings were out of range.")


def _check_gpio_loopback():
    print("Connect GPIO13 to GPIO14 with a jumper wire; connect no power source.")
    input("After checking the loopback wire, press Enter to run the check. ")
    byui_ebadge.configure_pin(byui_ebadge.GPIO13, mode="output")
    byui_ebadge.configure_pin(byui_ebadge.GPIO14, mode="input")
    try:
        byui_ebadge.write_pin(byui_ebadge.GPIO13, byui_ebadge.HIGH)
        byui_ebadge.pause(10)
        high_read = byui_ebadge.is_high(byui_ebadge.GPIO14)
        byui_ebadge.write_pin(byui_ebadge.GPIO13, byui_ebadge.LOW)
        byui_ebadge.pause(10)
        low_read = byui_ebadge.is_low(byui_ebadge.GPIO14)
    finally:
        byui_ebadge.write_pin(byui_ebadge.GPIO13, byui_ebadge.LOW)
    print("HIGH loopback: {}; LOW loopback: {}".format(high_read, low_read))
    print("Both readings should be True.")


def _check_pwm():
    print("For a visible check, connect GPIO13 to an LED through a current-limiting resistor.")
    print("A scope or logic analyzer can also verify a 1 kHz, 50% waveform.")
    input("Connect a safe test load, or skip if unavailable; press Enter to continue. ")
    byui_ebadge.configure_pin(byui_ebadge.GPIO13, mode="output")
    try:
        byui_ebadge.set_pwm(byui_ebadge.GPIO13, frequency_hz=1000, duty_percent=50)
        input("Confirm the waveform or LED activity, then press Enter. ")
    finally:
        byui_ebadge.stop_pwm(byui_ebadge.GPIO13)
        byui_ebadge.write_pin(byui_ebadge.GPIO13, byui_ebadge.LOW)


def _check_adc():
    print("Connect a known 1.5 V source to GPIO13 and its negative to board GND.")
    print("The ADC measurement range is approximately 0.15–2.45 V; GPIO max is 3.3 V.")
    print("ADC2 reads require Wi-Fi to be inactive. Do not connect an unknown source.")
    input("After checking the source and common ground, press Enter to measure. ")
    byui_ebadge.configure_pin(byui_ebadge.GPIO13, mode="input")
    measured = byui_ebadge.read_voltage(byui_ebadge.GPIO13)
    print("GPIO13 voltage: {:.3f} V".format(measured))
    input("Compare with your source or meter, then press Enter to record the result. ")


def _check_accelerometer():
    before = byui_ebadge.read_accelerometer()
    print("Initial acceleration (g): {}".format(before))
    input("Tilt the badge, return it to rest, then press Enter. ")
    after = byui_ebadge.read_accelerometer()
    print("After movement (g): {}".format(after))
    input("Confirm the values changed and press Enter to record the result. ")


def _check_battery_voltage():
    print("This reading requires the VMain-to-IO12 jumper bridge.")
    print("It is an uncalibrated estimate of the selected power rail, not battery charge.")
    input("If the jumper is installed and Wi-Fi is off, press Enter to read. ")
    voltage = byui_ebadge.read_battery_voltage()
    print("Estimated selected-rail voltage: {:.3f} V".format(voltage))
    input("Compare with a meter if available, then press Enter to record. ")


def run_joystick_check():
    """Run only the normalized joystick check on physical hardware."""
    del _results[:]
    byui_ebadge.initialize(mode="hardware")
    try:
        _record_check("Joystick", _check_joystick)
    finally:
        byui_ebadge.shutdown()

    print("\nJoystick check summary:")
    for name, result in _results:
        print("{}: {}".format(result, name))


def main():
    """Run each supported check and print a final result summary."""
    # A MicroPython REPL can import this module once and call main repeatedly.
    # Start each displayed summary with only this invocation's results.
    del _results[:]
    byui_ebadge.initialize(mode="hardware")
    try:
        _record_check("Button A", lambda: _check_button(byui_ebadge.BUTTON_A, "A"))
        _record_check("Button B", lambda: _check_button(byui_ebadge.BUTTON_B, "B"))
        _record_check("Up button", lambda: _check_button(byui_ebadge.BUTTON_UP, "Up"))
        _record_check("Down button", lambda: _check_button(byui_ebadge.BUTTON_DOWN, "Down"))
        _record_check("Left button", lambda: _check_button(byui_ebadge.BUTTON_LEFT, "Left"))
        _record_check("Right button", lambda: _check_button(byui_ebadge.BUTTON_RIGHT, "Right"))
        _record_check("Joystick", _check_joystick)
        _record_check("RGB indicator", _check_rgb_led)
        _record_check("Addressable LED strip", _check_led_strip)
        _record_check("Buzzer", _check_buzzer)
        _record_check("Display", _check_display)
        _record_check("Wi-Fi scan", _check_wifi)
        _record_check("Wi-Fi setup and connection info", _check_wifi_setup)
        _record_check("HTTP GET and POST", _check_http_helpers)
        _record_check("GPIO HIGH/LOW loopback", _check_gpio_loopback)
        _record_check("GPIO PWM", _check_pwm)
        _record_check("Analog voltage", _check_adc)
        _record_check("Accelerometer", _check_accelerometer)
        _record_check("Battery / selected-rail voltage", _check_battery_voltage)
    finally:
        byui_ebadge.shutdown()

    print("\nHardware check summary:")
    for name, result in _results:
        print("{}: {}".format(result, name))


if __name__ == "__main__":
    main()
