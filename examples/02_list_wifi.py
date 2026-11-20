"""Scan for nearby Wi-Fi networks and show their names and signal strength.

Run from the repository root after `byui_ebadge.py` is implemented. A scan may take
several seconds. The badge does not need to connect to any listed network.
"""

import byui_ebadge


def main():
    byui_ebadge.initialize()
    unavailable_message = None
    try:
        byui_ebadge.display_clear()
        byui_ebadge.display_text("Scanning for Wi-Fi...", x=8, y=8)

        networks = byui_ebadge.scan_wifi()
        byui_ebadge.display_clear()
        byui_ebadge.display_text("Nearby Wi-Fi networks", x=8, y=8)

        if not networks:
            byui_ebadge.display_text("No networks found", x=8, y=32)
            print("No Wi-Fi networks found.")
            return

        for index, (name, signal_dbm) in enumerate(networks[:9]):
            line = "{} ({:+} dBm)".format(name or "(hidden)", signal_dbm)
            byui_ebadge.display_text(line, x=8, y=32 + index * 20)
            print(line)

        if len(networks) > 9:
            byui_ebadge.display_text("+{} more".format(len(networks) - 9), x=8, y=212)
    except byui_ebadge.UnsupportedFeatureError as error:
        unavailable_message = "Wi-Fi scan unavailable: {}".format(error)
        byui_ebadge.display_clear()
        byui_ebadge.display_text("Wi-Fi scan unavailable", x=8, y=8)
    finally:
        byui_ebadge.shutdown()

    if unavailable_message is not None:
        print(unavailable_message)


if __name__ == "__main__":
    main()
