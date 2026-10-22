from gpiozero import Device, Motor, DigitalOutputDevice
from gpiozero.pins.pigpio import PiGPIOFactory

import board
import adafruit_tcs34725
from time import sleep


# --------------------------------
# GPIO setup
# --------------------------------

Device.pin_factory = PiGPIOFactory()

slp = DigitalOutputDevice(7)

motor_a = Motor(
    forward=12,
    backward=18
)

motor_b = Motor(
    forward=13,
    backward=19
)


# --------------------------------
# RGB sensor
# --------------------------------

i2c = board.I2C()

sensor = adafruit_tcs34725.TCS34725(i2c)

sensor.integration_time = 50
sensor.gain = 4


# --------------------------------
# Settings
# --------------------------------

# Slow forward movement
FORWARD_A = 0.20
FORWARD_B = 0.19

# Search / turning power
SEARCH_POWER = 0.22

# Backwards power
BACK_POWER = 0.20

# Black / white threshold
CLEAR_THRESHOLD = 2900

# Movement times
FORWARD_TIME = 0.08

TURN_SMALL = 0.025
TURN_BIG = 0.045

BACK_TIME = 0.025

PAUSE_TIME = 0.04



# --------------------------------
# Helper functions
# --------------------------------

def read_clear():
    r, g, b, clear = sensor.color_raw
    return r, g, b, clear


def stop_motors():
    motor_a.stop()
    motor_b.stop()


def check_line():

    r, g, b, clear = read_clear()

    print(
        f"R={r} "
        f"G={g} "
        f"B={b} "
        f"Clear={clear}"
    )

    return clear < CLEAR_THRESHOLD


# --------------------------------
# Start
# --------------------------------

slp.on()

print("Line following started")


try:

    while True:

        r, g, b, clear = read_clear()

        print(
            f"R={r} "
            f"G={g} "
            f"B={b} "
            f"Clear={clear}"
        )


        # ==================================
        # BLACK -> FORWARD
        # ==================================

        if clear < CLEAR_THRESHOLD:

            print("BLACK -> SLOW FORWARD")

            motor_a.forward(FORWARD_A)
            motor_b.forward(FORWARD_B)

            sleep(FORWARD_TIME)

            stop_motors()

            sleep(PAUSE_TIME)


        # ==================================
        # WHITE -> SEARCH
        # ==================================

        else:

            print("WHITE -> SEARCH")

            line_found = False


            # --------------------------------
            # 1. SMALL TURN ONE DIRECTION
            #
            # Motor A backward
            # Motor B forward
            # --------------------------------

            print("SEARCH 1")

            motor_a.backward(SEARCH_POWER)
            motor_b.forward(SEARCH_POWER)

            sleep(TURN_SMALL)

            stop_motors()
            sleep(PAUSE_TIME)


            if check_line():

                print("BLACK FOUND")
                line_found = True



            # --------------------------------
            # 2. SMALL TURN OTHER DIRECTION
            #
            # Motor A forward
            # Motor B backward
            #
            # Longer because we first need
            # to pass the starting position.
            # --------------------------------

            if not line_found:

                print("SEARCH 2")

                motor_a.forward(SEARCH_POWER)
                motor_b.backward(SEARCH_POWER)

                sleep(TURN_SMALL * 2)

                stop_motors()
                sleep(PAUSE_TIME)


                if check_line():

                    print("BLACK FOUND")
                    line_found = True


            # --------------------------------
            # 3. BIGGER TURN FIRST DIRECTION
            # --------------------------------

            if not line_found:

                print("SEARCH 3 - WIDER")

                motor_a.backward(SEARCH_POWER)
                motor_b.forward(SEARCH_POWER)

                sleep(TURN_BIG * 2)

                stop_motors()
                sleep(PAUSE_TIME)


                if check_line():

                    print("BLACK FOUND")
                    line_found = True


            # --------------------------------
            # 4. BIGGER TURN OTHER DIRECTION
            # --------------------------------

            if not line_found:

                print("SEARCH 4 - WIDER")

                motor_a.forward(SEARCH_POWER)
                motor_b.backward(SEARCH_POWER)

                sleep(TURN_BIG * 2)

                stop_motors()
                sleep(PAUSE_TIME)


                if check_line():

                    print("BLACK FOUND")
                    line_found = True


            # --------------------------------
            # LINE STILL NOT FOUND -> BACK
            # --------------------------------

            if not line_found:

                print("LINE NOT FOUND -> SMALL BACK")

                motor_a.backward(BACK_POWER)
                motor_b.backward(BACK_POWER)

                sleep(BACK_TIME)

                stop_motors()

                sleep(PAUSE_TIME)


except KeyboardInterrupt:

    print("\nStopping rover")


finally:

    stop_motors()
    slp.off()
