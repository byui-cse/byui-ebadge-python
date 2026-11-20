"""Collect raw joystick ADC readings on a physical V4.1.1 eBadge.

Run from the MicroPython REPL after deploying this file as an asset. The
reported samples are diagnostic only; hardware ``joystick()`` remains
disabled until the readings have been reviewed and a mapping is implemented.
"""


_SAMPLE_COUNT = 32


def _average(adc):
    """Return the average raw ADC count from a short steady sample."""
    total = 0
    minimum = 65535
    maximum = 0
    for _ in range(_SAMPLE_COUNT):
        value = adc.read()
        total += value
        minimum = min(minimum, value)
        maximum = max(maximum, value)
    return total // _SAMPLE_COUNT, minimum, maximum


def main():
    """Prompt for center and four directions and print raw axis readings."""
    import machine

    x_adc = machine.ADC(machine.Pin(8))
    y_adc = machine.ADC(machine.Pin(9))
    attenuation = machine.ADC.ATTN_11DB
    x_adc.atten(attenuation)
    y_adc.atten(attenuation)
    try:
        readings = []
        for position in ("center", "left", "right", "up", "down"):
            input(
                "Place joystick at {} and hold steady; press Enter to sample. ".format(
                    position
                )
            )
            x_value = _average(x_adc)
            y_value = _average(y_adc)
            reading = (position, x_value, y_value)
            readings.append(reading)
            print(
                "{}: GPIO8/X avg={} range={}..{}; GPIO9/Y avg={} range={}..{}".format(
                    position,
                    x_value[0],
                    x_value[1],
                    x_value[2],
                    y_value[0],
                    y_value[1],
                    y_value[2],
                )
            )
        return readings
    finally:
        for adc in (x_adc, y_adc):
            deinit = getattr(adc, "deinit", None)
            if deinit is not None:
                deinit()


if __name__ == "__main__":
    main()
