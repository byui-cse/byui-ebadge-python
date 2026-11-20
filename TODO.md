# Project task list

## Completed

- [x] Add project instructions in `AGENTS.md`.
- [x] Add Python and V4.1.1 hardware specification drafts under `specifications/`.
- [x] Keep maintained examples focused on the public API.
- [x] Add beginner-facing example programs under `examples/`.

## Project structure and documentation

- [x] Evaluate the user-facing repository workflow: compare packaging `byui_ebadge` for installation with pip against having users fork the repository and add programs under `examples/`. Document pros, cons, and a recommendation, considering setup effort, offline use, version updates, local edits, sharing, and maintenance.
- [x] Create the top-level README with the repository map, usage instructions, current V4.1.1 board photos, and MicroPython installation steps adapted from the supplied eBadge setup guidance.
- [x] Add the BYU-I eBadge repository (`git@github.com:BYU-I-eBadge/e-badge.git`) as a Git submodule under `assets/board/`.
- [x] Create `mpremote` copy commands for the hardware backend dependencies and user programs, including device filenames and paths. Physical badge deployment remains to be validated after the backend's uncalibrated features are completed.
- [x] Review the V4.1.1 hardware design and merge useful findings from `specifications/board_info_v4_1.md` into `specifications/hardware-v4.1.1.md`, including verified pin mappings, SD wiring, jumperable power sensing, wireless capability, and API candidates. Keep firmware-dependent details and ADC calibration clearly qualified.
- [x] Record the initial source import and related documentation in Git history (initial project commit `55be908`).

## `byui_ebadge.py` and runtime modes

- [x] Review the public API with the project owner; agreed decisions are recorded in [`specifications/api-proposal.md`](specifications/api-proposal.md).
- [ ] Implement one stable, beginner-friendly `byui_ebadge.py` API backed by three modes:
  - [x] Hardware mode: delegate supported operations to maintained, repository-owned MicroPython drivers on the eBadge.
  - [x] Simulator mode: run on a regular computer with a terminal board visual, simple display, and clickable buttons using Textual.
    - [x] Put the BYU-Idaho logo in the blue board artwork as permanent silkscreen-style decoration, separate from the program-controlled simulated screen. Provide a terminal-compatible fallback when image rendering is unavailable.
    - [x] Focus the simulator on buttons, joystick, screen, LEDs, and buzzer; clearly document unsupported simulation such as Wi-Fi, ADC voltage readings, and full electrical behavior.
  - [x] Test mode: a deterministic, headless backend for `pytest`; it must not start the terminal interface or wait for input.
- [x] Define backend selection and initialization without import-time hardware or UI side effects. Keep shared API behavior consistent across modes.
- [x] Implement the functions used by `examples/` (button reads, LED output, Wi-Fi scanning, tones, display text/image) in all applicable backends.
- [x] Add simple display drawing helpers for pixels, lines, and outlined or filled rectangles in the applicable backends.
- [x] Implement accelerometer readings in g and battery-voltage readings in volts in applicable backends. Hardware battery readings use the nominal ×16 divider ratio and still require physical calibration; never describe voltage as a charge percentage.
- [x] Implement external GPIO input/output helpers, `HIGH`/`LOW` checks, PWM output, analog voltage measurement, and addressable LED strip controls in each applicable backend. GPIO13–GPIO18 (`IO13`–`IO18`) are ADC2 channels 2–7 on the ESP32-S3; analog reads require Wi-Fi inactive.
- [ ] Validate `read_voltage()` accuracy with a known source on physical V4.1.1 hardware and record both the source voltage and reported reading. The human-run `HardwareBackend` check passed but did not record measurement values.
- [ ] Calibrate normalized joystick direction and center behavior on physical V4.1.1 hardware before enabling hardware-mode `joystick()`.
- [x] Document the standard jumper-bridge routing assumed by built-in peripheral helpers and the current procedure for nonstandard routing: use GPIO helpers for the actual signal or restore the standard bridge positions.
- [x] Create a host-side `resize_image.py` utility that accepts common PNG/JPG inputs, preserves aspect ratio, fits them to the 320 × 240 badge display, and outputs a 24-bit BMP supported by the hardware image helper.
- [x] Track `assets/byui-cse.png`, generate its prepared BMP with `resize_image.py`, and document how to copy that resource to the badge before running the logo example.

## Tests

