from gpiozero import (
    Device,
    Motor,
    DigitalOutputDevice,
    MCP3008
)

from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

Device.pin_factory = PiGPIOFactory()

# -------------------------
# Hardware
# -------------------------

slp = DigitalOutputDevice(7)

motor_a = Motor(
    forward=12,
    backward=18
)

motor_b = Motor(
    forward=13,
    backward=19
)

adc = MCP3008(channel=0)

# -------------------------
# Sensor calibration
# -------------------------

VREF = 3.3

# From earlier calibration:
# 20 cm = 2.287 V
STOP_VOLTAGE = 2.287

# -------------------------
# Motor settings
# -------------------------

SPEED_A = 0.15
SPEED_B = 0.14


# Sensor update rate
INTERVAL = 0.05

slp.on()

stopped = False

print("Collision avoidance started")
print("20 cm threshold = 2.287 V")

try:

    while True:

        voltage = adc.value * VREF

        # --------------------------------
        # Fail-safe stop
        # --------------------------------

        if voltage >= STOP_VOLTAGE:

            motor_a.stop()
            motor_b.stop()

            stopped = True

            print(
                f"{voltage:.3f} V -> "
                f"OBSTACLE -> STOP"
            )

        elif stopped:

            # Keep rover stopped once an
            # unsafe distance was detected.
            #
            # This is safer because the IR
            # sensor becomes unreliable below
            # approximately 20 cm.

            motor_a.stop()
            motor_b.stop()

            print(
                f"{voltage:.3f} V -> "
                f"STOPPED (fail-safe)"
            )

        else:

            motor_a.forward(SPEED_A)
            motor_b.forward(SPEED_B)

            print(
                f"{voltage:.3f} V -> FORWARD"
            )

        sleep(INTERVAL)

except KeyboardInterrupt:

    print("\nStopping rover")

finally:

    motor_a.stop()
    motor_b.stop()

    slp.off()
    adc.close()
