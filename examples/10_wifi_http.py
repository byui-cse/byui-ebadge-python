"""On the badge, connect to Wi-Fi, download a file, and send a JSON request.

Before running on the badge, replace the Wi-Fi credentials and URLs below
with your network details and HTTP endpoints. The GET URL should return a file;
the POST URL should accept JSON. The badge needs ``urequests`` or ``requests``.
"""

import pybadge


WIFI_SSID = "your-wifi-name"
WIFI_PASSWORD = "your-wifi-password"
DOWNLOAD_URL = "https://example.com/file.bin"
POST_URL = "https://example.com/api"
DOWNLOAD_PATH = "download.bin"


def main():
    pybadge.initialize(mode="hardware")
    try:
        print("Connecting to Wi-Fi...")
        if not pybadge.connect_wifi(WIFI_SSID, WIFI_PASSWORD):
            print("Could not connect to Wi-Fi.")
            return

        print("Connected. Downloading {}...".format(DOWNLOAD_URL))
        saved_path = pybadge.download_url(DOWNLOAD_URL, filename=DOWNLOAD_PATH)
        print("Saved download to {}.".format(saved_path))

        print("Sending JSON to {}...".format(POST_URL))
        response = pybadge.post_url(
            POST_URL,
            json={"message": "Hello from the eBadge"},
        )
        print("POST response: {}".format(response))
    except (OSError, RuntimeError) as error:
        print("Wi-Fi or HTTP request failed: {}".format(error))
    finally:
        pybadge.disconnect_wifi()
        pybadge.shutdown()


if __name__ == "__main__":
    main()