- [x] Add `pytest` unit tests for `byui_ebadge.py` using the headless test backend. Cover button state, LED state, tone requests, Wi-Fi results, display operations, and backend selection.
- [x] Create a guided, interactive hardware test runner for the `byui_ebadge.py` public API. It prompts for button, joystick, LED, display, buzzer, Wi-Fi, GPIO HIGH/LOW, PWM, ADC, accelerometer, and battery/power checks; records pass/fail/skip and supports retry.
- [x] Add an interactive hardware test program for `HardwareBackend`, independently of `byui_ebadge.py`, covering the same physical components where practical.
- [x] Include accelerometer and battery-voltage checks in headless and interactive hardware validation. These are not required in the focused terminal simulator.
- [x] Document how to run automated tests on a computer and how to run/interpret the interactive checks on the physical badge.
- [x] Have a human upload and run `hardware_tests/run_hardware_backend_checks.py` on a physical V4.1.1 badge. Reported: PASS for A/B/up/down/left/right buttons, RGB indicator, addressable LED strip, buzzer, display, Wi-Fi scan, GPIO HIGH/LOW loopback, GPIO PWM, ADC voltage, accelerometer, and battery/selected-rail voltage; joystick was skipped pending calibration.
- [ ] Have a human upload and run `hardware_tests/run_byui_ebadge_checks.py` on a physical V4.1.1 badge; record the results and investigate any failures.

## Example programs

- [x] Example 1: light an LED while a button is pressed (`examples/01_button_led.py`).
- [x] Example 2: list nearby Wi-Fi networks (`examples/02_list_wifi.py`).
- [x] Example 3: play a note when a button is pressed (`examples/03_button_tone.py`).
- [x] Example 4: display the BYU-Idaho logo from a prepared display image (`examples/04_display_logo.py`).
- [x] Example 5: draw pixels, lines, and outlined and filled rectangles (`examples/05_display_shapes.py`).

## Additional requested work

- [x] Rename the Python module/import to `byui_ebadge.py` / `byui_ebadge` and update maintained code and documentation.
- [x] Rename the GitHub repository to `byui-cse/byui-ebadge-python` and update this checkout's `origin` remote.
- [x] Extend `deploy.py` to upload a complete local directory tree, including resources such as a directory of photos, while preserving its directory structure on the badge.
- [x] Clean up README deployment commands to use mpremote port auto-detection by default and explain that `--port <PORT>` is optional when automatic selection works.
- [x] Add a digital picture-frame example that cycles through image files in a directory.
- [x] Review the Tetris, Etch-a-Sketch, and Snake program requirements to identify required capabilities; the existing public button, display, tone, LED, and pause helpers were sufficient, so no backend changes were needed.
  - [x] Add Snake using the D-pad and current public drawing helpers (`examples/07_snake.py`).
  - [x] Add an Etch-a-Sketch variant using the D-pad and current public drawing helpers (`examples/08_etch_sketch.py`).
  - [x] Port Tetris using the D-pad and current public drawing helpers (`examples/09_tetris.py`).
- [x] Create a program selector that lets a user choose which installed program to run (`program_selector.py`). Deploy it as `main.py`; it returns to the menu after a selected program finishes or is interrupted.
- [x] Investigate USB keyboard support: V4.1.1 has native USB-host hardware, but the board setup notes identify keyboard host mode as Arduino-only and the supplied MicroPython 1.29.0 generic ESP32-S3 firmware has no USB-host HID API. A keyboard terminal would need custom firmware or a native host driver; it is not supported by the current Python target. See [`hardware-v4.1.1.md`](specifications/hardware-v4.1.1.md).
- [x] Expand Wi-Fi support in `byui_ebadge.py`. Use MicroPython's built-in `network` module instead of adding a separate Wi-Fi dependency; add an on-screen network and password flow plus dictionary and display helpers for connection details.
  - [ ] Validate the on-screen setup flow and connected SSID, RSSI, and IP reporting on physical V4.1.1 hardware.
- [x] Add a README tutorial explaining how to build a program, detect pressed buttons, control the board lights, and use the display.

## Deferred future work

- [ ] Add Bluetooth Low Energy (BLE) support after the target MicroPython firmware's `bluetooth.BLE` and `gap_scan` behavior is verified on the badge.
- [ ] Add SD-card support after SPI/SD mounting, filesystem behavior, and safe unmounting are verified with the target MicroPython firmware. V4.1.1 wiring is documented as GPIO37–40.
- [ ] Validate `read_battery_voltage()` on physical hardware; V4.1.1 uses a 150 kΩ / 10 kΩ divider (nominal ×16), but ADC conversion needs calibration and the signal measures the selected `PWR_RAW` rail.
- [x] Add `connect_wifi()`, `disconnect_wifi()`, and `is_wifi_connected()` helpers that handle already-connected or already-disconnected states cleanly.
- [x] Add `download_url()` for HTTP GET. It checks Wi-Fi first, supports optional `urequests`/`requests`, closes responses, and can return bytes or save them to a file.
- [x] Add `post_url()` for HTTP POST with text, bytes, or JSON. It checks Wi-Fi first, supports optional `urequests`/`requests`, and closes responses.
- [ ] Evaluate remaining API additions from the V4.1 examples: servo control, UART helpers, accelerometer events, and higher-level song playback.
