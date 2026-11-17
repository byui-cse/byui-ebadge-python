"""Host-side checks for the hardware backend's Wi-Fi and HTTP logic."""

import sys
from types import SimpleNamespace

import pytest

from backends.hardware_backend import HardwareBackend


class FakeClock:
    def __init__(self):
        self.now = 0

    def ticks_ms(self):
        return self.now

    def ticks_diff(self, newer, older):
        return newer - older

    def sleep_ms(self, milliseconds):
        self.now += milliseconds


class FakeWlan:
    def __init__(self, connected=False, connect_succeeds=True):
        self.connected = connected
        self.connect_succeeds = connect_succeeds
        self.is_active = connected
        self.connect_calls = []
        self.disconnect_calls = 0

    def active(self, value=None):
        if value is not None:
            self.is_active = value
        return self.is_active

    def isconnected(self):
        return self.connected

    def connect(self, ssid, password):
        self.connect_calls.append((ssid, password))
        self.connected = self.connect_succeeds

    def disconnect(self):
        self.disconnect_calls += 1
        self.connected = False


class FakeResponse:
    def __init__(self, content=b"response", status_code=200):
        self.content = content
        self.status_code = status_code
        self.closed = False

    def close(self):
        self.closed = True


def _install_wlan(monkeypatch, wlan):
    network = SimpleNamespace(STA_IF=0, WLAN=lambda _interface: wlan)
    monkeypatch.setitem(sys.modules, "network", network)


def test_connect_wifi_skips_reconnect_when_already_connected(monkeypatch):
    wlan = FakeWlan(connected=True)
    _install_wlan(monkeypatch, wlan)
    backend = HardwareBackend()
    backend._utime = FakeClock()

    assert backend.connect_wifi("net", "secret", 500) is True
    assert wlan.connect_calls == []


def test_connect_wifi_returns_false_after_timeout(monkeypatch):
    wlan = FakeWlan(connect_succeeds=False)
    _install_wlan(monkeypatch, wlan)
    backend = HardwareBackend()
    backend._utime = FakeClock()

    assert backend.connect_wifi("net", "secret", 150) is False
    assert backend._utime.now >= 150


def test_disconnect_wifi_is_safe_when_already_disconnected(monkeypatch):
    wlan = FakeWlan()
    _install_wlan(monkeypatch, wlan)
    backend = HardwareBackend()

    backend.disconnect_wifi()
    assert wlan.disconnect_calls == 0
    assert wlan.is_active is False


def test_http_request_checks_wifi_before_loading_request_module(monkeypatch):
    wlan = FakeWlan()
    _install_wlan(monkeypatch, wlan)
    backend = HardwareBackend()

    with pytest.raises(RuntimeError, match="connect to Wi-Fi"):
        backend.download_url("https://example.com", None, None)


def test_download_url_closes_response_and_returns_content(monkeypatch):
    wlan = FakeWlan(connected=True)
    response = FakeResponse(b"downloaded")
    requests = SimpleNamespace(get=lambda url, headers: response)
    _install_wlan(monkeypatch, wlan)
    monkeypatch.setitem(sys.modules, "urequests", requests)
    backend = HardwareBackend()

    assert backend.download_url("https://example.com", None, None) == b"downloaded"
    assert response.closed is True


def test_download_url_closes_response_when_server_returns_error(monkeypatch):
    wlan = FakeWlan(connected=True)
    response = FakeResponse(status_code=503)
    requests = SimpleNamespace(get=lambda url, headers: response)
    _install_wlan(monkeypatch, wlan)
    monkeypatch.setitem(sys.modules, "urequests", requests)
    backend = HardwareBackend()

    with pytest.raises(OSError, match="status 503"):
        backend.download_url("https://example.com", None, None)
    assert response.closed is True


def test_post_url_json_sets_content_type_and_closes_response(monkeypatch):
    wlan = FakeWlan(connected=True)
    response = FakeResponse(b"accepted")
    calls = []

    def post(url, data, headers):
        calls.append((url, data, headers))
        return response

    requests = SimpleNamespace(post=post)
    _install_wlan(monkeypatch, wlan)
    monkeypatch.setitem(sys.modules, "urequests", requests)
    backend = HardwareBackend()

    result = backend.post_url(
        "https://example.com", None, {"ok": True}, {"X-Trace": "abc"}
    )

    assert result == b"accepted"
    assert calls == [
        (
            "https://example.com",
            '{"ok": true}',
            {"X-Trace": "abc", "Content-Type": "application/json"},
        )
    ]
    assert response.closed is True
