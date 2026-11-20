#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ASSETS_DIR="$ROOT_DIR/assets"
FIRMWARE_NAME="ESP32_GENERIC_S3-20260824-v1.29.0.bin"
FIRMWARE_URL="https://micropython.org/resources/firmware/$FIRMWARE_NAME"
FIRMWARE_PATH="$ASSETS_DIR/$FIRMWARE_NAME"
IMAGE_PATH="$ASSETS_DIR/lego-python_badge.bmp"

cd "$ROOT_DIR"
mkdir -p "$ASSETS_DIR"

if command -v python3 >/dev/null 2>&1; then
    PYTHON="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON="python"
else
    echo "Error: Python 3 is required. Install it and retry." >&2
    exit 1
fi

if [[ ! -f "$ROOT_DIR/deploy.py" ]]; then
    echo "Error: deploy.py is missing from $ROOT_DIR." >&2
    exit 1
fi

if [[ ! -s "$IMAGE_PATH" ]]; then
    echo "Error: prepared logo not found at $IMAGE_PATH." >&2
    echo "Run: $PYTHON resize_image.py assets/lego-python.png" >&2
    exit 1
fi

if ! "$PYTHON" -c 'import esptool, mpremote' >/dev/null 2>&1; then
    echo "Error: esptool and mpremote are required for setup." >&2
    echo "Install them with: $PYTHON -m pip install esptool mpremote" >&2
    exit 1
fi

if [[ -s "$FIRMWARE_PATH" ]]; then
    echo "Using existing firmware: $FIRMWARE_PATH"
else
    DOWNLOAD_TMP="$FIRMWARE_PATH.part"
    trap 'rm -f "$DOWNLOAD_TMP"' EXIT

    echo "Downloading MicroPython firmware to $FIRMWARE_PATH"
    if command -v curl >/dev/null 2>&1; then
        curl --fail --location --retry 3 --output "$DOWNLOAD_TMP" "$FIRMWARE_URL"
    elif command -v wget >/dev/null 2>&1; then
        wget --output-document="$DOWNLOAD_TMP" "$FIRMWARE_URL"
    else
        echo "Error: install curl or wget to download the firmware." >&2
        exit 1
    fi

    mv "$DOWNLOAD_TMP" "$FIRMWARE_PATH"
    trap - EXIT
fi

echo "Erasing flash and installing MicroPython (esptool will detect the port)."
"$PYTHON" -m esptool erase-flash
"$PYTHON" -m esptool --baud 460800 write-flash 0 "$FIRMWARE_PATH"

echo "Deploying the eBadge library, prepared Python logo, and example 04."
echo "Running: $PYTHON deploy.py --install-library --asset $IMAGE_PATH examples/04_display_logo.py"
echo "Waiting for the firmware's first-boot filesystem setup to finish."
sleep 3

DEPLOYED=0
for attempt in 1 2 3; do
    echo "Deploy attempt $attempt/3."
    if "$PYTHON" deploy.py --install-library --asset "$IMAGE_PATH" examples/04_display_logo.py; then
        DEPLOYED=1
        break
    fi
    if [[ "$attempt" -lt 3 ]]; then
        echo "Deployment did not connect (attempt $attempt/3); retrying in 3 seconds."
        sleep 3
    fi
done

if [[ "$DEPLOYED" -ne 1 ]]; then
    echo "Error: deployment failed after 3 attempts." >&2
    exit 1
fi

echo "Setup complete. Power-cycle the badge or press its reset button to run the logo example."
