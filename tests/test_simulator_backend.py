"""Focused tests for simulator state and UI-thread lifecycle compatibility."""

import signal
import threading

from backends.simulator_backend import SimulatorBackend, _color_style


def test_simulator_leds_start_off_and_render_gray():
    backend = SimulatorBackend()

    assert backend.rgb_led == "off"
    assert backend.led_strip == ["off"] * 24
    assert _color_style(backend.rgb_led) == "#808080"
    assert all(_color_style(color) == "#808080" for color in backend.led_strip)


def test_simulator_records_outputs_without_starting_textual():
    backend = SimulatorBackend()

    backend.press_button("A")
    backend.set_joystick(-1.0, 1.0)
    backend.display_clear("black")
    backend.display_text("Ready", 4, 8, "white")
    backend.set_rgb_led("blue")
    backend.set_led_strip_pixel(2, "green")
    backend.play_tone(440, 100)

    assert backend.display_operations == [
        ("clear", "black"),
        ("text", "Ready", 4, 8, "white"),
    ]
    assert backend.rgb_led == "blue"
    assert backend.led_strip[2] == "green"
    assert backend.active_tone == (440, 100)
    assert backend.is_pressed("A") is True
    assert backend.joystick() == (-1.0, 1.0)


def test_simulator_suppresses_signal_registration_from_ui_thread(monkeypatch):
    backend = SimulatorBackend()
    registered = []

    def record_signal(signal_number, handler):
        registered.append((signal_number, handler))
        return signal.SIG_DFL

    monkeypatch.setattr(signal, "signal", record_signal)

    class FakeApp:
        def run(self):
            signal.signal(signal.SIGTSTP, lambda *_: None)
            signal.signal(signal.SIGCONT, lambda *_: None)
            if hasattr(signal, "SIGTTOU"):
                signal.signal(signal.SIGTTOU, lambda *_: None)
            signal.signal(signal.SIGINT, lambda *_: None)

    backend._app = FakeApp()
    worker = threading.Thread(target=backend._run_app)
    worker.start()
    worker.join()

    assert registered == []
    assert signal.signal is record_signal
    signal.signal(signal.SIGINT, lambda *_: None)
    assert [item[0] for item in registered] == [signal.SIGINT]


def test_simulator_shutdown_stops_and_joins_ui_thread():
    backend = SimulatorBackend()
    stop_requested = threading.Event()

    class FakeApp:
        is_running = True

        def call_from_thread(self, callback):
            callback()

        def exit(self):
            stop_requested.set()

    worker = threading.Thread(target=stop_requested.wait)
    worker.start()
    backend._app = FakeApp()
    backend._app_thread = worker

    backend.shutdown()

    assert stop_requested.is_set()
    assert not worker.is_alive()
    assert backend._app is None
    assert backend._app_thread is None
