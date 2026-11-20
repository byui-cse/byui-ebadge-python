"""Choose a Wi-Fi network on the badge and display its connection details.

Run on a physical eBadge. Use the screen prompts to select a network and enter
its password. After connecting, press B to disconnect and exit.
"""

import pybadge


def main():
    pybadge.initialize(mode="hardware")
    try:
        if pybadge.connect_wifi_with_screen():
            print(pybadge.wifi_info())
            print("Press B to disconnect and exit.")
            while not pybadge.is_pressed(pybadge.BUTTON_B):
                pybadge.pause(50)
    finally:
        pybadge.disconnect_wifi()
        pybadge.shutdown()


if __name__ == "__main__":
    main()
