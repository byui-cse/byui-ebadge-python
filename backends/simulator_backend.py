"""Focused terminal simulator for buttons, display, LEDs, and buzzer."""

import atexit
import signal
import threading
import time

from backends.test_backend import TestBackend
from pybadge import UnsupportedFeatureError


class SimulatorBackend(TestBackend):
    """Interactive terminal model for the board controls and outputs."""

    def __init__(self):
        super().__init__()
        self._app = None
        self._app_thread = None
        self._app_started = threading.Event()
        self._app_stopped = threading.Event()
        self._app_error = None
        self._atexit_registered = False
        self._tone_deadline = None

    def initialize(self):
        super().initialize()
        try:
            from textual.app import App, ComposeResult
            from textual.containers import Horizontal, Vertical
            from textual.widgets import Button, Static
        except ImportError as error:
            raise RuntimeError(
                "The simulator needs Textual. Install it with "
                "'python -m pip install textual' or run mode='test'."
            ) from error

        backend = self

        class BadgeApp(App):
            """Small interactive view of the eBadge board."""

            CSS = """
            Screen { align: center middle; }
            #board { width: 94; height: 32; padding: 0 2; background: #07539b; border: round #56a3e8; }
            #controls { height: 22; align: center middle; }
            #left-controls { width: 29; height: 22; align: center middle; }
            #directions { height: 12; align: center middle; }
            .direction-row { height: 3; align: center middle; }
            #actions { width: 18; height: 6; }
            #action-a-row { height: 3; align: center middle; }
            #action-b-row { height: 3; align: left middle; }
            #brand { width: 8; height: 6; margin: 0 1; content-align: center middle; text-align: center; color: white; text-style: bold; }
            #screen { width: 34; height: 13; padding: 1; margin: 3 1 0 1; border: heavy #d1d5db; background: black; color: white; overflow: hidden; }
            #joystick { width: 27; height: 11; align: center middle; }
            #action-area { width: 15; height: 22; align: right bottom; }
            .joystick-row { height: 3; align: center middle; }
            #stick-label { height: 1; content-align: center middle; color: #dbeafe; }
            .pad-button { min-width: 6; height: 3; margin: 0 1; }
            .stick-button { min-width: 5; height: 3; margin: 0 0; }
            #stick-center { min-width: 9; }
            #outputs { height: 6; content-align: center middle; color: white; }
            #help { height: 2; content-align: center middle; color: #dbeafe; }
            """

            TITLE = "BYU-I eBadge Simulator"
            BINDINGS = [("q", "quit", "Quit")]

            def compose(self) -> ComposeResult:
                with Vertical(id="board"):
                    with Horizontal(id="controls"):
                        with Vertical(id="left-controls"):
                            with Vertical(id="joystick"):
                                yield Static("Joystick", id="stick-label")
                                with Horizontal(classes="joystick-row"):
                                    yield Button("NW", id="stick-nw", classes="stick-button")
                                    yield Button("N", id="stick-n", classes="stick-button")
                                    yield Button("NE", id="stick-ne", classes="stick-button")
                                with Horizontal(classes="joystick-row"):
                                    yield Button("W", id="stick-w", classes="stick-button")
                                    yield Button("Center", id="stick-center", classes="stick-button")
                                    yield Button("E", id="stick-e", classes="stick-button")
                                with Horizontal(classes="joystick-row"):
                                    yield Button("SW", id="stick-sw", classes="stick-button")
                                    yield Button("S", id="stick-s", classes="stick-button")
                                    yield Button("SE", id="stick-se", classes="stick-button")
                            with Vertical(id="directions"):
                                with Horizontal(classes="direction-row"):
                                    yield Button("Up", id="button-up", classes="pad-button")
                                with Horizontal(classes="direction-row"):
                                    yield Button("Left", id="button-left", classes="pad-button")
                                    yield Button("Right", id="button-right", classes="pad-button")
                                with Horizontal(classes="direction-row"):
                                    yield Button("Down", id="button-down", classes="pad-button")
                        yield Static("BYU\n────\nIDAHO", id="brand")
                        yield Static(backend._screen_text(), id="screen")
                        with Vertical(id="action-area"):
                            with Vertical(id="actions"):
                                with Horizontal(id="action-a-row"):
                                    yield Button("A", id="button-a", classes="pad-button success")
                                with Horizontal(id="action-b-row"):
                                    yield Button("B", id="button-b", classes="pad-button warning")
                    yield Static(backend._output_text(), id="outputs")
                    yield Static(
                        "Click controls · center the stick to reset · q closes the board",
                        id="help",
                    )

            def on_button_pressed(self, event: Button.Pressed) -> None:
                stick_values = {
                    "stick-nw": (-1.0, 1.0),
                    "stick-n": (0.0, 1.0),
                    "stick-ne": (1.0, 1.0),
                    "stick-w": (-1.0, 0.0),
                    "stick-center": (0.0, 0.0),
                    "stick-e": (1.0, 0.0),
                    "stick-sw": (-1.0, -1.0),
                    "stick-s": (0.0, -1.0),
                    "stick-se": (1.0, -1.0),
                }
                stick = stick_values.get(event.button.id)
                if stick is not None:
                    backend.set_joystick(*stick)
                    return

                button = {
                    "button-a": "A",
                    "button-b": "B",
                    "button-up": "up",
                    "button-down": "down",
                    "button-left": "left",
                    "button-right": "right",
                }.get(event.button.id)
                if button is None:
                    return
                backend.press_button(button)
                self.set_timer(0.18, lambda: backend.release_button(button))

            def on_mount(self) -> None:
                backend._app_started.set()
                self.set_interval(0.1, self.refresh_board)

            def refresh_board(self) -> None:
                screen = self.query_one("#screen", Static)
                screen.styles.background = _color_style(backend.display_color)
                screen.update(backend._screen_text())
                self.query_one("#outputs", Static).update(backend._output_text())

        self._app = BadgeApp()
        self._app_thread = threading.Thread(
            target=self._run_app,
            name="pybadge-terminal-simulator",
            daemon=True,
        )
        atexit.register(self.shutdown)
        self._atexit_registered = True
        self._app_thread.start()
        if not self._app_started.wait(timeout=5.0):
            app_error = self._app_error
            self.shutdown()
            if app_error is not None:
                raise RuntimeError("The terminal simulator could not start.") from app_error
            raise RuntimeError("The terminal simulator did not finish starting.")

    def _run_app(self):
        """Run Textual in its UI thread without installing process signals.

        Textual's Linux driver installs terminal signal handlers when it
        starts. Python only permits signal handlers to be installed by the
        main thread, while the synchronous pybadge API needs the UI to run
        alongside the user's program. Skip signal registration requested by
        the UI thread; signal calls from the main thread keep normal behavior.
        """
        original_signal = signal.signal
        simulator_thread = threading.current_thread()

        def thread_aware_signal(signal_number, handler):
            if threading.current_thread() is simulator_thread:
                return signal.SIG_DFL
            return original_signal(signal_number, handler)

        signal.signal = thread_aware_signal
        try:
            self._app.run()
        except BaseException as error:
            self._app_error = error
        finally:
            signal.signal = original_signal
            self._app_stopped.set()

    def shutdown(self):
        app = self._app
        app_thread = self._app_thread
        if app is not None:
            try:
                if (
                    app_thread is not None
                    and app_thread.is_alive()
                    and threading.current_thread() is not app_thread
                    and getattr(app, "is_running", False)
                ):
                    app.call_from_thread(app.exit)
                else:
                    app.exit()
            except Exception:
                pass
        if (
            app_thread is not None
            and app_thread.is_alive()
            and threading.current_thread() is not app_thread
        ):
            app_thread.join(timeout=2.0)
        self._app = None
        self._app_thread = None
        if self._atexit_registered:
            atexit.unregister(self.shutdown)
            self._atexit_registered = False
        super().shutdown()
        self._tone_deadline = None

    def _screen_text(self):
        from rich.text import Text

        screen = Text()
        if self.display_operations:
            for operation in self.display_operations[-5:]:
                if operation[0] == "clear":
                    screen.append(
                        "[clear {}]\n".format(operation[1]),
                        style=_color_style(operation[1]),
                    )
                elif operation[0] == "text":
                    _kind, text, x, y, color = operation
                    screen.append(
                        "{:>3},{:<3} {}\n".format(x, y, text),
                        style=_color_style(color),
                    )
                elif operation[0] == "pixel":
                    _kind, x, y, color = operation
                    screen.append(
                        "pixel {},{}\n".format(x, y), style=_color_style(color)
                    )
                elif operation[0] == "line":
                    _kind, x1, y1, x2, y2, color = operation
                    screen.append(
                        "line {},{} to {},{}\n".format(x1, y1, x2, y2),
                        style=_color_style(color),
                    )
                elif operation[0] == "rectangle":
                    _kind, x, y, width, height, color, filled = operation
                    shape = "filled rectangle" if filled else "rectangle"
                    screen.append(
                        "{} {},{} {}x{}\n".format(shape, x, y, width, height),
                        style=_color_style(color),
                    )
                elif operation[0] == "image":
                    screen.append("[image: {}]\n".format(operation[1]))
        return screen

    def _output_text(self):
        from rich.text import Text

        if (
            self.active_tone is not None
            and self._tone_deadline is not None
            and time.monotonic() >= self._tone_deadline
        ):
            self.active_tone = None
            self._tone_deadline = None

        output = Text("RGB ")
        output.append("●", style="bold {}".format(_color_style(self.rgb_led)))
        output.append(
            " {}   Ring ".format(self.rgb_led),
            style=_color_style(self.rgb_led) if self.rgb_led == "off" else "white",
        )
        for color in self.led_strip:
            output.append("●", style="bold {}".format(_color_style(color)))
        if self.active_tone is None:
            tone = "buzzer off"
        else:
            tone = "buzzer {} Hz".format(self.active_tone[0])
        output.append("   {}".format(tone))
        output.append(
            "\nJoystick: ({:.1f}, {:.1f})".format(*self.joystick_values)
        )
        return output

    def joystick(self):
        return self.joystick_values

    def play_tone(self, frequency_hz, duration_ms):
        super().play_tone(frequency_hz, duration_ms)
        self._tone_deadline = time.monotonic() + duration_ms / 1000.0

    def stop_tone(self):
        super().stop_tone()
        self._tone_deadline = None

    def pause(self, milliseconds):
        time.sleep(milliseconds / 1000.0)

    def display_clear(self, color):
        super().display_clear(color)
        self.display_operations = [("clear", color)]

    def display_text(self, text, x, y, color):
        super().display_text(text, x, y, color)
        self._trim_display_history()

    def draw_pixel(self, x, y, color):
        super().draw_pixel(x, y, color)
        self._trim_display_history()

    def draw_line(self, x1, y1, x2, y2, color):
        super().draw_line(x1, y1, x2, y2, color)
        self._trim_display_history()

    def draw_rectangle(self, x, y, width, height, color, filled):
        super().draw_rectangle(x, y, width, height, color, filled)
        self._trim_display_history()

    def display_image(self, path, x, y):
        super().display_image(path, x, y)
        self._trim_display_history()

    def _trim_display_history(self):
        if len(self.display_operations) > 20:
            self.display_operations = self.display_operations[-20:]

    def scan_wifi(self, include_details=False):
        raise UnsupportedFeatureError(
            "Wi-Fi scanning is not modeled by the terminal simulator."
        )

    def is_wifi_connected(self):
        raise UnsupportedFeatureError(
            "Wi-Fi connections are not modeled by the terminal simulator."
        )

    def wifi_info(self):
        raise UnsupportedFeatureError(
            "Wi-Fi connections are not modeled by the terminal simulator."
        )

    def connect_wifi(self, ssid, password, timeout_ms):
        raise UnsupportedFeatureError(
            "Wi-Fi connections are not modeled by the terminal simulator."
        )

    def disconnect_wifi(self):
        raise UnsupportedFeatureError(
            "Wi-Fi connections are not modeled by the terminal simulator."
        )

    def download_url(self, url, filename, headers):
        raise UnsupportedFeatureError(
            "HTTP requests are not modeled by the terminal simulator."
        )

    def post_url(self, url, data, json, headers):
        raise UnsupportedFeatureError(
            "HTTP requests are not modeled by the terminal simulator."
        )

    def read_accelerometer(self):
        raise UnsupportedFeatureError(
            "Accelerometer readings are not modeled by the terminal simulator."
        )

    def read_battery_voltage(self):
        raise UnsupportedFeatureError(
            "Battery voltage is not modeled by the terminal simulator."
        )

    def read_voltage(self, pin):
        raise UnsupportedFeatureError(
            "External analog voltage is not modeled by the terminal simulator."
        )

    def set_pwm(self, pin, frequency_hz, duty_percent):
        raise UnsupportedFeatureError(
            "External GPIO PWM is not modeled by the terminal simulator."
        )

    def configure_pin(self, pin, mode, pull):
        raise UnsupportedFeatureError(
            "External GPIO configuration is not modeled by the terminal simulator."
        )

    def read_pin(self, pin):
        raise UnsupportedFeatureError(
            "External GPIO reads are not modeled by the terminal simulator."
        )

    def write_pin(self, pin, value):
        raise UnsupportedFeatureError(
            "External GPIO writes are not modeled by the terminal simulator."
        )

    def stop_pwm(self, pin):
        raise UnsupportedFeatureError(
            "External GPIO PWM is not modeled by the terminal simulator."
        )


def _color_style(color):
    if isinstance(color, (tuple, list)):
        red, green, blue = color
        return "#%02x%02x%02x" % (red, green, blue)
    colors = {
        "off": "#808080",
        "black": "#000000",
        "white": "#ffffff",
        "red": "#ff0000",
        "green": "#00ff00",
        "blue": "#0000ff",
        "yellow": "#ffff00",
        "orange": "#ff8000",
        "magenta": "#ff00ff",
        "cyan": "#00ffff",
        "purple": "#800080",
    }
    return colors.get(color, "#ffffff")
