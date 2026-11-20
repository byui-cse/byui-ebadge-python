"""Choose a Wi-Fi network on the badge and display its connection details.

Run on a physical eBadge. Use the screen prompts to select a network and enter
its password. After connecting, press B to disconnect and exit.
"""

import byui_ebadge


def main():
    byui_ebadge.initialize(mode="hardware")
    try:
        if byui_ebadge.connect_wifi_with_screen():
            print(byui_ebadge.wifi_info())
            print("Press B to disconnect and exit.")
            while not byui_ebadge.is_pressed(byui_ebadge.BUTTON_B):
                byui_ebadge.pause(50)
    finally:
        byui_ebadge.disconnect_wifi()
        byui_ebadge.shutdown()


if __name__ == "__main__":
    main()
